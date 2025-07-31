# Deployment Summary for bynderlottery.online

## ✅ Configuration Updated

All Kubernetes configuration files have been updated with your specific settings from [`.env-k8s`](../.env-k8s):

### **Domain Configuration**

- **Domain**: `bynderlottery.online`
- **Site Name**: `bynderlottery.online`
- **Admin Email**: `jobganzevoort@bynderlottery.online`
- **From Email**: `noreply@bynderlottery.online`

### **Database Configuration**

- **Database Name**: `myproject`
- **Database User**: `janedoe`
- **Database Password**: `rxgcrsabhfxtuiuk` (base64 encoded in secrets)

### **Email Configuration**

- **SMTP Host**: `mail.candidmind.nl`
- **SMTP Port**: `587`
- **SMTP User**: `jobganzevoort@bynderlottery.online`
- **SMTP Password**: `eznqklgvsqcythnf` (base64 encoded in secrets)
- **TLS**: Enabled

### **Security**

- **Django Secret Key**: `zgspvncphrkoeubvpxpduyqceapfznzcaarfhpbqpggrqajbkhlfeymtobfhiuan`
- **Admin Password**: `avqhpolfkhkfjkdp` (base64 encoded in secrets)

### **Environment**

- **Layer**: `production`
- **Time Zone**: `Europe/Amsterdam`
- **UID/GID**: `7328/5799`

## 🚀 Next Steps

### 1. Create TransIP Kubernetes Cluster

1. Log into TransIP control panel
2. Create a new Kubernetes cluster:
   - **Cluster ID**: `k8g67` (assigned by TransIP)
   - **Region**: Amsterdam (or closest to your users)
   - **Nodes**: 2-3 t3.medium instances
   - **Storage**: 20-50 GB per node

### 2. Configure kubectl

```bash
# Download kubeconfig from TransIP and configure
kubectl config use-context k8g67

# Test connection
kubectl cluster-info
kubectl get nodes
```

### 3. Set Up Container Registry

1. Create a container registry in TransIP control panel
2. Note your registry URL (e.g., `registry.transip.nl/your-username`)
3. Login to registry:
   ```bash
   docker login registry.transip.nl
   ```

### 4. Update Registry References

Before deploying, update these files with your actual registry URL:

- [`k8s/deployments.yaml`](../k8s/deployments.yaml) - Replace `your-registry` with your registry URL
- [`helm-chart/values.yaml`](../helm-chart/values.yaml) - Replace `your-registry` with your registry URL

### 5. Deploy Application

**Option A: GitHub Actions Deployment (Recommended)**

```bash
# Push to main branch to trigger automatic deployment
git push origin main
```

**Option B: Manual Step-by-step**

```bash
# Install dependencies
./k8s/deploy.sh deploy -d bynderlottery.online

# Check status
kubectl get pods -n lottery
```

### 6. Configure DNS

1. Get the LoadBalancer IP:

   ```bash
   kubectl get service ingress-nginx-controller -n ingress-nginx
   ```

2. Create DNS A record:
   - **Name**: `@` (or your subdomain)
   - **Value**: LoadBalancer IP from step 1
   - **TTL**: 300 seconds

### 7. Verify Deployment

```bash
# Check all components
kubectl get pods -n lottery
kubectl get services -n lottery
kubectl get ingress -n lottery

# Check SSL certificate
kubectl get certificates -n lottery

# View logs
kubectl logs -f deployment/lottery-backend -n lottery
```

## 📋 Files Updated

### Kubernetes Manifests

- ✅ [`k8s/configmaps.yaml`](../k8s/configmaps.yaml) - Environment configuration
- ✅ [`k8s/secrets.yaml`](../k8s/secrets.yaml) - Base64 encoded secrets
- ✅ [`k8s/ingress.yaml`](../k8s/ingress.yaml) - Domain routing
- ✅ [`k8s/deployments.yaml`](../k8s/deployments.yaml) - Application deployments
- ✅ [`k8s/services.yaml`](../k8s/services.yaml) - Service definitions
- ✅ [`k8s/hpa.yaml`](../k8s/hpa.yaml) - Auto-scaling configuration

### Helm Chart

- ✅ [`helm-chart/values.yaml`](../helm-chart/values.yaml) - Chart configuration
- ✅ [`helm-chart/templates/`](../helm-chart/templates/) - All template files

### Deployment Scripts

- ✅ [`k8s/deploy.sh`](../k8s/deploy.sh) - Step-by-step deployment
- ✅ [`k8s/monitoring.yaml`](../k8s/monitoring.yaml) - Monitoring setup

## 🔧 Customization Needed

Before deployment, you need to:

1. **Update Registry URL**: Replace `your-registry` with your actual TransIP registry URL in:

   - [`k8s/deployments.yaml`](../k8s/deployments.yaml)
   - [`helm-chart/values.yaml`](../helm-chart/values.yaml)

2. **Verify Email Settings**: Ensure `mail.candidmind.nl` is accessible and credentials are correct

3. **Test Database Connection**: Verify PostgreSQL can connect with the provided credentials

## 🎯 Expected Result

After deployment, your application will be available at:

- **Main Site**: https://bynderlottery.online
- **Admin Panel**: https://bynderlottery.online/admin
- **API**: https://bynderlottery.online/api
- **Monitoring**: https://monitoring.bynderlottery.online (if enabled)

## 🔍 Troubleshooting

### Common Issues

1. **Image Pull Errors**

   ```bash
   # Check if images exist
   docker pull registry.transip.nl/your-username/lottery-backend:latest
   ```

2. **Database Connection**

   ```bash
   # Check PostgreSQL pod
   kubectl get pods -n lottery -l app=postgresql
   kubectl logs -f deployment/postgres -n lottery
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   kubectl get certificates -n lottery
   kubectl describe certificate lottery-tls -n lottery
   ```

### Useful Commands

```bash
# Get external IP
kubectl get service ingress-nginx-controller -n ingress-nginx

# Port forward for debugging
kubectl port-forward svc/lottery-backend 8000:8000 -n lottery

# View application logs
kubectl logs -f deployment/lottery-backend -n lottery
kubectl logs -f deployment/lottery-frontend -n lottery

# Scale deployment
kubectl scale deployment lottery-backend --replicas=3 -n lottery
```

## 📞 Support

- **TransIP Support**: For cluster and infrastructure issues
- **Application Logs**: Check pod logs for application issues
- **Monitoring**: Use Grafana dashboards for performance monitoring

Your lottery application is now ready for deployment on TransIP Kubernetes! 🎉
