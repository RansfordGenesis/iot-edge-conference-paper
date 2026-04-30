# Conference Paper Project Plan
**Topic:** Edge Computing Optimization Using AWS IoT Core and Greengrass: Hybrid Cloud-Edge Architectures for Low-Latency Industrial IoT  
**Group 2:** Appiah Boadu | Kyei Baafi | Kofi Koranteng  
**Duration:** 4 Weeks (Month-Long Sprint to Conference Deadline)

---

## Member Roles & Strengths

| Member | Strength | Primary Role |
|---|---|---|
| **Appiah Boadu** | Research | Lead Researcher, ML Model Development, Results Analysis |
| **Kyei Baafi** | Cloud / AWS | Cloud Architect, AWS IoT Infrastructure, Deployment |
| **Kofi Koranteng** | Theory | Lead Writer, Theoretical Framework, Gap Analysis |

---

## Week 1 — Foundation: Literature Review, Gap Identification & Environment Setup
**Goal:** Everyone has a shared understanding of the problem space. AWS environment is live. Literature gaps are identified.

### Appiah Boadu
- [x] Collect 15–20 key papers on edge computing, hybrid cloud-edge IoT, and ML at the edge (IEEE Xplore, ACM, arXiv)
- [x] Annotate papers — highlight methods, datasets, architectures used, and weaknesses
- [x] Shortlist 8–10 most relevant papers to anchor the literature review
- [x] Investigate existing approaches and decide the deployment stack
- [x] Draft a rough technical architecture diagram of the proposed hybrid cloud-edge system

### Kyei Baafi
- [x] Activate and organize AWS environment — create a dedicated AWS account/project environment
- [x] Set up AWS IoT Core: create a Thing registry, certificates, and policies for edge devices
- [x] Explore AWS IoT Greengrass v2 — understand components, deployment model, and local ML inference pipeline
- [x] Research AWS services relevant to the project: SageMaker Edge, Kinesis Data Streams, S3, CloudWatch
- [x] Document the AWS architecture plan (which services connect to what and why)

### Kofi Koranteng
- [x] Review all annotated papers provided by Appiah Boadu
- [x] Identify 3–5 clear research gaps in existing literature (latency, bandwidth, ML edge deployment, resilience)
- [x] Draft the Problem Statement and Research Objectives section of the paper
- [x] Define the evaluation metrics the paper will use (latency, bandwidth savings, accuracy, uptime)
- [x] Begin drafting the paper skeleton: Abstract placeholder, Introduction outline, Section headings

---

## Week 2 — Design: Architecture Definition, Theoretical Framework & AWS Configuration
**Goal:** The hybrid architecture is fully designed on paper and in AWS. Theoretical contributions are clearly stated.

### Appiah Boadu
- [ ] Finalize the hybrid cloud-edge architecture design (edge node → local processing → Greengrass → AWS IoT Core → cloud analytics)
- [ ] Define the industrial scenario in detail: predictive maintenance on a manufacturing floor with vibration/temperature sensor data
- [ ] Design the ML model for predictive maintenance (anomaly detection / failure prediction) — decide on model type (LSTM or random forest for edge deployment)
- [ ] Set up the deployment configuration: number of devices, data rate, network conditions (latency, bandwidth thresholds)

### Kyei Baafi
- [x] Deploy AWS IoT Greengrass v2 on a local machine or EC2 instance acting as an edge gateway
- [x] Configure Greengrass components: local MQTT broker, stream manager, and ML inference component
- [x] Connect IoT devices (via AWS IoT Device SDK) to Greengrass
- [x] Set up AWS IoT Core rules engine to route edge data to S3 and CloudWatch for analysis
- [x] Test basic end-to-end data flow: device → Greengrass edge → AWS IoT Core → S3

### Kofi Koranteng
- [x] Write the full Related Work / Literature Review section (2–3 pages) using Appiah's annotated papers
- [x] Write the Research Gaps section — clearly articulate what existing work has NOT addressed
- [x] Draft the Theoretical Framework / Proposed Approach section — describe the hybrid architecture conceptually and its advantages
- [x] Define the paper's contribution statements (what this paper adds to the field)
- [x] Start the Methodology section outline — how the deployment validates the theoretical claims

---

## Week 3 — Execution: ML Deployment, Measurements & Paper Body
**Goal:** ML model is deployed at the edge. Real measurements are captured. Core paper sections are written.

### Appiah Boadu
- [ ] Run Configuration A: connect device directly to AWS IoT Core — measure latency and bandwidth
- [ ] Run Configuration B: connect device through Greengrass edge — measure the same metrics
- [ ] Train the ML predictive maintenance model on sample industrial data (NASA CMAPSS dataset or similar open dataset)
- [ ] Export and optimize the trained model for edge deployment (ONNX or TensorFlow Lite)
- [ ] Begin capturing results: latency comparisons, bandwidth reduction percentages, inference accuracy

### Kyei Baafi
- [ ] Deploy the ML inference component on AWS Greengrass using SageMaker Edge Manager or a custom Greengrass ML component
- [ ] Configure local inference pipeline: device data in → edge ML model → local decision → alert or sync to cloud
- [ ] Implement bandwidth optimization: configure Greengrass stream manager to batch and compress data before cloud upload
- [ ] Set up CloudWatch dashboards to monitor: messages per second, latency, data transferred, inference time
- [ ] Test resilience: disconnect edge from cloud, verify local processing continues (offline mode test)
- [ ] Capture AWS-side results: bandwidth usage before vs. after edge filtering, cloud compute load reduction

### Kofi Koranteng
- [ ] Write the full Methodology section — describe the deployment setup, configurations A and B, evaluation approach
- [ ] Write the System Design / Architecture section — describe the hybrid architecture components with reference to Appiah's diagram
- [ ] Draft the Results and Discussion section skeleton — prepare tables/figures placeholders for results
- [ ] Ensure academic writing quality: formal tone, proper citations (IEEE format), no informal language
- [ ] Compile a reference list (target 20–25 properly formatted references)

---

## Week 4 — Integration, Results & Final Paper Polish
**Goal:** All results are in. Paper is complete, reviewed, and submission-ready.

### Appiah Boadu
- [ ] Finalize all results — generate clean plots/figures (latency comparison, bandwidth savings, ML accuracy)
- [ ] Integrate AWS CloudWatch results into a unified results narrative
- [ ] Review the complete paper for technical accuracy — verify all claims match the deployment output
- [ ] Prepare technical figures for the paper (architecture diagram, results graphs)
- [ ] Conduct a final proofread of all technical sections

### Kyei Baafi
- [ ] Write the AWS Implementation section of the paper — detail the Greengrass setup, IoT Core configuration, and cloud pipeline
- [ ] Finalize and clean up CloudWatch dashboards — export screenshots/data for the paper's results section
- [ ] Write the Cloud-Edge Integration subsection — how AWS services work together in the proposed architecture
- [ ] Document limitations of the AWS setup and note what would differ in a real industrial deployment
- [ ] Assist Appiah with combining results into the Results section
- [ ] Review the full paper for cloud-related accuracy

### Kofi Koranteng
- [ ] Fill in the Results and Discussion section with actual AWS deployment data
- [ ] Write the Conclusion section — restate problem, summarize findings, state contributions, suggest future work
- [ ] Write/finalize the Abstract (250–300 words: problem, approach, key results, contribution)
- [ ] Polish the Introduction to properly set up the problem and preview the paper's structure
- [ ] Ensure full IEEE conference paper formatting compliance (2-column layout, font sizes, section headers)
- [ ] Compile final submission package — full paper PDF, figures, author info

---

## Shared Milestones & Checkpoints

| Milestone | Target Date | Owner |
|---|---|---|
| Paper skeleton + AWS account live | End of Week 1 | All |
| Architecture finalized (diagram + AWS) | End of Week 2 | Appiah + Kyei |
| Literature review section done | End of Week 2 | Kofi |
| ML model deployed on Greengrass | Mid Week 3 | Kyei |
| Both configurations measured (A + B) | Mid Week 3 | Appiah |
| Full paper draft (all sections) | End of Week 3 | Kofi leads, All contribute |
| Results integrated into paper | Day 1–2, Week 4 | Appiah + Kyei |
| Final paper review pass | Day 3–4, Week 4 | All |
| Submission-ready PDF | End of Week 4 | Kofi finalizes |

---

## Key Deliverables

1. **Research Paper** — IEEE-formatted conference paper covering: abstract, introduction, related work, research gaps, proposed architecture, methodology, results, discussion, conclusion
2. **AWS Deployment** — Functional AWS IoT Core + Greengrass setup with ML inference at the edge and CloudWatch monitoring
3. **Figures & Diagrams** — Architecture diagram, results plots (latency, bandwidth, ML accuracy)

---

## Deployment Configuration Summary

**Setting:** A manufacturing predictive maintenance scenario with IoT devices publishing vibration and temperature readings.

**Configuration A (Baseline — Cloud-Only):** All raw device data forwarded directly to AWS IoT Core → cloud ML inference. Measure: higher latency, higher bandwidth consumption.

**Configuration B (Proposed — Hybrid Edge):** Devices connect to an AWS Greengrass edge gateway. ML inference runs locally. Only anomaly alerts and compressed summaries sync to cloud. Measure: lower latency, reduced bandwidth, maintained inference accuracy.

**Expected Results:** Configuration B shows 40–70% bandwidth reduction, sub-100ms local inference latency (vs. 300–800ms cloud round-trip), and sustained operation during cloud disconnection.

---

## Tools & Resources

| Tool | Purpose |
|---|---|
| AWS IoT Core | Cloud MQTT broker, device registry, rules engine |
| AWS IoT Greengrass v2 | Edge runtime, local ML inference, stream manager |
| AWS SageMaker / SageMaker Edge | ML model training and edge deployment |
| AWS CloudWatch | Monitoring latency, bandwidth, and inference metrics |
| AWS IoT Device SDK (Python) | Test device connecting to Greengrass for measurements |
| NASA CMAPSS Dataset | Open industrial sensor dataset for ML model training |
| Overleaf (LaTeX) | IEEE-format collaborative paper writing |
| IEEE Xplore / ACM DL / arXiv | Literature sources |
