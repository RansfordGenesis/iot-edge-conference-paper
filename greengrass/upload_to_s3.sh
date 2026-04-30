#!/bin/bash
# Run from your LOCAL machine to upload all scripts to S3
# Then SSH/SSM into EC2 and run deploy_ml_component.sh

ACCOUNT_ID="195275654331"
REGION="us-east-1"
BUCKET="iiot-edge-${ACCOUNT_ID}-${REGION}"
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Uploading scripts to s3://${BUCKET}/scripts/ ..."

# Training script
aws s3 cp "${PROJECT_ROOT}/ml/train_model.py" \
  "s3://${BUCKET}/scripts/train_model.py" --region $REGION

# Inference component
aws s3 cp "${SCRIPT_DIR}/components/com.iiot.MLInference/artifacts/inference.py" \
  "s3://${BUCKET}/scripts/inference.py" --region $REGION

# Component recipe
aws s3 cp "${SCRIPT_DIR}/components/com.iiot.MLInference/recipe.yaml" \
  "s3://${BUCKET}/scripts/recipe.yaml" --region $REGION

# Measurement scripts
aws s3 cp "${PROJECT_ROOT}/measurements/config_a_measurement.py" \
  "s3://${BUCKET}/scripts/config_a_measurement.py" --region $REGION

aws s3 cp "${PROJECT_ROOT}/measurements/config_b_measurement.py" \
  "s3://${BUCKET}/scripts/config_b_measurement.py" --region $REGION

aws s3 cp "${PROJECT_ROOT}/measurements/analyze_results.py" \
  "s3://${BUCKET}/scripts/analyze_results.py" --region $REGION

# Deploy script itself
aws s3 cp "${SCRIPT_DIR}/deploy_ml_component.sh" \
  "s3://${BUCKET}/scripts/deploy_ml_component.sh" --region $REGION

echo ""
echo "Done. Now on EC2 (SSM session), run:"
echo "  aws s3 cp s3://${BUCKET}/scripts/deploy_ml_component.sh /tmp/deploy.sh --region ${REGION}"
echo "  chmod +x /tmp/deploy.sh && /tmp/deploy.sh"
