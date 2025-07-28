#!/bin/bash

# Quick Deploy Script for Lottery Application on TransIP Kubernetes
# This script automates the deployment process

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN=${1:-"bynderlottery.online"}
REGISTRY=${2:-"registry.bynderlottery.online"}
NAMESPACE="lottery"

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

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        print_error "helm is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "docker is not installed"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        print_error "kubectl is not configured or cluster is not accessible"
        exit 1
    fi
    
    print_success "All prerequisites are met"
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    
    # Add Helm repositories
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    # Install cert-manager
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --set installCRDs=true \
        --wait
    
    # Create ClusterIssuer
    kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@$DOMAIN
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
    
    # Install NGINX Ingress Controller
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --wait
    
    # Install PostgreSQL
    helm install postgres bitnami/postgresql \
        --namespace $NAMESPACE \
        --create-namespace \
        --set auth.postgresPassword=rxgcrsabhfxtuiuk \
        --set auth.database=myproject \
        --set auth.username=janedoe \
        --wait
    
    # Install Redis
    helm install redis bitnami/redis \
        --namespace $NAMESPACE \
        --set auth.enabled=false \
        --wait
    
    print_success "Dependencies installed"
}

# Build and push images
build_images() {
    print_step "Building and pushing Docker images..."
    
    # Build images
    docker build -t $REGISTRY/lottery-backend:latest backend/
    docker build -t $REGISTRY/lottery-frontend:latest frontend/
    
    # Push images
    docker push $REGISTRY/lottery-backend:latest
    docker push $REGISTRY/lottery-frontend:latest
    
    print_success "Images built and pushed"
}

# Update configuration files
update_config() {
    print_step "Updating configuration files..."
    
    # Update domain in configmaps
    sed -i.bak "s/yourdomain.com/$DOMAIN/g" k8s/configmaps.yaml
    
    # Update registry in deployments
    sed -i.bak "s|your-registry|$REGISTRY|g" k8s/deployments.yaml
    sed -i.bak "s|your-registry|$REGISTRY|g" helm-chart/values.yaml
    
    # Update domain in ingress
    sed -i.bak "s/yourdomain.com/$DOMAIN/g" k8s/ingress.yaml
    
    print_success "Configuration updated"
}

# Deploy application
deploy_application() {
    print_step "Deploying application..."
    
    # Create namespace
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply secrets and configmaps
    kubectl apply -f k8s/secrets.yaml
    kubectl apply -f k8s/configmaps.yaml
    
    # Deploy application
    kubectl apply -f k8s/deployments.yaml
    kubectl apply -f k8s/services.yaml
    kubectl apply -f k8s/ingress.yaml
    kubectl apply -f k8s/hpa.yaml
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/lottery-backend -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=300s deployment/lottery-frontend -n $NAMESPACE
    
    print_success "Application deployed"
}

# Show deployment status
show_status() {
    print_step "Deployment Status:"
    
    echo ""
    echo "Pods:"
    kubectl get pods -n $NAMESPACE
    
    echo ""
    echo "Services:"
    kubectl get services -n $NAMESPACE
    
    echo ""
    echo "Ingress:"
    kubectl get ingress -n $NAMESPACE
    
    echo ""
    echo "External IP:"
    kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
    
    echo ""
    print_warning "Don't forget to:"
    echo "1. Update your DNS A record to point to the external IP above"
    echo "2. Wait for SSL certificate to be issued (can take a few minutes)"
    echo "3. Test your application at https://$DOMAIN"
}

# Main deployment function
main() {
    echo "🚀 Lottery Application Kubernetes Deployment"
    echo "=========================================="
    echo "Domain: $DOMAIN"
    echo "Registry: $REGISTRY"
    echo "Namespace: $NAMESPACE"
    echo ""
    
    check_prerequisites
    install_dependencies
    build_images
    update_config
    deploy_application
    show_status
    
    echo ""
    print_success "Deployment completed! 🎉"
}

# Show usage
usage() {
    echo "Usage: $0 [DOMAIN] [REGISTRY]"
    echo ""
    echo "Arguments:"
    echo "  DOMAIN     Your domain name (default: bynderlottery.online)"
    echo "  REGISTRY   Your container registry (default: registry.transip.nl/your-username)"
    echo ""
    echo "Examples:"
    echo "  $0 bynderlottery.online"
    echo "  $0 myapp.com registry.transip.nl/myusername"
}

# Check if help is requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
    exit 0
fi

# Run main function
main 
