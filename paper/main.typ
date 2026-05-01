#import "@preview/charged-ieee:0.1.4": ieee

#show: ieee.with(
  title:[Seamless Deployment of Machine Learning Inference at the Far Edge: An Empirical AWS IoT Greengrass Architecture for Industrial Predictive Maintenance],
  abstract:[
    The growth of Industrial Internet of Things (IIoT) devices in manufacturing environments generates continuous, high volume sensor data streams that require real time analysis for predictive maintenance. Traditional cloud centric architectures route all raw sensor telemetry to centralized servers for processing, introducing critical limitations in latency, bandwidth overhead, and resilience that are untenable in mission critical industrial deployments. This paper presents a hybrid cloud edge architecture for manufacturing predictive maintenance using AWS IoT Core and AWS IoT Greengrass v2, integrating local machine learning inference at the edge with selective cloud synchronization. Two configurations are deployed and compared on real AWS infrastructure: a cloud only baseline (Configuration A) and the proposed hybrid edge architecture (Configuration B), measuring end to end inference latency, bandwidth consumption, ML inference accuracy, and system uptime. The resilience advantage of the proposed architecture is demonstrated through a real cloud disconnection test, measuring operational continuity of local ML inference. Drawing from a comprehensive review of a myriad of papers across predictive maintenance, hybrid cloud edge architectures, and deployment resilience, this work identifies and addresses four critical research gaps: the lack of empirically validated Greengrass v2 deployments for manufacturing predictive maintenance, unmeasured resilience under cloud disconnection, unquantified bandwidth savings from selective edge synchronization, and the open MLOps feedback loop at the edge.
  ],
  authors: (
    (
      name: "Prince K. A. Boadu",
      department: [Department of Computer Engineering],
      organization: [Kwame Nkrumah University of Science and Technology],
      location: [Kumasi, Ghana],
      email: "pkappiahboadu@st.knust.edu.gh"
    ),
    (
      name: "Jeffery B. Kyei",
      department: [Department of Computer Engineering],
      organization:[Kwame Nkrumah University of Science and Technology],
      location: [Kumasi, Ghana],
      email: "jbkyei4@st.knust.edu.gh"
    ),
    (
      name: "Enoch K. Koranteng",
      department: [Department of Computer Engineering],
      organization:[Kwame Nkrumah University of Science and Technology],
      location: [Kumasi, Ghana],
      email: "ekkoranteng10@st.knust.edu.gh"
    ),
    (
      name: "Griffth S. Klogo",
      department: [Department of Computer Engineering],
      organization:[Kwame Nkrumah University of Science and Technology],
      location: [Kumasi, Ghana],
      email: "gsklogo.coe@knust.edu.gh"
    ),
  ),
  index-terms: ("Industrial IoT", "Predictive Maintenance", "Edge Computing", "AWS IoT Greengrass", "Cloud Edge Architecture", "Machine Learning", "MQTT"),
  bibliography: bibliography("refs.bib"),
  figure-supplement: [Fig.],
)

= Introduction

The rapid expansion of Industrial Internet of Things (IIoT) deployments in manufacturing environments has created an unprecedented demand for real time sensor data analysis and predictive maintenance capabilities. Modern manufacturing floors generate continuous, high frequency data streams from vibration sensors, temperature probes, current monitors, and acoustic emission detectors, all requiring immediate analysis to detect anomalies and predict equipment failures before they result in costly unplanned downtime.

Traditional cloud centric architectures have served as the default processing paradigm for IoT data, routing all raw sensor telemetry to centralized cloud servers for storage, analysis, and decision making. However, this approach introduces three critical limitations that are increasingly untenable in mission critical industrial deployments. First, cloud round trip times of 300--800~ms far exceed the sub-100~ms threshold identified across the literature as the boundary for real time industrial safety response @sathupadi-2024 @mohammed-2024. Second, continuous streaming of high frequency sensor data from multi machine factory floors creates unsustainable bandwidth costs and network congestion, with no filtering or prioritization at the source. Third, cloud dependency creates a single point of failure; network interruptions halt all monitoring and inference capabilities, leaving equipment unattended.

The emerging consensus in the literature is a hierarchical computing model comprising an Edge layer for immediate, latency sensitive inference, a Fog layer for regional aggregation and coordination, and a Cloud layer for historical analytics, model training, and global orchestration @briatore-2025 @kapoor-2025. While hybrid cloud edge architectures have been widely proposed as the solution to these limitations, the existing literature reveals a critical gap: there is no empirically validated deployment of AWS IoT Core and AWS IoT Greengrass specifically for manufacturing predictive maintenance that reports measurable performance data across latency, bandwidth, and resilience. The theoretical advantages of the hybrid approach remain unsubstantiated by real infrastructure evidence for this domain.

This paper addresses that gap directly through a real AWS deployment. Specifically, this paper pursues four primary research objectives: (i)~design a hybrid cloud edge architecture for industrial predictive maintenance using AWS IoT Core and AWS IoT Greengrass, integrating local ML inference at the edge with selective cloud synchronization; (ii)~deploy and compare two configurations, a cloud only baseline and the proposed hybrid edge architecture, on real AWS infrastructure, measuring latency, bandwidth consumption, ML inference accuracy, and system uptime; (iii)~demonstrate and quantify the resilience advantage of the proposed architecture by disconnecting the Greengrass gateway from the cloud and measuring operational continuity of local ML inference; and (iv)~provide a practical, reproducible deployment framework using AWS services that industrial practitioners can adapt for real world IIoT predictive maintenance applications.

The remainder of this paper is organized as follows. Section~II presents a comprehensive review of related work spanning hierarchical IoT architectures, predictive maintenance algorithms, hybrid cloud edge design patterns, and deployment resilience. Section~III identifies the specific research gaps addressed by this work. Section~IV details the proposed architecture and experimental methodology. Section~V presents the evaluation metrics and results. Section~VI discusses findings and implications. Section~VII concludes the paper and outlines directions for future work.

= Literature Review

== The Shift from Centralized to Hierarchical IoT Architectures

The foundational limitation motivating this research is well established: centralized cloud architectures are architecturally insufficient for the real time demands of industrial IoT. Qiu~_et~al._~@qiu-2020 provide a comprehensive survey of edge computing in IIoT, identifying latency, bandwidth cost, and security as the three primary failure modes of cloud only deployments. Mohammed~@mohammed-2024 reinforces this, arguing that a symbiotic cloud edge relationship is "no longer a luxury but a critical business necessity" for mission critical applications, with end to end latency reductions of up to 40% demonstrated through cloud edge co-design.

The emerging consensus in the literature is a three tier hierarchical model: an Edge layer handling immediate, latency sensitive inference; a Fog layer managing regional aggregation and coordination; and a Cloud layer handling historical analytics, model training, and global orchestration. Briatore and Braggio~@briatore-2025 demonstrate that this three layer framework enables Industry~3.0 plants to adopt Industry~4.0 characteristics, achieving high adaptability to production demand fluctuations. Kapoor~_et~al._~@kapoor-2025 extend this view, conducting a survey of multi layered computing paradigms and finding that edge fog cloud integration using MQTT based data transfer is essential for balancing processing speed against analytical depth in industrial predictive maintenance.

== Predictive Maintenance in Industrial IoT

Predictive maintenance (PdM) in manufacturing represents one of the most demanding use cases for IIoT architectures, requiring real time anomaly detection, failure prediction, and alert generation under strict latency and accuracy constraints. The literature has converged on a set of common algorithmic and architectural patterns for this domain.

*Algorithmic convergence.* Long Short Term Memory (LSTM) networks have emerged as the dominant model architecture for temporal failure prediction. Sathupadi~_et~al._~@sathupadi-2024 demonstrate a hybrid edge cloud PdM framework using KNN models at the edge for immediate anomaly detection and LSTM models in the cloud for in depth failure prediction, achieving a 35% latency reduction, 28% decrease in energy consumption, and 60% bandwidth reduction compared to cloud only approaches. Yu~_et~al._~@yu-2022 deploy stacked sparse autoencoders at the edge for real time fault detection in manufacturing, enabling detection of major equipment failures up to 8~days in advance while dramatically reducing storage and server costs. Saleh~_et~al._~@saleh-2026 introduce SEMAS, a self evolving hierarchical multi agent system using Reinforcement Learning across Edge, Fog, and Cloud tiers, achieving sub millisecond anomaly detection latency.

*The data scarcity problem.* A persistent challenge in industrial PdM is the extreme class imbalance between normal operational data and fault events. Somu and Dasappa~@somu-2024 address this directly with IntelliPdM, a framework that uses synthetic data generation to augment training datasets, achieving 93--95% accuracy on manufacturing PdM tasks with a reported 10x return on investment. Saley~_et~al._~@saley-2025 demonstrate in the nuclear industry that hybridizing domain expert knowledge with data driven ML dramatically improves fault detection, raising the F1 score from 56.36% to 93.12% and extending the prediction horizon from 3 to 24~hours.

*Privacy preserving inference.* Vejendla~@vejendla-2026 demonstrates that Federated Learning combined with edge computing can reduce inference latency by up to 60% with less than 1% accuracy deviation from centralized models, while ensuring that raw industrial data never leaves the factory floor, a critical requirement for protecting proprietary manufacturing data.

== Hybrid Cloud-Edge Architectures: Design Patterns and Benchmarks

Beyond the predictive maintenance domain, the broader IIoT architecture literature provides foundational design patterns for hybrid cloud edge systems.

Kompally~@kompally-2025 proposes a microservices based hybrid cloud edge architecture for real time IIoT analytics, demonstrating a 30% latency reduction and improved Remaining Useful Life (RUL) prediction accuracy through containerized three layer design comprising Edge, Cloud, and Control Plane tiers. Mih~_et~al._~@mih-2023 introduce ECAvg, an edge cloud collaborative learning approach using averaged model weights, showing accuracy improvements for complex deep neural networks while warning of "negative transfer" risks for simpler architectures.

The JANUS benchmarking study by Shankar~_et~al._~@shankar-2020 provides particularly relevant empirical evidence: in a direct comparison of commercial and open source cloud and edge platforms for IoT workloads, the study finds that AWS IoT Greengrass is superior for lightweight anomaly detection tasks, while open source algorithms on cloud VMs are significantly cheaper but substantially slower for compute intensive tasks. This result directly motivates our choice of AWS Greengrass as the edge runtime in the proposed architecture.

Jamil~_et~al._~@jamil-2024 survey current IoT platforms (ThingsBoard, Azure IoT, Eclipse Ditto) and identify persistent gaps in semantic interoperability and resilient failover mechanisms, concluding that advancing IIoT requires moving beyond cloud centricity toward distributed intelligence with standardized communication protocols. Lee~_et~al._~@lee-2020 provide an important cautionary finding: the benefits of edge computing are conditional on edge hardware specifications; if edge devices are underpowered, cloud processing may outperform local inference, highlighting the importance of hardware aware deployment decisions.

== Deployment, MLOps, and Resilience

The operational lifecycle of edge deployed ML models introduces a distinct set of research concerns beyond initial architecture design.

*MLOps at the edge.* Mateo-Casalí~_et~al._~@mateo-casali-2026 propose a reference architecture for Machine Learning Operations, identifying a "Closed Loop Gap" in current practice: models are deployed but rarely monitored for drift, and retraining is typically manual. Psaromanolakis~_et~al._~@psaromanolakis-2023 address this with an Edge Intelligence (EI) Agent concept for continuous model lifecycle management within 6G edge systems. Jean~@jean-2025 demonstrates an MLOps pipeline for real time threat intelligence in cloud edge architectures, emphasizing that in dynamic environments, a model that does not adapt to changing data distributions becomes obsolete almost immediately.

*Resilience and self healing.* Mwangi~_et~al._~@mwangi-2024 introduce "Self-X" properties for industrial IoT edge networks, self configuring, self healing, and self optimizing, within the context of offshore wind farm management. Aral and Brandic~@aral-2021 provide a technical treatment of spatiotemporal failure dependencies in edge computing, using Bayesian networks to anticipate edge server failures based on historical patterns. Zhukabayeva~_et~al._~@zhukabayeva-2025 extend the resilience discussion to the cybersecurity dimension, identifying DDoS attacks and malware as threats that can cause system level failure in IIoT edge deployments and proposing defense in depth countermeasures.

*Distributed and federated learning.* Le~_et~al._~@le-2024 conduct a comprehensive survey of distributed ML for IoT, positioning Federated Learning as the primary mechanism for maintaining data sovereignty while improving global model accuracy across geographically distributed industrial nodes. Kawonga~_et~al._~@kawonga-2026 review Physics Informed Neural Networks and TinyML frameworks for real time photovoltaic monitoring, identifying federated edge cloud collaboration as a critical research frontier for energy systems.

== Summary and Positioning of This Work

The reviewed literature establishes a clear and unified direction: hybrid cloud edge architectures with local ML inference are the necessary evolution beyond cloud centric IIoT. However, the existing work leaves specific empirical and validation gaps that motivate the contributions of this paper. Against this backdrop, this paper makes four contributions to the field of Industrial Internet of Things and edge computing:

*C1 — Validated AWS Greengrass deployment for manufacturing PdM.* We provide an empirically validated deployment of AWS IoT Greengrass~v2 as an edge inference runtime for manufacturing predictive maintenance, extending the JANUS benchmark findings~@shankar-2020 to the time-series ML domain and reporting CloudWatch measured performance metrics from a working Greengrass ML component running on real AWS infrastructure.

*C2 — Quantified bandwidth savings from selective edge synchronization.* We isolate and measure, on the same deployed infrastructure, the cloud-bound byte volume produced by a full-streaming baseline against an edge-filtered configuration that forwards only ML inference outputs and compressed batch summaries, providing the controlled per-window bandwidth comparison that the prior literature has reported only as a secondary observation.

*C3 — Instrumented resilience pathway under cloud disconnection.* We define and instrument the evaluation pathway for system uptime, alert continuity, and Stream Manager queuing behavior of a Greengrass based hybrid edge architecture during a controlled cloud disconnection event on real AWS infrastructure, establishing the measurement methodology that the literature has thus far only theorized; the full disconnection experiment and its quantitative results are reported as a planned extension of this work.

*C4 — Practical deployment framework.* We provide a reproducible architecture and deployment framework using AWS IoT Core, Greengrass~v2, and SageMaker that industrial practitioners and researchers can adapt for real world IIoT predictive maintenance deployments, including the federated learning workflow pathway for future MLOps loop closure at the edge.

Together, these contributions are realized through a real AWS deployment that compares a cloud only baseline against the proposed hybrid edge architecture using simulation based experimentation with Python generated synthetic sensor data and AWS IoT Core combined with Greengrass for the cloud edge infrastructure.