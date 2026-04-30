#!/bin/bash
# ============================================================
#  IIoT ML Component — Full Deploy Script
#  Run this on the EC2 Greengrass instance via SSM session.
#  Installs deps, trains model, uploads to S3, creates and
#  deploys the com.iiot.MLInference Greengrass component.
# ============================================================
set -e

ACCOUNT_ID="195275654331"
REGION="us-east-1"
BUCKET="iiot-edge-${ACCOUNT_ID}-${REGION}"
COMPONENT="com.iiot.MLInference"
VERSION="1.0.0"
S3_PREFIX="greengrass-artifacts/${COMPONENT}/${VERSION}"
WORK_DIR="/tmp/iiot_ml"

echo "=============================================="
echo "  IIoT ML Component Deployment"
echo "  Bucket : s3://${BUCKET}"
echo "  Component: ${COMPONENT}:${VERSION}"
echo "=============================================="

# ── [1/6] Install Python dependencies ─────────────────────────────────────────
echo ""
echo "[1/6] Installing Python dependencies (training only)..."
pip3 install --quiet scikit-learn skl2onnx onnxruntime numpy pandas

# ── [2/6] Download project files from S3 ──────────────────────────────────────
echo ""
echo "[2/6] Downloading project files from S3..."
mkdir -p "$WORK_DIR"

aws s3 cp "s3://${BUCKET}/scripts/train_model.py"  "${WORK_DIR}/train_model.py"  --region $REGION
aws s3 cp "s3://${BUCKET}/scripts/inference.py"    "${WORK_DIR}/inference.py"    --region $REGION

# ── [3/6] Train model ──────────────────────────────────────────────────────────
echo ""
echo "[3/6] Training Random Forest on CMAPSS FD001..."
cd "$WORK_DIR"
python3 train_model.py

ls -lh "${WORK_DIR}/pdm_model.onnx" "${WORK_DIR}/scaler.pkl"

# ── [4/6] Upload model artifacts to S3 ────────────────────────────────────────
echo ""
echo "[4/6] Uploading artifacts to s3://${BUCKET}/${S3_PREFIX}/..."
aws s3 cp "${WORK_DIR}/pdm_model.onnx" "s3://${BUCKET}/${S3_PREFIX}/pdm_model.onnx" --region $REGION
aws s3 cp "${WORK_DIR}/scaler.pkl"     "s3://${BUCKET}/${S3_PREFIX}/scaler.pkl"     --region $REGION
aws s3 cp "${WORK_DIR}/inference.py"   "s3://${BUCKET}/${S3_PREFIX}/inference.py"   --region $REGION
echo "Artifacts uploaded."

# ── [5/6] Register Greengrass component ───────────────────────────────────────
echo ""
echo "[5/6] Registering ${COMPONENT} v${VERSION} in Greengrass..."
aws s3 cp "s3://${BUCKET}/scripts/recipe.yaml" "${WORK_DIR}/recipe.yaml" --region $REGION

# Read recipe and create component version
RECIPE_CONTENT=$(cat "${WORK_DIR}/recipe.yaml")
aws greengrassv2 create-component-version \
  --region "$REGION" \
  --inline-recipe fileb://"${WORK_DIR}/recipe.yaml"

echo "Component registered."

# ── [6/6] Deploy component to Greengrass ──────────────────────────────────────
echo ""
echo "[6/6] Deploying ${COMPONENT} to ManufacturingFloorEdgeDevices..."
aws greengrassv2 create-deployment \
  --region "$REGION" \
  --target-arn "arn:aws:iot:${REGION}:${ACCOUNT_ID}:thinggroup/ManufacturingFloorEdgeDevices" \
  --deployment-name "IIoT-EdgeDeployment-v5-MLInference" \
  --components "{
    \"aws.greengrass.StreamManager\": {
      \"componentVersion\": \"2.3.0\"
    },
    \"aws.greengrass.Cli\": {
      \"componentVersion\": \"2.17.0\"
    },
    \"${COMPONENT}\": {
      \"componentVersion\": \"${VERSION}\"
    }
  }"

echo ""
echo "=============================================="
echo "  Deployment submitted. Wait ~60s then run:"
echo "  sudo /greengrass/v2/bin/greengrass-cli component list"
echo "  Look for: ${COMPONENT} State: RUNNING"
echo "=============================================="
