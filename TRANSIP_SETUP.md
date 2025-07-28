# TransIP Kubernetes Cluster Setup Guide

This guide will help you set up a Kubernetes cluster on TransIP and deploy your lottery application.

## Prerequisites

1. **TransIP Account**: You need an active TransIP account
2. **Domain Name**: A domain name for your application (optional but recommended)
3. **Local Tools**: kubectl, helm, and docker installed on your local machine

## Step 1: Create TransIP Kubernetes Cluster

### 1.1 Access TransIP Control Panel

1. Log into your TransIP account at https://www.transip.nl/
2. Navigate to the "Kubernetes" section in the control panel

### 1.2 Create New Cluster

1. Click "Create New Cluster"
2. Configure the cluster with these recommended settings:

**Basic Configuration:**
- **Cluster ID**: `k8g67` (assigned by TransIP)
- **Region**: Choose the closest to your users (e.g., Amsterdam for EU)
- **Kubernetes Version**: Latest stable (1.28+)

**Node Pool Configuration:**
- **Node Pool Name**: `lottery-nodes`
- **Node Count**: Start with 2-3 nodes
- **Instance Type**: `t3.medium` or `t3.large` (2 vCPU, 4-8 GB RAM)
- **Storage**: 20-50 GB per node

**Network Configuration:**
- **VPC**: Use default VPC
- **Subnet**: Choose appropriate subnet
- **Security Groups**: Allow HTTP (80), HTTPS (443), and SSH (22)

### 1.3 Wait for Cluster Creation

The cluster creation process takes 10-15 minutes. You'll receive an email when it's ready.

## Step 2: Configure kubectl

### 2.1 Download kubeconfig

1. In the TransIP control panel, go to your cluster
2. Click "Download kubeconfig"
3. Save the file as `~/.kube/config` or merge it with your existing config

### 2.2 Test Connection

```bash
kubectl cluster-info
kubectl get nodes
```

**Note**: Your cluster ID is `k8g67`. Use this when referring to your cluster in TransIP control panel.

## Step 3: Install Required Tools

### 3.1 Install Helm

```bash
# macOS
brew install helm

# Linux
curl https://get.helm.sh/helm-v3.13.0-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/helm

# Windows
choco install kubernetes-helm
```

### 3.2 Install cert-manager (for SSL certificates)

```bash
# Add cert-manager repository
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

### 3.3 Create ClusterIssuer for Let's Encrypt

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Step 4: Set Up Container Registry

### 4.1 TransIP Container Registry

TransIP offers a container registry. Set it up:

1. Go to TransIP control panel
2. Navigate to "Container Registry"
3. Create a new registry
4. Note the registry URL (e.g., `registry.transip.nl/your-username`)

### 4.2 Configure Docker Login

```bash
# Login to TransIP registry
docker login registry.transip.nl
```

## Step 5: Build and Push Docker Images

### 5.1 Update Image References

Edit the following files to use your TransIP registry:

- `k8s/deployments.yaml`
- `helm-chart/values.yaml`
- `k8s/deploy.sh`

Replace `your-registry` with your actual TransIP registry URL.

### 5.2 Build and Push Images

```bash
# Build images
docker build -t registry.transip.nl/your-username/lottery-backend:latest backend/
docker build -t registry.transip.nl/your-username/lottery-frontend:latest frontend/

# Push to registry
docker push registry.transip.nl/your-username/lottery-backend:latest
docker push registry.transip.nl/your-username/lottery-frontend:latest
```

## Step 6: Configure Environment Variables

### 6.1 Update Secrets

Edit `k8s/secrets.yaml` with your actual production values:

```bash
# Generate a secure Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Encode secrets in base64
echo -n "your-secret-key" | base64
echo -n "your-database-password" | base64
echo -n "your-email-password" | base64
```

### 6.2 Update ConfigMaps

Edit `k8s/configmaps.yaml` with your domain and email settings:

```yaml
SITENAME: "yourdomain.com"
DEFAULT_FROM_EMAIL: "noreply@yourdomain.com"
EMAIL_HOST: "smtp.yourdomain.com"
# ... other settings
```

## Step 7: Deploy Application

### 7.1 Install Dependencies

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

# Install PostgreSQL
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

### 7.2 Deploy Application

```bash
# Create namespace
kubectl create namespace lottery

# Apply secrets and configmaps
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmaps.yaml

# Deploy application
kubectl apply -f k8s/deployments.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Or use Helm chart
helm install lottery ./helm-chart \
  --namespace lottery \
  --values helm-chart/values.yaml
```

## Step 8: Configure DNS

### 8.1 Get Load Balancer IP

```bash
kubectl get service -n ingress-nginx
```

Note the external IP of the ingress-nginx-controller service.

### 8.2 Update DNS Records

In your domain's DNS settings, create an A record:

- **Name**: `@` (or your subdomain)
- **Value**: The Load Balancer IP from step 8.1
- **TTL**: 300 seconds

## Step 9: Verify Deployment

### 9.1 Check Pod Status

```bash
kubectl get pods -n lottery
kubectl get services -n lottery
kubectl get ingress -n lottery
```

### 9.2 Check Logs

```bash
# Check backend logs
kubectl logs -f deployment/lottery-backend -n lottery

# Check frontend logs
kubectl logs -f deployment/lottery-frontend -n lottery
```

### 9.3 Test Application

1. Wait for SSL certificate to be issued (can take a few minutes)
2. Visit your domain in a browser
3. Test the application functionality

## Step 10: Monitoring and Maintenance

### 10.1 Install Monitoring Stack

```bash
# Apply monitoring configuration
kubectl apply -f k8s/monitoring.yaml
```

### 10.2 Set Up Backups

```bash
# Apply backup configuration
kubectl apply -f k8s/backup-job.yaml
```

### 10.3 Apply Security Policies

```bash
# Apply network policies
kubectl apply -f k8s/network-policies.yaml
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   ```bash
   # Check if images exist in registry
   docker pull registry.transip.nl/your-username/lottery-backend:latest
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL service
   kubectl get pods -n lottery -l app=postgresql
   kubectl logs -f deployment/postgres -n lottery
   ```

3. **Ingress Issues**
   ```bash
   # Check ingress controller
   kubectl get pods -n ingress-nginx
   kubectl describe ingress lottery-ingress -n lottery
   ```

4. **SSL Certificate Issues**
   ```bash
   # Check cert-manager
   kubectl get certificates -n lottery
   kubectl describe certificate lottery-tls -n lottery
   ```

### Useful Commands

```bash
# Get external IP
kubectl get service ingress-nginx-controller -n ingress-nginx

# Check certificate status
kubectl get certificates -A

# View application logs
kubectl logs -f deployment/lottery-backend -n lottery

# Port forward for debugging
kubectl port-forward svc/lottery-backend 8000:8000 -n lottery

# Scale deployment
kubectl scale deployment lottery-backend --replicas=3 -n lottery
```

## Cost Optimization

1. **Right-size nodes**: Start with smaller instances and scale up as needed
2. **Use spot instances**: For non-critical workloads
3. **Enable autoscaling**: Set up HPA for automatic scaling
4. **Monitor usage**: Use TransIP's monitoring tools to track costs

## Security Best Practices

1. **Use secrets management**: Store sensitive data in Kubernetes secrets
2. **Network policies**: Restrict pod-to-pod communication
3. **RBAC**: Use service accounts with minimal permissions
4. **Regular updates**: Keep images and dependencies updated
5. **Backup strategy**: Regular database and configuration backups

## Support

- **TransIP Support**: Contact TransIP support for cluster issues
- **Application Issues**: Check logs and monitoring dashboards
- **Community**: Use Kubernetes and Helm community resources 
