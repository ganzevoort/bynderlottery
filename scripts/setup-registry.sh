#!/bin/bash

# Setup Docker Registry for TransIP Kubernetes
# Based on TransIP documentation

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
REGISTRY_USERNAME=${1:-"lottery"}
REGISTRY_PASSWORD=${2:-"lottery-secure-password-2024"}
REGISTRY_DOMAIN="registry.bynderlottery.online"

print_step "Setting up Docker Registry for TransIP Kubernetes"

# Step 1: Generate password file
print_step "Generating authentication password file..."
htpasswd -nB $REGISTRY_USERNAME | tee registry.htpasswd

# Step 2: Create namespace
print_step "Creating docker-registry namespace..."
kubectl create namespace docker-registry --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Create secret for authentication
print_step "Creating authentication secret..."
kubectl create secret generic registry-auth-secret \
  --from-file=users=registry.htpasswd \
  -n docker-registry \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 4: Deploy registry
print_step "Deploying Docker registry..."
kubectl apply -f k8s/registry-deployment.yaml

# Step 5: Wait for deployment
print_step "Waiting for registry to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/docker-registry-deployment -n docker-registry

# Step 6: Get external IP
print_step "Getting external IP..."
EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$EXTERNAL_IP" ]; then
    print_warning "External IP not available yet. Please check later with:"
    echo "kubectl get service ingress-nginx-controller -n ingress-nginx"
else
    print_success "External IP: $EXTERNAL_IP"
fi

print_success "Docker Registry setup complete!"
echo ""
echo "Registry Details:"
echo "  URL: https://$REGISTRY_DOMAIN"
echo "  Username: $REGISTRY_USERNAME"
echo "  Password: $REGISTRY_PASSWORD"
echo ""
echo "Next steps:"
echo "1. Add DNS A record: registry.bynderlottery.online -> $EXTERNAL_IP"
echo "2. Wait for SSL certificate (can take a few minutes)"
echo "3. Test login: docker login $REGISTRY_DOMAIN"
echo "4. Update deployment files with registry URL"
echo ""
echo "To check status:"
echo "  kubectl get pods -n docker-registry"
echo "  kubectl get ingress -n docker-registry"
