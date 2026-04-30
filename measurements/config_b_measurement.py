"""
Configuration B — Hybrid Edge Measurement
Edge ML inference runs locally (ONNX); only anomaly alerts forwarded to IoT Core.
Normal readings batched and compressed before cloud upload.

Measures: local inference latency, cloud-bound bandwidth reduction vs Config A.

Usage (on EC2 Greengrass instance — same machine as edge):
    python3 config_b_measurement.py --model /path/to/pdm_model.onnx --scaler /path/to/scaler.pkl
"""

import argparse
import json
import os
import pickle
import random
import time
import numpy as np
import onnxruntime as ort
import boto3
from awsiot import mqtt_connection_builder, mqtt

IOT_ENDPOINT = 'a1h6vr5m0pm8qb-ats.iot.us-east-1.amazonaws.com'
REGION       = 'us-east-1'
CERT_PATH    = '/greengrass/v2/thingCert.crt'
KEY_PATH     = '/greengrass/v2/privKey.key'
CA_PATH      = '/greengrass/v2/rootCA.pem'

CLIENT_ID    = 'TestDevice-ConfigB-Machine01'
ALERT_TOPIC  = 'iiot/edge/machine-01/alerts'
BATCH_TOPIC  = 'iiot/edge/machine-01/batch'
N_READINGS   = 200
BATCH_SIZE   = 10

FEATURE_SENSORS = [
    's2', 's3', 's4', 's7', 's8', 's9',
    's11', 's12', 's13', 's14', 's15', 's17', 's20', 's21'
]

SENSOR_PARAMS = {
    's2':  (642.15, 0.50),  's3':  (1589.70, 5.00),
    's4':  (1400.60, 5.00), 's7':  (554.36,  1.00),
    's8':  (2388.02, 5.00), 's9':  (9065.00, 20.00),
    's11': (47.47,   0.50), 's12': (521.66,  2.00),
    's13': (2388.00, 5.00), 's14': (8138.00, 20.00),
    's15': (8.4195,  0.05), 's17': (392.00,  1.00),
    's20': (38.86,   0.50), 's21': (23.37,   0.50),
}


def make_reading(i, anomaly=False):
    mult = 1.15 if anomaly else 1.0
    payload = {
        'machine_id': 'machine-01',
        'reading_id': i,
        'timestamp':  time.time(),
        'config':     'B',
    }
    for s, (mean, std) in SENSOR_PARAMS.items():
        payload[s] = round(random.gauss(mean * mult, std), 4)
    return payload


def run(model_path, scaler_path):
    print('=' * 55)
    print(' Configuration B — Hybrid Edge')
    print(f' Model   : {model_path}')
    print(f' Readings: {N_READINGS} total')
    print('=' * 55)

    # ── Load model ────────────────────────────────────────────────────────────
    session    = ort.InferenceSession(model_path)
    input_name = session.get_inputs()[0].name
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    print('ONNX model loaded.\n')

    # ── Connect to IoT Core (for forwarding anomalies only) ───────────────────
    conn = mqtt_connection_builder.mtls_from_path(
        endpoint=IOT_ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=KEY_PATH,
        ca_filepath=CA_PATH,
        client_id=CLIENT_ID,
    )
    conn.connect().result()
    print('Connected to IoT Core (anomaly forward channel only).\n')

    inf_latencies   = []
    cloud_latencies = []
    n_anomalies     = 0
    bytes_to_cloud  = 0
    normal_batch    = []

    for i in range(N_READINGS):
        is_anomaly = (random.random() < 0.10)
        payload    = make_reading(i, anomaly=is_anomaly)

        # ── Local edge inference ───────────────────────────────────────────
        features = np.array(
            [[payload.get(s, 0.0) for s in FEATURE_SENSORS]], dtype=np.float32
        )
        scaled = scaler.transform(features).astype(np.float32)
        t0 = time.perf_counter()
        out = session.run(None, {input_name: scaled})
        inf_ms = (time.perf_counter() - t0) * 1000
        inf_latencies.append(inf_ms)
        predicted_anomaly = int(out[0][0])

        if predicted_anomaly == 1:
            # ── Forward alert to cloud immediately ────────────────────────
            alert = {
                'machine_id':           'machine-01',
                'timestamp':            payload['timestamp'],
                'anomaly':              True,
                'inference_latency_ms': round(inf_ms, 2),
                'reading_id':           i,
                'config':               'B',
                's9':  payload['s9'],
                's12': payload['s12'],
            }
            raw = json.dumps(alert).encode()
            bytes_to_cloud += len(raw)
            t_cloud = time.perf_counter()
            future, _ = conn.publish(topic=ALERT_TOPIC, payload=raw, qos=mqtt.QoS.AT_LEAST_ONCE)
            future.result()
            cloud_ms = (time.perf_counter() - t_cloud) * 1000
            cloud_latencies.append(cloud_ms)
            n_anomalies += 1
            print(f'  ANOMALY [{i+1:>3}] inf={inf_ms:.1f}ms cloud={cloud_ms:.1f}ms')
        else:
            normal_batch.append(payload)
            if len(normal_batch) >= BATCH_SIZE:
                # ── Flush compressed batch to cloud ───────────────────────
                summary = {
                    'machine_id': 'machine-01',
                    'timestamp':  time.time(),
                    'batch_size': len(normal_batch),
                    'config':     'B',
                    'avg_inference_ms': round(float(np.mean(inf_latencies[-BATCH_SIZE:])), 2),
                    # Send only mean sensor values — compression
                    'sensor_means': {
                        s: round(float(np.mean([r.get(s, 0) for r in normal_batch])), 4)
                        for s in FEATURE_SENSORS
                    }
                }
                raw = json.dumps(summary).encode()
                bytes_to_cloud += len(raw)
                conn.publish(topic=BATCH_TOPIC, payload=raw, qos=mqtt.QoS.AT_LEAST_ONCE)
                print(f'  Batch  [{i+1:>3}] flushed {len(normal_batch)} normal readings → {len(raw)} bytes')
                normal_batch = []

    # Flush remaining batch
    if normal_batch:
        summary = {
            'machine_id': 'machine-01', 'timestamp': time.time(),
            'batch_size': len(normal_batch), 'config': 'B', 'final_batch': True,
            'sensor_means': {
                s: round(float(np.mean([r.get(s, 0) for r in normal_batch])), 4)
                for s in FEATURE_SENSORS
            }
        }
        raw = json.dumps(summary).encode()
        bytes_to_cloud += len(raw)
        conn.publish(topic=BATCH_TOPIC, payload=raw, qos=mqtt.QoS.AT_LEAST_ONCE)

    conn.disconnect().result()

    # ── Config A reference values (200 readings × ~280 bytes each) ───────────
    config_a_bytes   = N_READINGS * 280
    bandwidth_saving = (1 - bytes_to_cloud / config_a_bytes) * 100

    results = {
        'config':              'B',
        'n_readings':          N_READINGS,
        'n_anomalies':         n_anomalies,
        'n_normal_cloud':      int(np.ceil(N_READINGS / BATCH_SIZE)),
        'bytes_to_cloud':      bytes_to_cloud,
        'bandwidth_saving_pct': round(bandwidth_saving, 1),
        'inf_latency_mean_ms':  float(np.mean(inf_latencies)),
        'inf_latency_median_ms': float(np.median(inf_latencies)),
        'inf_latency_p95_ms':   float(np.percentile(inf_latencies, 95)),
        'inf_latency_max_ms':   float(np.max(inf_latencies)),
        'cloud_latency_mean_ms': float(np.mean(cloud_latencies)) if cloud_latencies else 0,
    }

    print('\n' + '=' * 55)
    print(' CONFIGURATION B RESULTS')
    print('=' * 55)
    print(f'  Total readings processed locally : {N_READINGS}')
    print(f'  Anomalies forwarded to cloud     : {n_anomalies} ({n_anomalies/N_READINGS:.0%})')
    print(f'  Normal batches forwarded         : {results["n_normal_cloud"]}')
    print(f'  Total bytes to cloud             : {bytes_to_cloud:,} bytes ({bytes_to_cloud/1024:.1f} KB)')
    print(f'  Bandwidth saving vs Config A     : {bandwidth_saving:.1f}%')
    print(f'  Local inference latency mean     : {results["inf_latency_mean_ms"]:.2f} ms')
    print(f'  Local inference latency P95      : {results["inf_latency_p95_ms"]:.2f} ms')
    print(f'  Local inference latency max      : {results["inf_latency_max_ms"]:.2f} ms')
    print('=' * 55)

    out_path = '/tmp/config_b_results.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nResults saved → {out_path}')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model',  default='/tmp/ml_artifacts/pdm_model.onnx')
    parser.add_argument('--scaler', default='/tmp/ml_artifacts/scaler.pkl')
    args = parser.parse_args()
    run(args.model, args.scaler)
