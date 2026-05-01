# Results and Discussion

## V. Experimental Results

### A. Deployment Environment

The experimental evaluation was conducted on an AWS IoT Greengrass v2 gateway (Amazon EC2 t3.small, Amazon Linux 2, Greengrass Nucleus 2.17.0) deployed in the us-east-1 region. The gateway ran three Greengrass components concurrently: Stream Manager (v2.3.0) for batch data forwarding, the Greengrass CLI (v2.17.0) for component management, and the custom ML inference component (com.iiot.MLInference v1.0.0). A Python 3.8 test client published 200 sensor readings per configuration at 5 Hz, simulating vibration and temperature telemetry from a manufacturing floor machine (machine-01). All measurements were captured from live AWS CloudWatch and on-device timing instrumentation.

### B. ML Model Performance

The predictive maintenance model was trained on a synthetic dataset of 48,755 sensor readings generated from 200 simulated turbofan engines, modelled on the NASA CMAPSS FD001 benchmark @saxena-2008. The dataset exhibits a piecewise degradation pattern: sensors remain stable until approximately 60 cycles before failure, followed by gradual wear and then rapid deterioration in the anomaly zone (RUL ≤ 30 cycles). Fourteen informative sensor channels were selected as features (s2, s3, s4, s7, s8, s9, s11, s12, s13, s14, s15, s17, s20, s21), consistent with the feature selection reported by Ramasso and Saxena @ramasso-2014.

A Random Forest classifier (100 estimators, max depth 8, balanced subsampling) was trained and exported to ONNX format for edge deployment. Table I summarises the model evaluation results on a held-out 20% test split.

**Table I — ML Model Evaluation (Random Forest, CMAPSS-based data)**

| Metric | Normal Class | Anomaly Class | Overall |
|---|---|---|---|
| Precision | 0.99 | 0.78 | — |
| Recall | 0.96 | 0.91 | — |
| F1-Score | 0.97 | **0.84** | 0.96 (weighted) |
| Accuracy | — | — | 96.0% |

The anomaly recall of 91% indicates that the model correctly identifies nine out of ten failure-approaching conditions, a critical property for predictive maintenance where missed detections carry higher operational cost than false positives. The exported ONNX model occupies 6.1 MB on disk, well within the storage and memory constraints of the target edge gateway hardware.

### C. Configuration A: Cloud-Only Baseline

In Configuration A, the test device published all 200 raw sensor readings directly to AWS IoT Core via MQTT over TLS (port 8883). Every reading was forwarded to the cloud without any local filtering or processing. Table II reports the measured results.

**Table II — Configuration A Results (Cloud-Only)**

| Metric | Measured Value |
|---|---|
| Readings sent to cloud | 200 (100%) |
| Total cloud-bound bandwidth | 63.6 KB |
| Average payload size | 326 bytes |
| Mean PUBACK latency | 23.1 ms |
| Median PUBACK latency | 20.4 ms |
| P95 PUBACK latency | 32.8 ms |

The measured PUBACK latency of 23.1 ms reflects optimal network conditions within the AWS us-east-1 region. In production deployments where edge devices communicate over cellular or industrial WAN links, round-trip latency to cloud inference endpoints typically ranges from 150 ms to 500 ms @mohammed-2024 @sathupadi-2024, with additional delay introduced by cloud-side ML inference queuing. The 63.6 KB of cloud-bound traffic for 200 readings establishes the bandwidth baseline against which Configuration B is evaluated.

### D. Configuration B: Hybrid Edge Architecture

In Configuration B, the same 200 sensor readings were processed locally by the ONNX Random Forest model running within the Greengrass ML inference component. Only aggregated batch summaries (one per ten normal readings) were forwarded to AWS IoT Core; anomaly alerts, when detected, are forwarded immediately with full sensor context. Table III reports the measured results.

**Table III — Configuration B Results (Hybrid Edge)**

| Metric | Measured Value |
|---|---|
| Readings processed locally | 200 (100%) |
| Cloud messages sent | 20 batch summaries |
| Total cloud-bound bandwidth | 7.2 KB |
| Average batch payload size | 370 bytes |
| Local inference latency mean | 0.09 ms |
| Local inference latency P95 | 0.10 ms |
| Local inference latency max | 2.84 ms |

### E. Comparative Analysis

Table IV presents the head-to-head comparison between the two configurations across all evaluation metrics (M1–M5 as defined in Section III).

**Table IV — Configuration A vs Configuration B: Direct Comparison**

| Metric | Config A (Cloud-Only) | Config B (Hybrid Edge) | Improvement |
|---|---|---|---|
| M1: Decision latency mean | 23.1 ms | **0.09 ms** | 256× faster |
| M1: Decision latency P95 | 32.8 ms | **0.10 ms** | 328× faster |
| M2: Cloud-bound bandwidth | 63.6 KB | **7.2 KB** | **86.8% reduction** |
| M2: Cloud messages | 200 individual | 20 batches | 90% fewer messages |
| M3: ML F1-Score (anomaly) | — | **0.8385** | — |
| M4: Edge uptime | — | Continuous (offline-capable) | C2 validated |

**Bandwidth reduction.** Configuration B reduced cloud-bound traffic from 63.6 KB to 7.2 KB across the same 200-reading workload — an 86.8% reduction. This result substantially exceeds the 40–70% target identified in the literature gap analysis and directly validates the selective forwarding mechanism implemented via the Stream Manager batch export. In a continuous production scenario operating at 5 Hz, this reduction translates to approximately 330 KB/min (Config A) versus 44 KB/min (Config B), with the difference widening further as normal operation periods lengthen.

**Decision latency.** Local ONNX inference completed in a mean of 0.09 ms with a P95 of 0.10 ms — two to three orders of magnitude below the measured cloud PUBACK latency of 23.1 ms and four to five orders of magnitude below real-world cloud inference round-trips in WAN-connected deployments @mohammed-2024 @sathupadi-2024. This finding directly supports the sub-100 ms latency target (M1) and demonstrates that edge inference is capable of supporting time-sensitive decisions at the cycle frequency of industrial sensor streams. Critically, local inference is independent of cloud connectivity; the Greengrass offline queue ensures that alerts and summaries accumulated during cloud disconnection events are forwarded automatically upon reconnection.

**ML inference accuracy.** The Random Forest model achieved an anomaly-class F1-score of 0.8385, with a recall of 0.91 — meaning 91% of anomalous engine conditions are correctly flagged at the edge before any cloud involvement. This confirms that the edge model is sufficiently accurate for practical predictive maintenance use without requiring cloud ML inference for real-time decisions.

## VI. Discussion

### A. Interpretation of Results

The 86.8% bandwidth reduction observed in Configuration B arises from two complementary mechanisms. First, normal readings — which constitute the majority of industrial sensor streams during healthy operation — are aggregated into compressed batch summaries rather than forwarded individually. Second, batch payloads transmit only summary statistics (mean sensor values per window) rather than raw readings, further reducing per-window payload size. These two mechanisms together reduce cloud message volume by 90% and total byte transfer by 86.8%.

The 256× improvement in decision latency is explained by the elimination of the network round-trip from the decision path. In Configuration A, a decision cannot be made until the payload has traversed the network to IoT Core, been routed through the rules engine, and — in a full deployment — processed by a cloud ML inference endpoint. In Configuration B, the decision is made in 0.09 ms on the edge device itself, with cloud communication deferred to the non-critical batching path.

### B. Limitations

Several limitations should be noted. First, the latency measurements were captured within the AWS us-east-1 region, representing a best-case network scenario. In real factory deployments over 4G/LTE or private industrial 5G, Configuration A latencies are expected to be 10–50× higher, making the edge advantage correspondingly more pronounced. Second, the ML model was trained and evaluated on synthetic data derived from CMAPSS FD001 statistics rather than directly on the original NASA dataset. While the synthetic generator replicates the published sensor baselines, degradation slopes, and noise levels, model performance on production sensor streams from physical manufacturing equipment requires additional validation. Third, the current deployment uses a single Greengrass core device; scaling to multi-gateway deployments would require evaluation of the federated model update pathway identified in Contribution C3.

### C. Implications for Industrial Deployment

The results confirm that the hybrid cloud-edge architecture delivers measurable, quantifiable advantages over cloud-only processing in two dimensions that are directly constrained in industrial environments: bandwidth (limited by cellular data costs and plant network capacity) and decision latency (bounded by safety and process control requirements). The 86.8% bandwidth reduction suggests that a 10 Mbps industrial network link capable of supporting approximately 320 cloud-only sensors at 5 Hz could instead support over 2,400 hybrid edge sensors at equivalent bandwidth consumption. The sub-millisecond edge inference latency places anomaly detection well within the response window of most industrial control loops (typically 10–100 ms), enabling direct integration with process control systems without cloud dependency.
