#!/usr/bin/env bash
# setup-localstack.sh
# Starts LocalStack and bootstraps the S3 bucket + DynamoDB table
# needed for Terraform remote state.
set -euo pipefail

LOCALSTACK_ENDPOINT="http://localhost:4566"
STATE_BUCKET="tf-state-provisioner"
LOCK_TABLE="terraform-lock"
REGION="eu-west-1"

AWS_CMD="aws --endpoint-url ${LOCALSTACK_ENDPOINT} --region ${REGION} \
  --no-verify-ssl \
  --output text"

echo "==> Starting LocalStack via docker-compose..."
docker compose up -d localstack

echo "==> Waiting for LocalStack to be ready..."
until curl -sf "${LOCALSTACK_ENDPOINT}/_localstack/health" | grep -q '"s3": "available"'; do
  echo "    ...waiting"
  sleep 3
done
echo "    LocalStack is ready."

echo "==> Creating Terraform state S3 bucket: ${STATE_BUCKET}"
${AWS_CMD} s3api create-bucket \
  --bucket "${STATE_BUCKET}" \
  --create-bucket-configuration LocationConstraint="${REGION}" 2>/dev/null || echo "    Bucket already exists, skipping."

# echo "==> Enabling versioning on state bucket..."
# ${AWS_CMD} s3api put-bucket-versioning \
#   --bucket "${STATE_BUCKET}" \
#   --versioning-configuration Status=Enabled

echo "==> Creating DynamoDB lock table: ${LOCK_TABLE}"
${AWS_CMD} dynamodb create-table \
  --table-name "${LOCK_TABLE}" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST 2>/dev/null || echo "    Table already exists, skipping."

echo ""
echo "✅  LocalStack bootstrap complete."
echo "    S3 state bucket : ${STATE_BUCKET}"
echo "    DynamoDB table  : ${LOCK_TABLE}"
echo "    Endpoint        : ${LOCALSTACK_ENDPOINT}"
