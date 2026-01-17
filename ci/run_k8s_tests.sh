#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="mockapi-test-cluster"
IMAGE_NAME="mockapi-tests"
JOB_NAME="mockapi-test-job"
CONFIGMAP_NAME="mockapi-env"

echo "🚀 Starting Kubernetes test run..."

# -----------------------------
# Preconditions
# -----------------------------
command -v kind >/dev/null || { echo "❌ kind not installed"; exit 1; }
command -v kubectl >/dev/null || { echo "❌ kubectl not installed"; exit 1; }
command -v docker >/dev/null || { echo "❌ docker not installed"; exit 1; }

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
# Run test Job
# -----------------------------
echo "▶️ Running test Job..."
kubectl delete job "$JOB_NAME" --ignore-not-found
kubectl apply -f ci/mockapi_test_job.yaml

# -----------------------------
# Wait for Job completion
# -----------------------------
echo "⏳ Waiting for Job to finish..."
kubectl wait --for=condition=complete job/"$JOB_NAME" --timeout=300s || true

# -----------------------------
# Show logs from the Job pod
# -----------------------------
JOB_POD=$(kubectl get pods --selector=job-name="$JOB_NAME" -o jsonpath='{.items[0].metadata.name}')
echo "📜 Test logs from pod $JOB_POD:"
kubectl logs "$JOB_POD"

# -----------------------------
# Final result check
# -----------------------------
JOB_SUCCEEDED=$(kubectl get job "$JOB_NAME" -o jsonpath='{.status.succeeded}')

echo "📊 Job succeeded count: $JOB_SUCCEEDED"

if [ "$JOB_SUCCEEDED" != "1" ]; then
  echo "❌ Tests failed inside Kubernetes Job"
  kubectl describe job "$JOB_NAME"
  exit 1
fi

echo "✅ Kubernetes test run finished successfully"
