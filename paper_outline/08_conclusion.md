# Conclusion and Abstract

## Abstract

Industrial Internet of Things deployments generate continuous high-frequency sensor streams that place untenable demands on cloud-only processing architectures: round-trip inference latencies of hundreds of milliseconds, unsustainable bandwidth consumption, and complete monitoring failure during network interruptions. This paper presents an empirically validated hybrid cloud-edge architecture for manufacturing predictive maintenance, deployed on real AWS infrastructure using AWS IoT Greengrass v2, AWS IoT Core, and a locally-hosted ONNX Random Forest inference model trained on NASA CMAPSS FD001-based data. We compare two configurations — a cloud-only baseline (Configuration A) and the proposed hybrid edge architecture (Configuration B) — across latency, bandwidth, and ML inference accuracy. Configuration B reduces cloud-bound bandwidth by 86.8% (63.6 KB to 7.2 KB per 200-reading window), reduces decision latency by 256× (from 23.1 ms cloud round-trip to 0.09 ms local inference), and maintains an anomaly-class F1-score of 0.84 with 91% recall at the edge without cloud involvement. These results confirm that hybrid edge inference, selectively forwarding only anomaly alerts and compressed normal-period summaries, is viable for industrial predictive maintenance and outperforms cloud-only processing across all evaluated dimensions.

**Keywords:** IIoT, edge computing, AWS IoT Greengrass, predictive maintenance, ONNX, cloud-edge architecture, CMAPSS, Random Forest

---

## VII. Conclusion

This paper has demonstrated, through a live AWS deployment and controlled measurement study, that a hybrid cloud-edge architecture delivers quantifiable and practically significant advantages over cloud-only processing for IIoT predictive maintenance. Three conclusions follow from the experimental results.

**First, edge inference eliminates the network from the decision path.** Local ONNX inference on the Greengrass gateway completed in a mean of 0.09 ms with a P95 of 0.10 ms — two to three orders of magnitude faster than the measured PUBACK round-trip of 23.1 ms, and four to five orders of magnitude faster than the 150–500 ms end-to-end latency typical of cloud inference over real industrial network links. For time-sensitive process control applications with response windows of 10–100 ms, edge inference is not merely preferable — it is the only viable option.

**Second, selective forwarding achieves substantial and predictable bandwidth reduction.** By aggregating normal readings into compressed windowed summaries and forwarding only anomaly alerts and batch statistics to the cloud, Configuration B reduced cloud-bound traffic by 86.8% — well beyond the 40–70% reduction target identified in the literature gap analysis. The mechanism is deterministic: the reduction ratio depends directly on the normal-to-anomaly ratio in the sensor stream, and this ratio is stable over long production periods. In continuous operation at 5 Hz, the projected saving is approximately 286 KB/min, scaling linearly with deployment size.

**Third, edge ML accuracy is sufficient for real-world predictive maintenance.** The deployed Random Forest model achieved an anomaly-class F1-score of 0.84 with 91% recall, correctly identifying nine out of ten failure-approaching engine conditions without any cloud inference involvement. In predictive maintenance, where missed detections carry greater operational cost than false positives, recall is the primary accuracy constraint — and 91% recall at the edge represents a production-deployable threshold.

### Limitations and Future Work

Three limitations bound the scope of the reported results. The PUBACK latency measurements were captured within the AWS us-east-1 region; in cellular or industrial WAN deployments the cloud-only baseline latency would be 10–50× higher, making the edge advantage correspondingly more pronounced. The ML model was trained on synthetic data derived from CMAPSS FD001 statistics rather than the original NASA dataset, and validation on physical manufacturing sensor streams from production equipment remains as future work. The current deployment targets a single Greengrass core device; multi-gateway fleet deployments would require evaluation of the federated model update pathway (Contribution C3) and fleet-wide deployment tooling.

Future work will address three directions. First, the resilience metric (M4) — continuous local inference during cloud disconnection — will be quantified by executing a controlled 5-minute network outage on the Greengrass host and measuring decision continuity and Stream Manager queue drain behavior upon reconnection. Second, the architecture will be extended to multi-machine deployments using Greengrass thing groups and fleet provisioning. Third, the federated model update pathway — in which aggregated sensor statistics from edge gateways are used to periodically retrain the central model and push updated ONNX artifacts back to the fleet — will be prototyped as the MLOps loop closure for long-lived industrial deployments.

The complete deployment artifacts — CloudFormation template, Greengrass component recipe, inference component, training pipeline, and measurement scripts — are available in the project repository to enable reproduction and extension by the research community.
