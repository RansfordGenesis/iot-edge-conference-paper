# Paper Contribution Statements

This paper makes the following three contributions to the field of Industrial Internet of Things and edge computing:

**C1 — Validated AWS Greengrass Deployment for Manufacturing PdM:**
We provide an empirically validated deployment of AWS IoT Greengrass v2 as an edge inference runtime for manufacturing predictive maintenance, extending the JANUS benchmark findings (Shankar et al., 2020) to the time-series ML domain and reporting CloudWatch-measured performance metrics from a working Greengrass ML component running on real AWS infrastructure.

**C2 — Quantified Resilience Under Cloud Disconnection:**
We measure, in a real deployed AWS environment, the system uptime, alert continuity, and data queuing behavior of a Greengrass-based hybrid edge architecture during a real cloud disconnection event, providing concrete evidence for the resilience advantage that the literature has thus far only theorized.

**C3 — Practical Deployment Framework:**
We provide a reproducible architecture and deployment framework using AWS IoT Core, Greengrass v2, and SageMaker that industrial practitioners and researchers can adapt for real-world IIoT predictive maintenance deployments, including the federated learning workflow pathway for future MLOps loop closure at the edge.
