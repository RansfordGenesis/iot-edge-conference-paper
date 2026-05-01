# Research Gaps

The following four gaps are identified from the comparative analysis of 31 reviewed papers across the domains of Predictive Maintenance, Hybrid Cloud-Edge Architectures, and Deployment & Resilience.

---

## Gap 1: AWS IoT Greengrass for Edge ML Inference in Manufacturing PdM Is Unvalidated

**Evidence:** Shankar et al. (2020) in the JANUS benchmarking paper confirm that "AWS IoT Greengrass is superior for lightweight anomaly detection" workloads. However, this finding is based on compute-light object detection tasks, not on ML inference for industrial predictive maintenance (vibration/temperature time-series). Kompally (2025) proposes a microservices-based hybrid architecture but uses generic containerization, not Greengrass specifically. No published study validates AWS IoT Greengrass v2 as the edge inference runtime for manufacturing predictive maintenance with a deployed ML model (LSTM or autoencoder) and reports performance metrics from that specific deployment.

**Gap:** The literature lacks an empirically validated Greengrass v2 deployment for manufacturing PdM that reports real CloudWatch-measured performance data.

**This paper's contribution:** A working Greengrass v2 deployment with an LSTM or random forest model running local inference on real edge device data, with AWS CloudWatch metrics exported to validate and report performance.

---

## Gap 2: Resilience Under Cloud Disconnection Is Asserted but Not Measured

**Evidence:** Aral & Brandic (2021) provide a theoretical treatment of spatiotemporal failure dependencies in edge networks. Mwangi et al. (2024) propose Self-X (self-healing, self-configuring) properties for edge IoT networks. Both argue that edge architectures can sustain operations during cloud outages. However, neither provides measured uptime percentages, queuing behavior data, or recovery time metrics from a real disconnection event on deployed infrastructure.

**Gap:** The quantifiable resilience of hybrid edge architectures — specifically how long local inference continues, how data is queued, and how quickly cloud sync resumes upon reconnection — is not empirically measured in the literature against real deployed infrastructure.

**This paper's contribution:** A real cloud disconnection test on the deployed Greengrass setup, measuring system uptime (%), alert continuity, and data queue behavior during and after disconnection using actual Greengrass logs and CloudWatch metrics.

---

## Gap 3: Bandwidth Savings from Selective Edge Synchronization Are Not Rigorously Quantified

**Evidence:** Vejendla (2026) reports a 60% latency reduction from Federated Learning + edge computing. Hafeez et al. (2021) argue that edge-level sampling, compression, and fusion are essential for cost-effective IIoT. However, bandwidth measurements are rarely the primary metric — they are typically secondary observations without a controlled comparison against a full-streaming baseline, and the specific savings attributable to selective sync (only anomalies and summaries) versus full stream are not isolated on real infrastructure.

**Gap:** The precise bandwidth reduction achievable by routing only ML inference outputs and anomaly alerts to the cloud — rather than raw sensor streams — has not been isolated and measured from a real deployed system.

**This paper's contribution:** Measurement of bytes transferred under Configuration A (full cloud forwarding) vs. Configuration B (edge-filtered selective sync) using Greengrass stream manager with CloudWatch `BytesIn` monitoring on the real AWS deployment.

---

## Gap 4: The MLOps Feedback Loop at the Edge Remains an Open Research Problem

**Evidence:** Mateo-Casalí et al. (2026) identify a "Closed-Loop Gap" in their MLOps reference architecture: models are deployed but rarely monitored for performance decay (drift), and retraining is manual. Psaromanolakis et al. (2023) propose an EI Agent (Edge Intelligence Agent) concept for continuous model lifecycle management at the edge. Jean (2025) addresses this for cybersecurity threat models but not for industrial PdM.

**Gap:** No published implementation demonstrates a complete MLOps loop at the edge — where model drift is detected locally, retraining is triggered, and updated model weights are synced back to the cloud — within a manufacturing IIoT context using commercially available platforms (such as SageMaker + Greengrass).

**This paper's contribution:** While a full MLOps loop is beyond the scope of this work, the proposed architecture explicitly defines the pathway for it and identifies it as a direction for future work, with the AWS federated workflow (SageMaker → IoT Core → Greengrass → gradient upload → aggregation) serving as the implementation blueprint.
