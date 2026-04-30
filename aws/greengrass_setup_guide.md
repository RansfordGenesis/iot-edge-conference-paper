# AWS IoT Core + Greengrass v2 Setup Guide
**Owner: Kyei Baafi**

This guide covers the complete AWS setup for the hybrid cloud-edge deployment. Follow sections in order.

---

## Step 1: AWS Account & IAM Setup

```bash
# Install AWS CLI if not already installed
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# Configure with your credentials and region
aws configure
# AWS Access Key ID: [from IAM]
# AWS Secret Access Key: [from IAM]
# Default region: us-east-1
# Default output format: json

# Create a dedicated IAM role for Greengrass
aws iam create-role \
  --role-name GreengrassV2TokenExchangeRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "credentials.iot.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach required policies
aws iam attach-role-policy \
  --role-name GreengrassV2TokenExchangeRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam attach-role-policy \
  --role-name GreengrassV2TokenExchangeRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

---

## Step 2: AWS IoT Core — Thing Registry, Certificates & Policies

```bash
# Create a Thing for the edge gateway
aws iot create-thing --thing-name "iiot-edge-gateway-01"

# Create a Thing Group for all edge devices
aws iot create-thing-group --thing-group-name "ManufacturingFloorEdgeDevices"

# Add the gateway to the group
aws iot add-thing-to-thing-group \
  --thing-group-name ManufacturingFloorEdgeDevices \
  --thing-name iiot-edge-gateway-01

# Create X.509 certificate (saves cert + private key)
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile "device-cert.pem" \
  --public-key-outfile "public.key" \
  --private-key-outfile "private.key"

# Note the certificateArn from the output — needed below
CERT_ARN=$(aws iot create-keys-and-certificate --set-as-active \
  --query 'certificateArn' --output text)

# Create IoT Policy
aws iot create-policy \
  --policy-name "GreengrassEdgePolicy" \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["iot:*", "greengrass:*"],
        "Resource": "*"
      }
    ]
  }'

# Attach policy to certificate
aws iot attach-policy \
  --policy-name GreengrassEdgePolicy \
  --target $CERT_ARN

# Attach certificate to Thing
aws iot attach-thing-principal \
  --thing-name iiot-edge-gateway-01 \
  --principal $CERT_ARN
```

---

## Step 3: Install AWS IoT Greengrass v2 on Edge Device

Run this on the machine acting as the edge gateway (local machine or EC2 instance):

```bash
# Download Greengrass installer
curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip \
  -o greengrass-nucleus-latest.zip
unzip greengrass-nucleus-latest.zip -d GreengrassInstaller

# Set your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"
THING_NAME="iiot-edge-gateway-01"

# Install Greengrass nucleus
sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE \
  -jar ./GreengrassInstaller/lib/Greengrass.jar \
  --aws-region $REGION \
  --thing-name $THING_NAME \
  --thing-group-name ManufacturingFloorEdgeDevices \
  --tes-role-name GreengrassV2TokenExchangeRole \
  --tes-role-alias-name GreengrassCoreTokenExchangeRoleAlias \
  --component-default-user ggc_user:ggc_group \
  --provision true \
  --setup-system-service true

# Verify Greengrass is running
sudo systemctl status greengrass
```

---

## Step 4: Configure Greengrass Components

### 4a — Local MQTT Broker (Moquette)

Create a Greengrass component recipe file `local-mqtt-broker.yaml`:

```yaml
RecipeFormatVersion: '2020-01-25'
ComponentName: com.example.LocalMqttBroker
ComponentVersion: '1.0.0'
ComponentDescription: Local MQTT broker for sensor devices
ComponentPublisher: IIoT-Research
ComponentDependencies:
  aws.greengrass.Nucleus:
    VersionRequirement: '>=2.0.0'
Manifests:
  - Platform:
      os: linux
    Lifecycle:
      Run: |
        java -jar {artifacts:path}/moquette-broker.jar
```

### 4b — Stream Manager (AWS-provided component)

Deploy via AWS Console: **Greengrass → Deployments → Add Component → aws.greengrass.StreamManager**

Or via CLI:
```bash
aws greengrassv2 create-deployment \
  --target-arn "arn:aws:iot:$REGION:$ACCOUNT_ID:thinggroup/ManufacturingFloorEdgeDevices" \
  --deployment-name "IIoTEdgeDeployment" \
  --components '{
    "aws.greengrass.StreamManager": {
      "componentVersion": "2.1.9"
    }
  }'
```

---

## Step 5: AWS IoT Core Rules Engine — Route to S3 and CloudWatch

```bash
# Create S3 bucket for data archiving
aws s3 mb s3://iiot-edge-conference-data --region $REGION

# Create IoT Rule: route all messages to S3
aws iot create-topic-rule \
  --rule-name "EdgeDataToS3" \
  --topic-rule-payload '{
    "sql": "SELECT * FROM '\''iiot/edge/+/telemetry'\''",
    "description": "Route edge telemetry to S3",
    "actions": [{
      "s3": {
        "roleArn": "arn:aws:iam::'"$ACCOUNT_ID"':role/GreengrassV2TokenExchangeRole",
        "bucketName": "iiot-edge-conference-data",
        "key": "${topic()}/${timestamp()}.json"
      }
    }],
    "ruleDisabled": false
  }'

# Create IoT Rule: route anomaly alerts to CloudWatch
aws iot create-topic-rule \
  --rule-name "AnomalyAlertsToCloudWatch" \
  --topic-rule-payload '{
    "sql": "SELECT * FROM '\''iiot/edge/+/alerts'\''",
    "description": "Route anomaly alerts to CloudWatch",
    "actions": [{
      "cloudwatchMetric": {
        "roleArn": "arn:aws:iam::'"$ACCOUNT_ID"':role/GreengrassV2TokenExchangeRole",
        "metricNamespace": "IIoT/EdgeAlerts",
        "metricName": "AnomalyCount",
        "metricValue": "1",
        "metricUnit": "Count"
      }
    }],
    "ruleDisabled": false
  }'
```

---

## Step 6: CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
  --dashboard-name "IIoT-Edge-Monitoring" \
  --dashboard-body '{
    "widgets": [
      {
        "type": "metric",
        "properties": {
          "title": "Edge-to-Cloud Latency (ms)",
          "metrics": [["IIoT/EdgeMetrics", "InferenceLatency"]],
          "period": 60, "stat": "Average"
        }
      },
      {
        "type": "metric",
        "properties": {
          "title": "Bytes Sent to Cloud",
          "metrics": [["AWS/IoT", "PublishIn.Success", "Protocol", "MQTT"]],
          "period": 60, "stat": "Sum"
        }
      },
      {
        "type": "metric",
        "properties": {
          "title": "Anomaly Alerts Count",
          "metrics": [["IIoT/EdgeAlerts", "AnomalyCount"]],
          "period": 60, "stat": "Sum"
        }
      }
    ]
  }'
```

---

## Step 7: End-to-End Test

Run this Python script to test a device publishing to Greengrass:

```python
# test_sensor_publish.py
# pip install awsiotsdk

from awsiot import mqtt_connection_builder
import json, time, random

ENDPOINT = "YOUR_IOT_ENDPOINT.iot.us-east-1.amazonaws.com"  # aws iot describe-endpoint --endpoint-type iot:Data-ATS
CLIENT_ID = "TestDevice-Machine-01"
CERT_PATH = "device-cert.pem"
KEY_PATH = "private.key"
CA_PATH = "AmazonRootCA1.pem"  # download from AWS

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=CERT_PATH,
    pri_key_filepath=KEY_PATH,
    ca_filepath=CA_PATH,
    client_id=CLIENT_ID,
)

connect_future = mqtt_connection.connect()
connect_future.result()
print("Connected to AWS IoT Core via Greengrass")

for i in range(100):
    payload = {
        "machine_id": "machine-01",
        "timestamp": time.time(),
        "vibration": round(random.gauss(0.5, 0.1), 4),
        "temperature": round(random.gauss(75.0, 5.0), 2)
    }
    mqtt_connection.publish(
        topic="iiot/edge/machine-01/telemetry",
        payload=json.dumps(payload),
        qos=1
    )
    print(f"Published: {payload}")
    time.sleep(0.1)  # 10 Hz

disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
```

Run: `python test_sensor_publish.py`

Verify in AWS Console: **IoT Core → Test → Subscribe to `iiot/edge/+/telemetry`** — messages should appear.

---

## AWS IoT Endpoint

Get your endpoint for the Python script:
```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text
```
