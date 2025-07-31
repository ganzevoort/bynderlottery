#!/bin/bash

# Lottery Application Kubernetes Deployment Script
# This script helps deploy the lottery application to a Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="lottery"
CHART_PATH="./helm-chart"
VALUES_FILE="./helm-chart/values.yaml"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if kubectl is configured
check_kubectl() {
    if ! kubectl cluster-info &> /dev/null; then
        print_error "kubectl is not configured or cluster is not accessible"
        exit 1
    fi
    print_status "kubectl is configured"
}

# Function to check if helm is installed
check_helm() {
    if ! command -v helm &> /dev/null; then
        print_error "helm is not installed"
        exit 1
    fi
    print_status "helm is installed"
}

# Function to create namespace
create_namespace() {
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        print_status "Creating namespace: $NAMESPACE"
        kubectl create namespace $NAMESPACE
    else
        print_status "Namespace $NAMESPACE already exists"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Helm repositories..."
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update

    print_status "Installing NGINX Ingress Controller..."
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer

    print_status "Installing PostgreSQL..."
    helm install postgres bitnami/postgresql \
        --namespace $NAMESPACE \
        --set auth.postgresPassword=rxgcrsabhfxtuiuk \
        --set auth.database=myproject \
        --set auth.username=janedoe

    print_status "Installing Redis..."
    helm install redis bitnami/redis \
        --namespace $NAMESPACE \
        --set auth.enabled=false
}

# Function to build and push Docker images
build_images() {
    print_status "Building Docker images..."

    # Build backend image
    docker build -t your-registry/lottery-backend:latest backend/

    # Build frontend image
    docker build -t your-registry/lottery-frontend:latest frontend/

    print_status "Pushing Docker images..."
    docker push your-registry/lottery-backend:latest
    docker push your-registry/lottery-frontend:latest
}

# Function to deploy application
deploy_application() {
    print_status "Deploying lottery application..."

    # Update values file with your domain
    if [ -n "$DOMAIN" ]; then
        sed -i "s/yourdomain.com/$DOMAIN/g" $VALUES_FILE
    fi

    # Deploy using Helm
    helm install lottery $CHART_PATH \
        --namespace $NAMESPACE \
        --values $VALUES_FILE
}

# Function to check deployment status
check_status() {
    print_status "Checking deployment status..."
    kubectl get pods -n $NAMESPACE
    kubectl get services -n $NAMESPACE
    kubectl get ingress -n $NAMESPACE
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy the complete application"
    echo "  build      Build and push Docker images"
    echo "  status     Check deployment status"
    echo "  delete     Delete the deployment"
    echo ""
    echo "Options:"
    echo "  -d, --domain DOMAIN    Set the domain name for the application"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy -d lottery.example.com"
    echo "  $0 build"
    echo "  $0 status"
}

# Function to delete deployment
delete_deployment() {
    print_warning "Deleting lottery deployment..."
    helm uninstall lottery -n $NAMESPACE
    helm uninstall postgres -n $NAMESPACE
    helm uninstall redis -n $NAMESPACE
    helm uninstall ingress-nginx -n ingress-nginx
    kubectl delete namespace $NAMESPACE
    kubectl delete namespace ingress-nginx
}

# Main script
main() {
    case $1 in
        deploy)
            check_kubectl
            check_helm
            create_namespace
            install_dependencies
            build_images
            deploy_application
            check_status
            ;;
        build)
            build_images
            ;;
        status)
            check_status
            ;;
        delete)
            delete_deployment
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Run main function
main $COMMAND
