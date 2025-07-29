# TransIP Kubernetes Cluster Information

## Cluster Details
- **Cluster ID**: `k8g67`
- **Domain**: `bynderlottery.online`
- **Registry**: `registry.transip.nl/your-username` (update with your actual registry)

## Quick Commands

### Check Cluster Status
```bash
kubectl config use-context k8g67
kubectl cluster-info
kubectl get nodes
```

### Deploy Application
```bash
# Deploy via GitHub Actions
git push origin main

# Or step-by-step
./k8s/deploy.sh deploy -d bynderlottery.online
```

### Check Application Status
```bash
kubectl get pods -n lottery
kubectl get services -n lottery
kubectl get ingress -n lottery
```

### Get External IP
```bash
kubectl get service ingress-nginx-controller -n ingress-nginx
```

### View Logs
```bash
kubectl logs -f deployment/lottery-backend -n lottery
kubectl logs -f deployment/lottery-frontend -n lottery
```

## DNS Configuration
Once you have the LoadBalancer IP, create an A record:
- **Name**: `@`
- **Value**: LoadBalancer IP
- **TTL**: 300 seconds

## Expected URLs
- **Main Site**: https://bynderlottery.online
- **Admin Panel**: https://bynderlottery.online/admin
- **API**: https://bynderlottery.online/api
- **Monitoring**: https://monitoring.bynderlottery.online (if enabled)

## Troubleshooting
```bash
# Check certificate status
kubectl get certificates -n lottery

# Port forward for debugging
kubectl port-forward svc/lottery-backend 8000:8000 -n lottery

# Check all namespaces
kubectl get namespaces
``` 
