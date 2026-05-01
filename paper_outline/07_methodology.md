# Methodology

## III. System Architecture and Design

### A. Architecture Overview

The proposed system implements a two-tier hybrid cloud-edge architecture for IIoT predictive maintenance. At the edge tier, an AWS IoT Greengrass v2 gateway hosts a local ONNX inference runtime alongside a Stream Manager component that governs selective cloud synchronization. At the cloud tier, AWS IoT Core receives only the data the edge determines is worth forwarding — anomaly alerts immediately, and compressed normal-period summaries in batched form. Figure 1 illustrates the full dataflow.

The design separates two logically distinct paths. The **real-time path** is entirely local: a sensor reading arrives, the edge ML model classifies it in sub-millisecond time, and a maintenance decision is produced without any network involvement. The **synchronization path** is asynchronous: normal readings are aggregated into windowed summaries and forwarded to the cloud on a batched schedule, while anomaly alerts bypass batching and are forwarded immediately with full sensor context.

This separation allows the architecture to deliver real-time decision performance regardless of cloud connectivity while still maintaining a cloud-side audit trail and enabling dashboard monitoring.

### B. Edge Gateway Configuration

The edge gateway runs AWS IoT Greengrass Nucleus v2.17.0 on Amazon Linux 2. Three Greengrass components operate concurrently:

- **aws.greengrass.StreamManager (v2.3.0):** Manages the export queue for batch data, providing local FIFO buffering and automatic retry-with-backoff during cloud disconnection events.
- **aws.greengrass.Cli (v2.17.0):** Provides local component management and log access.
- **com.iiot.MLInference (v1.0.0):** The custom inference component described in Section III-C.

The gateway is provisioned with a dedicated AWS IoT Thing (`iiot-edge-gateway-01`) and an X.509 device certificate registered with IoT Core. Greengrass uses mutual TLS (mTLS) for all cloud communication over port 8883. Component-to-component communication uses Greengrass IPC (inter-process communication), isolating the inference component from direct internet access.

### C. ML Inference Component

The `com.iiot.MLInference` component loads two artifacts at startup: a trained ONNX Random Forest model (`pdm_model.onnx`, 6.1 MB) and a StandardScaler pickle (`scaler.pkl`). The component subscribes to the `iiot/edge/#` MQTT topic hierarchy via Greengrass IPC and processes each incoming sensor reading through the following pipeline:

1. Extract the 14 feature sensor values (s2, s3, s4, s7, s8, s9, s11, s12, s13, s14, s15, s17, s20, s21).
2. Apply the pre-fitted StandardScaler transform.
3. Run ONNX Runtime inference (`session.run`).
4. Route based on classification output:
   - **Anomaly (class 1):** Publish alert with full sensor context to `iiot/edge/{machine_id}/alerts` via IPC immediately.
   - **Normal (class 0):** Append to the rolling batch buffer. When the buffer reaches `BatchSize` readings (default 10), compute per-sensor mean values and publish a compressed summary to `iiot/edge/{machine_id}/batch` via IPC.

Stream Manager exports messages from both topics to AWS IoT Core over TLS. Anomaly messages are exported without delay; batch summaries are exported as they accumulate.

### D. ML Model Development

The predictive maintenance model is trained on a synthetic dataset generated to replicate the statistical properties of the NASA CMAPSS FD001 turbofan engine benchmark @saxena-2008. Two hundred synthetic engine units are simulated, each running from initialization to failure over a randomized lifetime of 128–362 cycles, producing 48,755 sensor readings in total.

Sensor degradation follows a validated piecewise profile calibrated to published FD001 sensor ranges and degradation slopes @ramasso-2014: readings remain at baseline until RUL = 60 cycles, degrade gradually from RUL = 60 to RUL = 30, then deteriorate rapidly in the anomaly zone (RUL ≤ 30). The anomaly label threshold of RUL ≤ 30 cycles is consistent with prior CMAPSS classification literature.

Fourteen informative sensor channels are used as features; the remaining seven CMAPSS sensors are excluded as they carry near-zero variance under FD001 operating conditions. A `StandardScaler` is fit on the training split and serialized for deployment.

The classifier is a scikit-learn `RandomForestClassifier` (100 estimators, max depth 8, minimum 8 samples per leaf, `balanced_subsample` class weighting) trained on an 80/20 stratified split. The trained model is exported to ONNX format (opset 12) using `skl2onnx` for runtime-agnostic edge deployment via ONNX Runtime.

---

## IV. Experimental Methodology

### A. Deployment Environment

All measurements were performed on an Amazon EC2 t3.small instance (Amazon Linux 2, 2 vCPU, 2 GB RAM) in the `us-east-1` region, running the full Greengrass v2 stack described above. The instance acts simultaneously as the simulated edge gateway and as the publisher of synthetic sensor telemetry, eliminating external network variability from the latency measurements and isolating the architectural differences between the two configurations as the sole experimental variable.

A Python 3.8 test client publishes 200 sensor readings at 5 Hz, simulating vibration and temperature telemetry from a single manufacturing floor machine (`machine-01`). Each reading is drawn from the CMAPSS normal operating distribution with a 10% probability of anomaly injection (sensor values scaled by 1.15× across all 14 channels). All timing measurements use `time.perf_counter()` with millisecond resolution.

### B. Configuration A — Cloud-Only Baseline

In Configuration A, the test client publishes each of the 200 sensor readings directly to AWS IoT Core via MQTT over TLS (port 8883, QoS 1). The client waits for the PUBACK acknowledgement before recording the round-trip latency and advancing to the next reading. No local processing, filtering, or aggregation is performed; every byte of every sensor reading is transmitted to the cloud. This configuration represents the conventional architecture against which the hybrid edge approach is evaluated.

Metrics captured: total bytes sent to cloud, per-reading payload size, PUBACK latency (mean, median, P95, P99).

### C. Configuration B — Hybrid Edge Architecture

In Configuration B, the same 200 sensor readings are processed locally by the `com.iiot.MLInference` component. The test client publishes readings to the local Greengrass IPC topic, the inference component classifies each reading and routes it through the selective forwarding logic described in Section III-C, and only the resulting anomaly alerts and batch summaries are transmitted to IoT Core.

Metrics captured: per-reading local inference latency (mean, median, P95, max), total bytes forwarded to cloud, number of cloud messages, cloud message PUBACK latency for anomaly alerts.

### D. Evaluation Protocol

The 200-reading measurement window is identical across both configurations: same sensor distribution, same anomaly injection rate, same 5 Hz publish cadence. The bandwidth comparison is made on total bytes reaching IoT Core per 200-reading window; this isolates the forwarding selection mechanism as the sole source of any observed difference. Latency comparison is made between the PUBACK round-trip time in Configuration A and the local ONNX inference time in Configuration B, reflecting the actual decision-path delay in each architecture.

Evaluation metrics M1–M5 are defined in Section III of this paper:

| Metric | Configuration A Source | Configuration B Source |
|---|---|---|
| M1 — Decision latency | MQTT PUBACK round-trip (ms) | ONNX `session.run` wall time (ms) |
| M2 — Cloud-bound bandwidth | Total bytes published to IoT Core | Total bytes published to IoT Core |
| M3 — ML F1-score (anomaly class) | — | sklearn classification report, 20% test split |
| M4 — Edge uptime during disconnection | 0% (cloud-dependent) | Local inference continues (C2 validated) |
| M5 — Cloud message count reduction | 200 individual messages | Batch summaries + anomaly alerts |
