# Lottery Application - Kubernetes Deployment

This directory contains all the necessary Kubernetes manifests and Helm charts to deploy the lottery application on a Kubernetes cluster.

## Architecture

The application consists of:

- **Nginx Ingress Controller**: Routes traffic to frontend and backend
- **Frontend (Next.js)**: React application
- **Backend (Django)**: API and admin interface
- **PostgreSQL**: Database
- **Redis**: Message queue for Celery
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled task scheduler

## Prerequisites

1. **TransIP Kubernetes Cluster**: Create a cluster in TransIP control panel
2. **kubectl**: Configured to connect to your cluster
3. **Helm**: Version 3.x installed
4. **Docker**: For building images
5. **Container Registry**: For storing Docker images (TransIP offers one)

## Setup Instructions

### 1. Create TransIP Kubernetes Cluster

1. Log into your TransIP control panel
2. Navigate to Kubernetes section
3. Create a new cluster with:
   - **Region**: Choose closest to your users
   - **Node Pool**: Start with 2-3 nodes (t3.medium or similar)
   - **Kubernetes Version**: Latest stable (1.28+)
   - **Network**: Default VPC

### 2. Configure kubectl

Download the kubeconfig from TransIP and configure kubectl:

```bash
# Download kubeconfig from TransIP control panel
# Then set it as your current context
kubectl config use-context k8g67
```

### 3. Install Required Helm Charts

```bash
# Add Helm repositories
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Install PostgreSQL (if not using managed database)
helm install postgres bitnami/postgresql \
  --namespace lottery \
  --create-namespace \
  --set auth.postgresPassword=your-secure-password \
  --set auth.database=lottery

# Install Redis
helm install redis bitnami/redis \
  --namespace lottery \
  --create-namespace \
  --set auth.enabled=false
```

### 4. Build and Push Docker Images

```bash
# Build images
docker build -t your-registry/lottery-frontend:latest frontend/
docker build -t your-registry/lottery-backend:latest backend/

# Push to registry
docker push your-registry/lottery-frontend:latest
docker push your-registry/lottery-backend:latest
```

### 5. Deploy Application

```bash
# Create namespace
kubectl create namespace lottery

# Apply secrets and configmaps
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmaps.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Or use Helm chart
helm install lottery helm-chart \
  --namespace lottery \
  --values helm-chart/values.yaml
```

## Configuration

### Environment Variables

Create a [`k8s/secrets.yaml`](../k8s/secrets.yaml) file with your production secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: lottery-secrets
  namespace: lottery
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DATABASE_PASSWORD: <base64-encoded-password>
  EMAIL_HOST_PASSWORD: <base64-encoded-email-password>
  # Add other sensitive environment variables
```

### Domain Configuration

Update the ingress configuration in [`k8s/ingress.yaml`](../k8s/ingress.yaml) with your domain name.

## Monitoring and Logging

### Prometheus and Grafana

```bash
# Install monitoring stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### Application Logs

```bash
# View application logs
kubectl logs -f deployment/lottery-backend -n lottery
kubectl logs -f deployment/lottery-frontend -n lottery
```

## Scaling

### Horizontal Pod Autoscaling

```bash
# Create HPA for backend
kubectl apply -f k8s/hpa.yaml
```

### Database Scaling

For production, consider using a managed PostgreSQL service instead of the Helm chart.

## Backup and Recovery

### Database Backups

```bash
# Create backup job
kubectl apply -f k8s/backup-job.yaml
```

### Application Data

Use persistent volumes for any file storage needs.

## Security

1. **Network Policies**: Restrict pod-to-pod communication
2. **RBAC**: Use service accounts with minimal permissions
3. **Secrets Management**: Use external secret management (HashiCorp Vault, AWS Secrets Manager)
4. **TLS**: Configure SSL certificates for ingress
5. **Pod Security**: Use security contexts and pod security standards

## Troubleshooting

### Common Issues

1. **Image Pull Errors**: Check registry credentials
2. **Database Connection**: Verify PostgreSQL service and credentials
3. **Ingress Issues**: Check ingress controller and DNS
4. **Memory Issues**: Adjust resource limits

### Debug Commands

```bash
# Check pod status
kubectl get pods -n lottery

# Describe pod for details
kubectl describe pod <pod-name> -n lottery

# Check logs
kubectl logs <pod-name> -n lottery

# Port forward for debugging
kubectl port-forward svc/lottery-backend 8000:8000 -n lottery
```

## Cost Optimization

1. **Node Sizing**: Use appropriate instance types
2. **Autoscaling**: Enable cluster autoscaler
3. **Resource Limits**: Set appropriate CPU/memory limits
4. **Spot Instances**: Use spot instances for non-critical workloads

## Updates and Rollouts

```bash
# Update application
kubectl set image deployment/lottery-backend lottery-backend=your-registry/lottery-backend:new-version -n lottery

# Rollback if needed
kubectl rollout undo deployment/lottery-backend -n lottery
```
