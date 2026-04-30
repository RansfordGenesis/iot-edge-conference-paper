"""
IIoT Edge ML Inference — AWS IoT Greengrass v2 Component
Subscribes to local sensor telemetry, runs ONNX inference, routes results.

Normal readings → batched via Stream Manager → S3 (periodic)
Anomaly readings → immediate alert → IoT Core → CloudWatch
"""

import json
import os
import pickle
import time
import traceback
import numpy as np
import onnxruntime as ort
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as ipc_client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    PublishToTopicRequest,
    PublishMessage,
    BinaryMessage,
)

# ── Topics ────────────────────────────────────────────────────────────────────
SUBSCRIBE_TOPIC = 'iiot/edge/#'
ALERT_TOPIC     = 'iiot/edge/{mid}/alerts'
BATCH_TOPIC     = 'iiot/edge/{mid}/batch'

# ── Sensor order must match training ─────────────────────────────────────────
FEATURE_SENSORS = [
    's2', 's3', 's4', 's7', 's8', 's9',
    's11', 's12', 's13', 's14', 's15', 's17', 's20', 's21'
]

BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '10'))

ARTIFACTS = os.environ.get(
    'ARTIFACTS_PATH',
    os.path.dirname(os.path.abspath(__file__))
)


class EdgeInference:
    def __init__(self):
        model_path  = os.path.join(ARTIFACTS, 'pdm_model.onnx')
        scaler_path = os.path.join(ARTIFACTS, 'scaler.pkl')

        print(f'Loading model: {model_path}')
        self.session    = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)

        self.ipc    = awsiot.greengrasscoreipc.connect()
        self.batch  = []          # normal readings buffer
        self.inf_ms = []          # inference latency log
        print('Inference component ready.')

    # ── Inference ─────────────────────────────────────────────────────────────
    def predict(self, payload: dict):
        features = np.array(
            [[payload.get(s, 0.0) for s in FEATURE_SENSORS]],
            dtype=np.float32
        )
        scaled = self.scaler.transform(features).astype(np.float32)
        t0     = time.perf_counter()
        out    = self.session.run(None, {self.input_name: scaled})
        ms     = (time.perf_counter() - t0) * 1000
        label  = int(out[0][0])          # 0 = normal, 1 = anomaly
        self.inf_ms.append(ms)
        return label, ms

    # ── IPC publish ───────────────────────────────────────────────────────────
    def publish(self, topic: str, payload: dict):
        req = PublishToTopicRequest()
        req.topic = topic
        req.publish_message = PublishMessage()
        req.publish_message.binary_message = BinaryMessage()
        req.publish_message.binary_message.message = json.dumps(payload).encode()
        op = self.ipc.new_publish_to_topic()
        op.activate(req)
        op.get_response().result(timeout=5.0)

    # ── Message handler ───────────────────────────────────────────────────────
    def handle(self, topic: str, raw: bytes):
        try:
            payload = json.loads(raw.decode())
            mid     = payload.get('machine_id', 'unknown')
            label, ms = self.predict(payload)

            if label == 1:
                alert = {
                    'machine_id':           mid,
                    'timestamp':            payload.get('timestamp', time.time()),
                    'anomaly':              True,
                    'inference_latency_ms': round(ms, 2),
                    'sensor_snapshot':      {s: payload.get(s) for s in FEATURE_SENSORS},
                }
                self.publish(ALERT_TOPIC.format(mid=mid), alert)
                print(f'ANOMALY | {mid} | {ms:.1f} ms')
            else:
                self.batch.append(payload)
                print(f'Normal  | {mid} | {ms:.1f} ms | batch {len(self.batch)}/{BATCH_SIZE}')
                if len(self.batch) >= BATCH_SIZE:
                    self._flush(mid)

        except Exception:
            print(f'Handler error:\n{traceback.format_exc()}')

    def _flush(self, mid: str):
        summary = {
            'machine_id':              mid,
            'timestamp':               time.time(),
            'batch_size':              len(self.batch),
            'avg_inference_latency_ms': round(float(np.mean(self.inf_ms[-len(self.batch):])), 2),
            'readings':                self.batch,
        }
        self.publish(BATCH_TOPIC.format(mid=mid), summary)
        print(f'Batch flushed: {len(self.batch)} normal readings for {mid}')
        self.batch = []

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        req = SubscribeToTopicRequest()
        req.topic = SUBSCRIBE_TOPIC
        handler  = _StreamHandler(self.handle)
        op = self.ipc.new_subscribe_to_topic(handler)
        op.activate(req)
        print(f'Subscribed to {SUBSCRIBE_TOPIC} — waiting for sensor data...')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            op.close()
            avg = np.mean(self.inf_ms) if self.inf_ms else 0
            print(f'\nShutting down. Avg inference: {avg:.1f} ms over {len(self.inf_ms)} samples.')


class _StreamHandler(ipc_client.SubscribeToTopicStreamHandler):
    def __init__(self, callback):
        super().__init__()
        self._cb = callback

    def on_stream_event(self, event):
        topic   = event.message.topic_name
        payload = event.message.binary_message.message
        self._cb(topic, payload)

    def on_stream_error(self, error):
        print(f'Stream error: {error}')
        return True

    def on_stream_closed(self):
        print('Stream closed.')


if __name__ == '__main__':
    EdgeInference().run()
