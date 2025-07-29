# Docker Registry Setup for TransIP Kubernetes

Based on the [TransIP documentation](https://www.transip.nl/knowledgebase/7078-een-docker-registry-deployen-kubernetes), you need to deploy your own Docker registry within your Kubernetes cluster.

## 🐳 **Registry Configuration**

### **Registry Details**
- **Domain**: `registry.bynderlottery.online`
- **Username**: `lottery`
- **Password**: `lottery-secure-password-2024`
- **Storage**: 10GB persistent volume

## 🚀 **Quick Setup**

### **Option 1: Automated Setup**
```bash
# Run the setup script
./scripts/setup-registry.sh lottery lottery-secure-password-2024
```

### **Option 2: Manual Setup**

#### **Step 1: Generate Authentication**
```bash
# Generate password file
htpasswd -nB lottery | tee registry.htpasswd
# Enter password: lottery-secure-password-2024
```

#### **Step 2: Create Namespace and Secret**
```bash
# Create namespace
kubectl create namespace docker-registry

# Create authentication secret
kubectl create secret generic registry-auth-secret \
  --from-file=users=registry.htpasswd \
  -n docker-registry
```

#### **Step 3: Deploy Registry**
```bash
# Deploy the registry
kubectl apply -f k8s/registry-deployment.yaml
```

#### **Step 4: Wait for Deployment**
```bash
# Wait for registry to be ready
kubectl wait --for=condition=available --timeout=300s deployment/docker-registry-deployment -n docker-registry
```

## 📋 **DNS Configuration**

### **Get External IP**
```bash
kubectl get service ingress-nginx-controller -n ingress-nginx
```

### **Add DNS Record**
Create an A record in your DNS settings:
- **Name**: `registry`
- **Value**: External IP from above
- **TTL**: 300 seconds

## 🔐 **Authentication**

### **Login to Registry**
```bash
# Login to your registry
docker login registry.bynderlottery.online

# Username: lottery
# Password: lottery-secure-password-2024
```

### **Test Registry**
```bash
# Test with a simple image
docker pull hello-world
docker tag hello-world registry.bynderlottery.online/hello-world
docker push registry.bynderlottery.online/hello-world
```

## 🏗️ **Build and Push Images**

### **Build Images**
```bash
# Build backend image
docker build -t registry.bynderlottery.online/lottery-backend:latest backend/

# Build frontend image
docker build -t registry.bynderlottery.online/lottery-frontend:latest frontend/
```

### **Push Images**
```bash
# Push images to registry
docker push registry.bynderlottery.online/lottery-backend:latest
docker push registry.bynderlottery.online/lottery-frontend:latest
```

## 📊 **Monitor Registry**

### **Check Status**
```bash
# Check registry pods
kubectl get pods -n docker-registry

# Check registry service
kubectl get service -n docker-registry

# Check ingress
kubectl get ingress -n docker-registry

# Check certificates
kubectl get certificates -n docker-registry
```

### **View Logs**
```bash
# View registry logs
kubectl logs -f deployment/docker-registry-deployment -n docker-registry
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Authentication Failed**
   ```bash
   # Check secret
   kubectl get secret registry-auth-secret -n docker-registry
   
   # Recreate secret if needed
   kubectl delete secret registry-auth-secret -n docker-registry
   kubectl create secret generic registry-auth-secret \
     --from-file=users=registry.htpasswd \
     -n docker-registry
   ```

2. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   kubectl get certificates -n docker-registry
   kubectl describe certificate registry-tls -n docker-registry
   ```

3. **Storage Issues**
   ```bash
   # Check PVC
   kubectl get pvc -n docker-registry
   kubectl describe pvc registry-pv-claim -n docker-registry
   ```

### **Registry Access**

- **Web Interface**: https://registry.bynderlottery.online
- **Docker Login**: `docker login registry.bynderlottery.online`
- **API**: https://registry.bynderlottery.online/v2/

## 🎯 **Next Steps**

After setting up the registry:

1. **Build and push your images**
2. **Deploy your lottery application**
3. **Monitor the registry usage**

## 📚 **References**

- [TransIP Docker Registry Documentation](https://www.transip.nl/knowledgebase/7078-een-docker-registry-deployen-kubernetes)
- [Docker Registry Documentation](https://docs.docker.com/registry/)
- [NGINX Ingress Basic Auth](https://kubernetes.github.io/ingress-nginx/examples/auth/basic/) 
