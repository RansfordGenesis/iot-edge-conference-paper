# AWS Implementation

## AWS IoT Greengrass v2 Deployment

### A. Infrastructure Provisioning

The edge gateway infrastructure is provisioned via an AWS CloudFormation stack (`iiot-stack.yaml`) that creates and configures all required resources in a single declarative deployment. The stack includes:

- **Amazon EC2 instance** (t3.small, Amazon Linux 2): The Greengrass host, provisioned with a UserData script that installs Java 11 (Amazon Corretto), downloads and runs the Greengrass Nucleus installer, and configures the system sudoers policy required for Greengrass to launch components under the `ggc_user:ggc_group` identity.
- **IAM Role (`GreengrassEC2Role`)**: Attached to the EC2 instance profile, granting permissions for IoT Core provisioning (`iot:*`), Greengrass component and deployment management (`greengrass:*`), S3 artifact access (`s3:GetObject`, `s3:PutObject`, `s3:ListBucket` on the artifacts bucket), and the IAM provisioning actions the Greengrass installer requires (`iam:GetPolicy`, `iam:CreatePolicy`, `iam:AttachRolePolicy`) to create its Token Exchange Service (TES) policy.
- **IoT Thing (`iiot-edge-gateway-01`)**: The logical representation of the gateway in IoT Core, used for certificate-based authentication.
- **S3 Bucket (`iiot-edge-{AccountId}-{Region}`)**: Stores Greengrass component artifacts (ONNX model, scaler pickle, inference script) and deployment scripts.
- **Security Group**: Allows outbound MQTT over TLS (port 8883) and HTTPS (port 443) to AWS service endpoints; inbound SSH (port 22) for administrative access.

The Greengrass Nucleus installer is invoked with `--provision true`, which automates certificate issuance, IoT Thing registration, and TES role alias creation. The Nucleus version pinned in the stack is 2.17.0.

### B. Greengrass Component Deployment

After Nucleus installation, three components are deployed via a Greengrass deployment targeting the edge device's thing group:

```
aws greengrassv2 create-deployment \
  --target-arn arn:aws:iot:us-east-1:{AccountId}:thinggroup/iiot-edge-gateways \
  --components '{
    "aws.greengrass.StreamManager": {"componentVersion": "2.3.0"},
    "aws.greengrass.Cli":           {"componentVersion": "2.17.0"},
    "com.iiot.MLInference":         {"componentVersion": "1.0.0"}
  }'
```

The `com.iiot.MLInference` component version is registered in the Greengrass component registry (`aws greengrassv2 create-component-version`) with a recipe (`recipe.yaml`) that specifies S3 artifact URIs, install lifecycle hooks, and run lifecycle commands. The install hook uses `pip3` to install `onnxruntime`, `numpy`, and `scikit-learn` on the device; the run hook launches the inference script with environment variables pointing to the artifacts directory and the configured batch size.

Component deployment status is verified via `greengrass-cli component list` on the device, confirming all three components reach the `RUNNING` state. Greengrass component logs are available at `/greengrass/v2/logs/com.iiot.MLInference.log` on the gateway and streamed to CloudWatch Logs under the log group `/aws/greengrass/GreengrassSystemComponent`.

### C. IoT Core Topic Architecture

Messages flow through four MQTT topic paths:

| Topic | Publisher | Consumer | Content |
|---|---|---|---|
| `iiot/edge/machine-01/telemetry` | Test client (Config A only) | IoT Core Rules Engine | Raw sensor reading (all 14 channels) |
| `iiot/edge/machine-01/alerts` | ML Inference component (via IPC) | IoT Core → Stream Manager | Anomaly alert with 2 key sensor values |
| `iiot/edge/machine-01/batch` | ML Inference component (via IPC) | IoT Core → Stream Manager | Compressed batch summary (per-sensor means) |
| `iiot/edge/#` | Test client (Config B) | ML Inference component (via IPC) | Raw sensor reading for local classification |

In Configuration B, the test client publishes to the local Greengrass IPC broker rather than directly to IoT Core. The `com.iiot.MLInference` component's IPC subscription on `iiot/edge/#` intercepts each reading before it leaves the device. Only the inference component's output topics (`alerts`, `batch`) reach IoT Core, and only after classification determines they should be forwarded.

All MQTT connections use mutual TLS with X.509 certificates issued by the AWS IoT Certificate Authority. QoS 1 (AT_LEAST_ONCE delivery) is used for all published messages to ensure delivery guarantees under transient network interruptions.

### D. Stream Manager Configuration

AWS IoT Greengrass Stream Manager (v2.3.0) provides the guaranteed-delivery buffer between the inference component and IoT Core. The inference component publishes batch summaries to a Stream Manager stream; Stream Manager handles export retry, backpressure, and offline queuing automatically. During a cloud disconnection event, Stream Manager buffers outgoing messages locally and exports them in order upon reconnection, ensuring no alert or summary data is lost during intermittent connectivity — a critical property for industrial deployments where cellular or industrial WAN links are subject to scheduled maintenance windows and coverage gaps.

Stream Manager is configured with default export parameters for the research deployment; production deployments would tune the export batch size, priority levels (anomaly alerts vs. batch summaries), and maximum queue size to match available on-device storage.

### E. Artifact Staging and Component Registration

ML artifacts are staged to S3 before component deployment using a shell script (`upload_to_s3.sh`) that uploads three files to `s3://iiot-edge-{AccountId}-{Region}/greengrass-artifacts/com.iiot.MLInference/1.0.0/`:

- `pdm_model.onnx` — Trained Random Forest in ONNX format (6.1 MB)
- `scaler.pkl` — Fitted StandardScaler for feature normalization
- `inference.py` — Greengrass IPC inference component runtime

The component recipe references these artifacts by S3 URI. When Greengrass deploys the component to the device, it downloads the artifacts from S3 (using the EC2 instance's IAM role for access), verifies integrity, and places them in the component's artifacts directory (`/greengrass/v2/packages/artifacts/com.iiot.MLInference/1.0.0/`). The inference script references artifacts via the `{artifacts:path}` recipe variable, which Greengrass resolves to the local path at runtime.
