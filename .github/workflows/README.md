# GitHub Actions CI/CD Pipeline

This repository uses GitHub Actions for continuous integration and deployment.

## Pipeline Overview

The pipeline runs on:
- **Push to main branch**: Full CI/CD (build → test → demo & deploy)
- **Pull requests**: Build and test only (no deployment)

## Pipeline Stages

### 1. Build Stage
- **Parallel builds**: Backend and frontend images build simultaneously
- **Docker registry**: Images pushed to `registry.bynderlottery.online`
- **Build caching**: Uses GitHub Actions cache for faster builds
- **Image tagging**: Uses SHA-based tags for traceability

### 2. Test Stage
- **Docker-based testing**: Uses [`compose.test.yaml`](../../compose.test.yaml) for consistent environment
- **Backend tests**: Django unit tests with SQLite (test environment)
- **Frontend tests**: Next.js tests
- **E2E tests**: Cypress integration tests
- **Full test suite**: Backend linting, formatting, tests + frontend E2E tests

### 3. Demo Stage (main branch only)
- Runs demo test suite using Docker containers
- Creates demo video for product owner review
- Uploads demo videos as artifacts (retained for 30 days)

### 4. Deploy Stage (main branch only)
- **Manual approval required**: Uses GitHub Environments
- Deploys to Kubernetes cluster
- Restarts all deployments to pick up latest images

## Required Secrets

Add these secrets in your GitHub repository settings:

### Container Registry
- `REGISTRY_PASSWORD`: Password for `registry.bynderlottery.online` (username is set as environment variable)

### Kubernetes Access
- `KUBECONFIG`: Base64-encoded kubeconfig file for cluster access

## Environment Protection

The `production` environment is configured with:
- **Required reviewers**: Manual approval before deployment
- **Wait timer**: Optional delay before deployment
- **Deployment branches**: Only `main` branch can deploy

## Artifacts

- **Demo videos**: Available for 30 days after each successful run
- **Test results**: Available for 90 days

## Local Development

For local testing, use the [`scripts/run-tests.sh`](../../scripts/run-tests.sh) script:

```bash
# Run all tests
./scripts/run-tests.sh full-test

# Run only E2E tests
./scripts/run-tests.sh all

# Run only backend tests
./scripts/run-tests.sh backend-check

# Interactive testing
./scripts/run-tests.sh interactive
```

## Troubleshooting

### Build Failures
- Check Docker registry credentials
- Verify Dockerfile syntax
- Check for missing dependencies

### Test Failures
- Review test logs in GitHub Actions
- Check database and Redis connectivity
- Verify test environment setup

### Deployment Failures
- Check Kubernetes cluster access
- Verify kubeconfig is valid
- Check namespace and resource quotas

## Manual Deployment

If you need to deploy manually:

1. Go to Actions tab in GitHub
2. Select the latest successful workflow
3. Click "Deploy to Production" job
4. Click "Re-run jobs" → "Re-run failed jobs"

## Workflow Structure

The pipeline follows this dependency structure:

```yaml
build-backend ──┐
                ├── test ──┐
build-frontend ──┘         ├── demo
                           └── deploy
```

### Key Features
- **Parallel builds**: Backend and frontend build simultaneously
- **Docker-based testing**: Consistent test environment
- **Composite actions**: Reusable Docker setup steps
- **Parallel demo & deploy**: Demo and deployment run in parallel after tests pass

## Monitoring

- **Pipeline status**: Check Actions tab
- **Deployment status**: Use `kubectl get pods -n lottery`
- **Application logs**: Use `kubectl logs -n lottery` 
