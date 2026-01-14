#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="mockapi-test-cluster"
IMAGE_NAME="mockapi-tests"
POD_NAME="mockapi-test-pod"
CONFIGMAP_NAME="mockapi-env"

echo "🚀 Starting Kubernetes test run..."

# -----------------------------
# Preconditions
# -----------------------------
command -v kind >/dev/null || { echo "❌ kind not installed"; exit 1; }
command -v kubectl >/dev/null || { echo "❌ kubectl not installed"; exit 1; }
command -v docker >/dev/null || { echo "❌ docker not installed"; exit 1; }

if [ ! -f ".env" ]; then
  echo "❌ .env file not found (BASE_URL, API_TOKEN required)"
  exit 1
fi

# -----------------------------
# Create cluster (idempotent)
# -----------------------------
if ! kind get clusters | grep -q "$CLUSTER_NAME"; then
  echo "🔧 Creating kind cluster: $CLUSTER_NAME"
  kind create cluster --name "$CLUSTER_NAME"
else
  echo "✅ Cluster already exists: $CLUSTER_NAME"
fi

kubectl cluster-info --context "kind-$CLUSTER_NAME"

# -----------------------------
# Build Docker image
# -----------------------------
echo "🐳 Building Docker image..."
docker build -t "$IMAGE_NAME" -f ci/Dockerfile .

# -----------------------------
# Load image into kind
# -----------------------------
echo "📦 Loading image into kind..."
kind load docker-image "$IMAGE_NAME:latest" --name "$CLUSTER_NAME"

# -----------------------------
# Create / update ConfigMap
# -----------------------------
echo "🔐 Creating ConfigMap from .env..."
kubectl delete configmap "$CONFIGMAP_NAME" --ignore-not-found
kubectl create configmap "$CONFIGMAP_NAME" --from-env-file=.env

# -----------------------------
# Run test pod
# -----------------------------
echo "▶️ Running test pod..."
kubectl delete pod "$POD_NAME" --ignore-not-found
kubectl apply -f ci/mockapi_test_pod.yaml

# -----------------------------
# Stream logs
# -----------------------------
echo "📜 Streaming logs..."
kubectl wait --for=condition=Ready pod/"$POD_NAME" --timeout=60s || true
kubectl logs -f "$POD_NAME" || true

# -----------------------------
# Final pod state
# -----------------------------
echo "📊 Final pod status:"
kubectl get pod "$POD_NAME"

echo "✅ Kubernetes test run finished"
