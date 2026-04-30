"""
Configuration A — Cloud-Only Baseline Measurement
Device publishes ALL sensor readings directly to AWS IoT Core.
Measures: round-trip PUBACK latency, total cloud-bound bandwidth.

Usage (on EC2 Greengrass instance):
    python3 config_a_measurement.py
"""

import json
import random
import time
import numpy as np
import boto3
from awsiot import mqtt_connection_builder, mqtt

# ── AWS IoT Core endpoint (filled by deploy script) ──────────────────────────
IOT_ENDPOINT = 'a1h6vr5m0pm8qb-ats.iot.us-east-1.amazonaws.com'
REGION       = 'us-east-1'

# ── Certificates (Greengrass device certs — already present on EC2) ──────────
CERT_PATH = '/greengrass/v2/thingCert.crt'
KEY_PATH  = '/greengrass/v2/privKey.key'
CA_PATH   = '/greengrass/v2/rootCA.pem'

CLIENT_ID  = 'TestDevice-ConfigA-Machine01'
TOPIC      = 'iiot/edge/machine-01/telemetry'
N_READINGS = 200
HZ         = 5        # publish rate
MACHINE_ID = 'machine-01'

# Baseline sensor means (CMAPSS FD001 normal operating range)
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
    """Generate a sensor reading; inject anomaly ~10% of the time."""
    mult = 1.15 if anomaly else 1.0
    payload = {
        'machine_id': MACHINE_ID,
        'reading_id': i,
        'timestamp':  time.time(),
        'config':     'A',
    }
    for s, (mean, std) in SENSOR_PARAMS.items():
        payload[s] = round(random.gauss(mean * mult, std), 4)
    return payload


def run():
    print('=' * 55)
    print(' Configuration A — Cloud-Only Baseline')
    print(f' Endpoint : {IOT_ENDPOINT}')
    print(f' Readings : {N_READINGS} @ {HZ} Hz')
    print('=' * 55)

    conn = mqtt_connection_builder.mtls_from_path(
        endpoint=IOT_ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=KEY_PATH,
        ca_filepath=CA_PATH,
        client_id=CLIENT_ID,
    )
    conn.connect().result()
    print(f'Connected to IoT Core.\n')

    latencies  = []
    bytes_sent = 0

    for i in range(N_READINGS):
        is_anomaly = (random.random() < 0.10)      # ~10% anomaly rate
        payload    = make_reading(i, anomaly=is_anomaly)
        raw        = json.dumps(payload).encode()
        bytes_sent += len(raw)

        t0 = time.perf_counter()
        future, _ = conn.publish(topic=TOPIC, payload=raw, qos=mqtt.QoS.AT_LEAST_ONCE)
        future.result()                             # wait for PUBACK
        ms = (time.perf_counter() - t0) * 1000
        latencies.append(ms)

        if (i + 1) % 40 == 0:
            print(f'  [{i+1:>3}/{N_READINGS}] last latency: {ms:.1f} ms')

        time.sleep(1.0 / HZ)

    conn.disconnect().result()

    # ── Results ───────────────────────────────────────────────────────────────
    results = {
        'config':            'A',
        'n_readings':        N_READINGS,
        'bytes_sent_total':  bytes_sent,
        'bytes_per_reading': bytes_sent / N_READINGS,
        'latency_mean_ms':   float(np.mean(latencies)),
        'latency_median_ms': float(np.median(latencies)),
        'latency_p95_ms':    float(np.percentile(latencies, 95)),
        'latency_p99_ms':    float(np.percentile(latencies, 99)),
        'latency_min_ms':    float(np.min(latencies)),
        'latency_max_ms':    float(np.max(latencies)),
    }

    print('\n' + '=' * 55)
    print(' CONFIGURATION A RESULTS')
    print('=' * 55)
    print(f'  Readings sent to cloud : {N_READINGS} (100%)')
    print(f'  Total bytes to cloud   : {bytes_sent:,} bytes ({bytes_sent/1024:.1f} KB)')
    print(f'  Avg bytes / reading    : {bytes_sent/N_READINGS:.0f} bytes')
    print(f'  Latency mean           : {results["latency_mean_ms"]:.1f} ms')
    print(f'  Latency median         : {results["latency_median_ms"]:.1f} ms')
    print(f'  Latency P95            : {results["latency_p95_ms"]:.1f} ms')
    print('=' * 55)

    out_path = '/tmp/config_a_results.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nResults saved → {out_path}')
    return results


if __name__ == '__main__':
    run()
