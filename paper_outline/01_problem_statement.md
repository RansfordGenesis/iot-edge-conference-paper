# Problem Statement & Research Objectives

## Problem Statement

The proliferation of Industrial Internet of Things (IIoT) devices in manufacturing environments generates continuous, high-volume sensor data streams that require real-time analysis for predictive maintenance. Traditional cloud-centric architectures route all raw sensor telemetry to centralized cloud servers for processing, introducing three critical limitations that are untenable in mission-critical industrial deployments:

1. **Latency:** Cloud round-trip times of 300–800ms far exceed the sub-100ms threshold identified across the literature as the boundary for real-time industrial safety response (Sathupadi et al., 2024; Mohammed, 2024).
2. **Bandwidth overhead:** Continuous streaming of high-frequency sensor data from multi-machine floors creates unsustainable bandwidth costs and network congestion, with no filtering or prioritization at the source.
3. **Resilience failure:** Cloud dependency creates a single point of failure; network interruptions halt all monitoring and inference capabilities, leaving equipment unattended.

While hybrid cloud-edge architectures have been widely proposed as the solution to these limitations, the existing literature reveals a critical gap: there is no empirically validated deployment of AWS IoT Core and AWS IoT Greengrass specifically for manufacturing predictive maintenance that reports measurable performance data across latency, bandwidth, and resilience. The theoretical advantages of the hybrid approach remain unsubstantiated by real infrastructure evidence for this domain.

This paper addresses that gap directly through a real AWS deployment.

---

## Research Objectives

This paper pursues four primary research objectives:

**RO1:** Design a hybrid cloud-edge architecture for industrial predictive maintenance using AWS IoT Core and AWS IoT Greengrass, integrating local ML inference at the edge with selective cloud synchronization.

**RO2:** Deploy and compare two configurations — a cloud-only baseline (Configuration A) and the proposed hybrid edge architecture (Configuration B) — on real AWS infrastructure, measuring latency, bandwidth consumption, ML inference accuracy, and system uptime.

**RO3:** Demonstrate and quantify the resilience advantage of the proposed architecture by disconnecting the Greengrass gateway from the cloud and measuring operational continuity of local ML inference.

**RO4:** Provide a practical, reproducible deployment framework using AWS services that industrial practitioners can adapt for real-world IIoT predictive maintenance applications.

---

## Research Questions

- **RQ1:** By what margin does local ML inference at the Greengrass edge reduce end-to-end decision latency compared to cloud-only inference under the same AWS infrastructure?
- **RQ2:** What percentage reduction in cloud-bound bandwidth consumption is achieved through selective edge synchronization compared to full raw data forwarding to the cloud?
- **RQ3:** To what extent does the hybrid edge architecture maintain ML inference accuracy and operational continuity during periods of cloud disconnection?
