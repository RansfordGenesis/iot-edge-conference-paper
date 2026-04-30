# Evaluation Metrics

The following metrics are used to compare Configuration A (cloud-only baseline) against Configuration B (proposed hybrid edge architecture). All metrics are measured from the real AWS deployment infrastructure.

---

## Primary Metrics

### M1 — End-to-End Inference Latency (ms)
**Definition:** Time elapsed from the moment a sensor reading is received to the moment a maintenance decision (normal / anomaly / alert) is produced.

- **Configuration A measurement:** Device → IoT Core → cloud ML inference → decision returned. Measured as round-trip time including network transit and cloud processing, captured via IoT Core message timestamps and CloudWatch.
- **Configuration B measurement:** Device → Greengrass local ML inference → decision. Measured as local processing time only, captured via Greengrass component logs.
- **Target:** Configuration B should achieve sub-100ms latency (threshold established across the literature as the boundary for real-time industrial safety).
- **Tool:** AWS CloudWatch latency metrics + Greengrass component log timestamps.

---

### M2 — Cloud-Bound Bandwidth Consumption (MB/s and total MB per measurement window)
**Definition:** Volume of data transmitted from the edge device or gateway to AWS IoT Core per unit time.

- **Configuration A measurement:** All raw device readings forwarded continuously to IoT Core.
- **Configuration B measurement:** Only anomaly alerts and compressed periodic summaries forwarded to IoT Core via Greengrass stream manager.
- **Target:** Configuration B should achieve ≥40% reduction in bandwidth compared to Configuration A (conservative target; literature reports 28–60% in comparable setups).
- **Tool:** CloudWatch `PublishIn.Success` byte count on IoT Core + Greengrass stream manager export logs.

---

### M3 — ML Inference Accuracy (F1-Score)
**Definition:** The harmonic mean of Precision and Recall for the predictive maintenance classification task (normal vs. anomaly/fault).

- **Why F1, not Accuracy:** Industrial datasets are class-imbalanced (thousands of normal readings for every fault event). F1-score penalizes models that predict "normal" for everything to achieve high nominal accuracy.
- **Measurement:** The same trained ML model is deployed in the cloud (Configuration A) and on Greengrass (Configuration B). F1-scores are compared to confirm that edge quantization/optimization does not degrade accuracy beyond an acceptable threshold (≤2% drop).
- **Tool:** Scikit-learn classification report on NASA CMAPSS test set.

---

### M4 — System Uptime During Cloud Disconnection (%)
**Definition:** Percentage of time that the system continues to generate valid maintenance decisions during a real cloud disconnection event.

- **Configuration A:** All inference depends on cloud connectivity. Uptime = 0% during disconnection.
- **Configuration B:** Local Greengrass inference continues independently. Uptime expected = 100% during disconnection (decisions still generated locally).
- **Measurement window:** 5-minute disconnection period (achieved by blocking outbound traffic on the Greengrass host via firewall rule).
- **Tool:** Greengrass local logs + CloudWatch gap analysis confirming local operation during disconnection period.

---

### M5 — Cloud Compute Load Reduction (%)
**Definition:** Reduction in cloud-side compute operations (ML inference calls, data ingestion volume) achieved by the edge architecture.

- **Configuration A:** Cloud handles 100% of inference calls at full device data rate.
- **Configuration B:** Cloud receives only filtered alerts and summary data. Edge handles all real-time inference.
- **Measurement:** CloudWatch IoT Core message count and SageMaker/Lambda invocation count compared between configurations.
- **Target:** ≥50% reduction in cloud-side ML inference invocations.

---

## Secondary Metrics

| Metric | Definition | Relevance |
|---|---|---|
| **Alert Response Time (ms)** | Time from fault onset to alert generation | Validates practical maintenance utility |
| **Model Size at Edge (MB)** | Size of the deployed ONNX/TFLite model | Validates edge deployability on constrained hardware |
| **Queue Drain Time (s)** | Time to sync queued data after cloud reconnection | Validates recovery behavior |
| **Data Compression Ratio** | Raw bytes vs. compressed bytes sent via stream manager | Quantifies compression benefit |

---

## Measurement Summary Table (to be filled with results)

| Metric | Configuration A (Cloud-Only) | Configuration B (Hybrid Edge) | Improvement |
|---|---|---|---|
| Inference Latency (ms) | TBD | TBD | TBD % reduction |
| Bandwidth (MB/s) | TBD | TBD | TBD % reduction |
| F1-Score | TBD | TBD | TBD Δ |
| Uptime during disconnect (%) | 0% | TBD | — |
| Cloud compute load reduction (%) | Baseline | TBD | TBD % |
