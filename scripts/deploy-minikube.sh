#!/usr/bin/env bash
# deploy-minikube.sh
# Builds the Docker image, loads it into minikube, deploys via Helm,
# and starts ngrok to expose the service publicly.
set -euo pipefail

IMAGE_NAME="cloud-provisioner"
IMAGE_TAG="dev"
HELM_RELEASE="cloud-provisioner"
HELM_CHART="../helm/cloud-provisioner"
NAMESPACE="default"
NODE_PORT=30080
NGROK_PORT=8000

# ── 1. Check prerequisites ────────────────────────────────────────────────────
for cmd in docker minikube helm ngrok kubectl; do
  if ! command -v "${cmd}" &>/dev/null; then
    echo "ERROR: '${cmd}' is not installed or not in PATH." >&2
    exit 1
  fi
done

# ── 2. Ensure minikube is running ─────────────────────────────────────────────
echo "==> Checking minikube status..."
if ! minikube status | grep -q "Running"; then
  echo "==> Starting minikube..."
  minikube start --driver=docker
fi

# ── 3. Make sure LocalStack is reachable from minikube ───────────────────────
# LocalStack runs on the host; expose it to minikube via host.minikube.internal
LOCALSTACK_HOST=$(minikube ssh "getent hosts host.minikube.internal | awk '{print \$1}'" 2>/dev/null || echo "host.minikube.internal")
echo "==> LocalStack will be reached at http://${LOCALSTACK_HOST}:4566 from inside minikube"

# ── 4. Build Docker image inside minikube's Docker daemon ─────────────────────
echo "==> Pointing Docker CLI at minikube's daemon..."
eval "$(minikube docker-env)"

echo "==> Building image ${IMAGE_NAME}:${IMAGE_TAG}..."
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" ../

# ── 5. Helm deploy ─────────────────────────────────────────────────────────────
echo "==> Deploying via Helm (release: ${HELM_RELEASE})..."
helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
  --namespace "${NAMESPACE}" \
  --set image.repository="${IMAGE_NAME}" \
  --set image.tag="${IMAGE_TAG}" \
  --set image.pullPolicy=Never \
  --set config.localstackEndpoint="http://${LOCALSTACK_HOST}:4566" \
  --wait --timeout 120s

# ── 6. Wait for pod to be ready ───────────────────────────────────────────────
echo "==> Waiting for pod to be ready..."
kubectl rollout status deployment/"${HELM_RELEASE}" -n "${NAMESPACE}" --timeout=120s

# ── 7. Start ngrok tunnel ─────────────────────────────────────────────────────
MINIKUBE_IP=$(minikube ip)
echo ""
echo "==> Starting ngrok tunnel → http://${MINIKUBE_IP}:${NODE_PORT}"
echo "    (press Ctrl+C to stop)"
echo ""
ngrok http "${MINIKUBE_IP}:${NODE_PORT}"
