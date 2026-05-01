# Related Work

## 2.1 The Shift from Centralized to Hierarchical IoT Architectures

The foundational limitation motivating this research is well-established: centralized cloud architectures are architecturally insufficient for the real-time demands of industrial IoT. Qiu et al. (2020) provide a comprehensive survey of edge computing in IIoT, identifying latency, bandwidth cost, and security as the three primary failure modes of cloud-only deployments. Mohammed (2024) reinforces this, arguing that a symbiotic cloud-edge relationship is "no longer a luxury but a critical business necessity" for mission-critical applications, with end-to-end latency reductions of up to 40% demonstrated through cloud-edge co-design.

The emerging consensus in the literature is a three-tier hierarchical model: an Edge layer handling immediate, latency-sensitive inference; a Fog layer managing regional aggregation and coordination; and a Cloud layer handling historical analytics, model training, and global orchestration. Briatore and Braggio (2025) demonstrate that this three-layer framework enables Industry 3.0 plants to adopt Industry 4.0 characteristics, achieving high adaptability to production demand fluctuations. Kapoor et al. (2025) extend this view, conducting a survey of multi-layered computing paradigms and finding that edge-fog-cloud integration using MQTT-based data transfer is essential for balancing processing speed against analytical depth in industrial predictive maintenance.

## 2.2 Predictive Maintenance in Industrial IoT

Predictive maintenance (PdM) in manufacturing represents one of the most demanding use cases for IIoT architectures, requiring real-time anomaly detection, failure prediction, and alert generation under strict latency and accuracy constraints. The literature has converged on a set of common algorithmic and architectural patterns for this domain.

**Algorithmic convergence.** Long Short-Term Memory (LSTM) networks have emerged as the dominant model architecture for temporal failure prediction. Sathupadi et al. (2024) demonstrate a hybrid edge-cloud PdM framework using KNN models at the edge for immediate anomaly detection and LSTM models in the cloud for in-depth failure prediction, achieving a 35% latency reduction, 28% decrease in energy consumption, and 60% bandwidth reduction compared to cloud-only approaches. Yu et al. (2023) deploy stacked sparse autoencoders at the edge for real-time fault detection in manufacturing, enabling detection of major equipment failures up to 8 days in advance while dramatically reducing storage and server costs. Saleh et al. (2026) introduce SEMAS, a self-evolving hierarchical multi-agent system using Reinforcement Learning across Edge, Fog, and Cloud tiers, achieving sub-millisecond anomaly detection latency.

**The data scarcity problem.** A persistent challenge in industrial PdM is the extreme class imbalance between normal operational data and fault events. Somu and Dasappa (2024) address this directly with IntelliPdM, a framework that uses synthetic data generation (SMARTHome module) to augment training datasets, achieving 93–95% accuracy on manufacturing PdM tasks with a reported 10x return on investment. Saley et al. (2025) demonstrate in the nuclear industry that hybridizing domain-expert knowledge with data-driven ML dramatically improves fault detection, raising the F1-score from 56.36% to 93.12% and extending the prediction horizon from 3 to 24 hours.

**Privacy-preserving inference.** Vejendla (2026) demonstrates that Federated Learning combined with edge computing can reduce inference latency by up to 60% with less than 1% accuracy deviation from centralized models, while ensuring that raw industrial data never leaves the factory floor — a critical requirement for protecting proprietary manufacturing data.

## 2.3 Hybrid Cloud-Edge Architectures: Design Patterns and Benchmarks

Beyond the predictive maintenance domain, the broader IIoT architecture literature provides foundational design patterns for hybrid cloud-edge systems.

Kompally (2025) proposes a microservices-based hybrid cloud-edge architecture for real-time IIoT analytics, demonstrating a 30% latency reduction and improved Remaining Useful Life (RUL) prediction accuracy through containerized three-layer design (Edge, Cloud, Control Plane). Mih et al. (2023) introduce ECAvg, an edge-cloud collaborative learning approach using averaged model weights, showing accuracy improvements for complex deep neural networks while warning of "negative transfer" risks for simpler architectures.

The JANUS benchmarking study by Shankar et al. (2020) provides particularly relevant empirical evidence: in a direct comparison of commercial and open-source cloud and edge platforms for IoT workloads, the study finds that **AWS IoT Greengrass is superior for lightweight anomaly detection tasks**, while open-source algorithms on cloud VMs are significantly cheaper but substantially slower for compute-intensive tasks. This result directly motivates our choice of AWS Greengrass as the edge runtime in the proposed architecture.

Jamil et al. (2024) survey current IoT platforms (ThingsBoard, Azure IoT, Eclipse Ditto) and identify persistent gaps in semantic interoperability and resilient failover mechanisms, concluding that advancing IIoT requires moving beyond cloud-centricity toward distributed intelligence with standardized communication protocols. Lee et al. (2020) provide an important cautionary finding: the benefits of edge computing are conditional on edge hardware specifications — if edge devices are underpowered, cloud processing may outperform local inference, highlighting the importance of hardware-aware deployment decisions.

## 2.4 Deployment, MLOps, and Resilience

The operational lifecycle of edge-deployed ML models introduces a distinct set of research concerns beyond initial architecture design.

**MLOps at the edge.** Mateo-Casalí et al. (2026) propose a reference architecture for Machine Learning Operations, identifying a "Closed-Loop Gap" in current practice: models are deployed but rarely monitored for drift, and retraining is typically manual. Psaromanolakis et al. (2023) address this with an Edge Intelligence (EI) Agent concept for continuous model lifecycle management within 6G edge systems. Jean (2025) demonstrates an MLOps pipeline for real-time threat intelligence in cloud-edge architectures, emphasizing that in dynamic environments, a model that does not adapt to changing data distributions becomes obsolete almost immediately.

**Resilience and self-healing.** Mwangi et al. (2024) introduce "Self-X" properties for industrial IoT-edge networks — self-configuring, self-healing, and self-optimizing — within the context of offshore wind farm management. Aral and Brandic (2021) provide a technical treatment of spatiotemporal failure dependencies in edge computing, using Bayesian networks to anticipate edge server failures based on historical patterns. Zhukabayeva et al. (2025) extend the resilience discussion to the cybersecurity dimension, identifying DDoS attacks and malware as threats that can cause system-level failure in IIoT-edge deployments and proposing defense-in-depth countermeasures.

**Distributed and federated learning.** Le et al. (2025) conduct a comprehensive survey of distributed ML for IoT, positioning Federated Learning as the primary mechanism for maintaining data sovereignty while improving global model accuracy across geographically distributed industrial nodes. Kawonga et al. (2026) review Physics-Informed Neural Networks and TinyML frameworks for real-time photovoltaic monitoring, identifying federated edge-cloud collaboration as a critical research frontier for energy systems.

## 2.5 Summary and Positioning of This Work

The reviewed literature establishes a clear and unified direction: hybrid cloud-edge architectures with local ML inference are the necessary evolution beyond cloud-centric IIoT. However, as detailed in Section 3 (Research Gaps), the existing work leaves specific empirical and validation gaps that this paper addresses: (1) a controlled simulation benchmark comparing cloud-only vs. hybrid edge under identical conditions; (2) empirical validation of AWS Greengrass v2 for manufacturing PdM inference; (3) measured resilience during cloud disconnection; and (4) quantified bandwidth savings from selective edge synchronization. This paper fills these gaps through simulation-based experimentation using Python-generated synthetic sensor data (NumPy/SciPy) and AWS IoT Core + Greengrass for the cloud-edge infrastructure.

---

## References (BibTeX — Combined)

All 31 BibTeX entries are available in `iiot-hybrid-architecture paper progress.txt`. The entries below are the primary citations for this section.

Key citations: Qiu et al. (2020), Mohammed (2024), Briatore & Braggio (2025), Kapoor et al. (2025), Sathupadi et al. (2024), Yu et al. (2023), Saleh et al. (2026), Somu & Dasappa (2024), Saley et al. (2025), Vejendla (2026), Kompally (2025), Shankar et al. (2020), Jamil et al. (2024), Lee et al. (2020), Mateo-Casalí et al. (2026), Psaromanolakis et al. (2023), Jean (2025), Mwangi et al. (2024), Aral & Brandic (2021), Zhukabayeva et al. (2025), Le et al. (2025), Kawonga et al. (2026).
