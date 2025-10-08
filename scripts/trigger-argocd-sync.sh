#!/bin/bash

# Script to trigger ArgoCD sync after Docker image is built
# This script will be called from GitHub Action

set -e

# Configuration
ARGOCD_SERVER="argocd-server.argocd-new.svc.cluster.local"
ARGOCD_APP_NAME="django-api-app"
ARGOCD_NAMESPACE="argocd-new"

# Get ArgoCD token from secret
ARGOCD_TOKEN="${ARGOCD_TOKEN:-}"

if [ -z "$ARGOCD_TOKEN" ]; then
    echo "Error: ARGOCD_TOKEN environment variable is required"
    exit 1
fi

echo "Triggering ArgoCD sync for application: $ARGOCD_APP_NAME"

# Method 1: Try to use kubectl to trigger sync (if running in cluster)
if command -v kubectl &> /dev/null; then
    echo "Using kubectl to trigger ArgoCD sync..."
    kubectl patch application $ARGOCD_APP_NAME -n $ARGOCD_NAMESPACE \
        --type merge \
        -p '{"operation":{"sync":{"syncOptions":["CreateNamespace=true","PrunePropagationPolicy=foreground"]}}}' \
        || echo "kubectl sync failed, trying alternative method..."
fi

# Method 2: Use ArgoCD CLI
if command -v argocd &> /dev/null; then
    echo "Using ArgoCD CLI to trigger sync..."
    argocd app sync $ARGOCD_APP_NAME \
        --server $ARGOCD_SERVER \
        --auth-token $ARGOCD_TOKEN \
        --prune \
        --force \
        || echo "ArgoCD CLI sync failed"
fi

# Method 3: Use curl to call ArgoCD API
echo "Using curl to call ArgoCD API..."
curl -X POST \
    -H "Authorization: Bearer $ARGOCD_TOKEN" \
    -H "Content-Type: application/json" \
    "http://$ARGOCD_SERVER/api/v1/applications/$ARGOCD_APP_NAME/sync" \
    -d '{
        "prune": true,
        "dryRun": false,
        "syncOptions": ["CreateNamespace=true", "PrunePropagationPolicy=foreground"]
    }' \
    || echo "ArgoCD API sync failed"

echo "ArgoCD sync trigger completed"
