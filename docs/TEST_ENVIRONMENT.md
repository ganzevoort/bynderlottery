# Test Environment Setup

This document describes the dedicated test environment for the Lottery System, which runs separately from the main development environment.

## 🏗️ Architecture

The test environment uses a separate Docker Compose configuration ([`compose.test.yaml`](../compose.test.yaml)) with the following services:

- **web** (nginx) - Reverse proxy on port 8081
- **frontend** (Next.js) - React frontend with test configuration
- **backend** (Django) - Python backend with test settings
- **cypress** - End-to-end testing framework

## 🎯 Purpose of compose.test.yaml

The `compose.test.yaml` file serves two specific purposes:

### 1. Integration Testing

- **Primary purpose**: Running comprehensive integration tests using Cypress
- **Environment**: Uses production-optimized images (`--target=production`)
- **Scope**: Tests the complete application stack (frontend + backend + database) as it would run in production
- **CI/CD**: Automatically triggered in GitHub Actions for every push to main branch
- **local**: Use [`scripts/run-tests.sh`](../scripts/run-tests.sh)

### 2. Demo Creation (Special Case)

- **Secondary purpose**: Creating demo videos for product owner review
- **Special case**: Uses the same infrastructure as integration tests but runs different Cypress specs
- **Output**: Generates video artifacts that are uploaded to GitHub Actions
- **Trigger**: Only runs on pushes to main branch, after successful integration tests
- **Demo specs**: Located in [`cypress/e2e/demo/`](../cypress/e2e/demo/) directory

## 🚀 Quick Start

### 1. Local Testing

```bash
./scripts/run-tests.sh
```

This command automatically runs tests in two phases:

#### Phase 1: Linting and Unit Tests

- Builds images with `--target=tester` stage
- Runs frontend linting and unit tests
- Runs backend unit tests and formatting checks

#### Phase 2: Integration Tests

- Builds images with `--target=production` stage (cached from tester)
- Starts test containers using `compose.test.yaml`
- Runs Cypress E2E tests
- Cleans up containers when done

### 2. CI/CD Testing

The GitHub Actions workflow uses a different approach:

1. **Build Jobs**: Build and push production images, then build tester images
2. **Integration Tests**: Pull production images from registry and run E2E tests
3. **Demo**: Create demo videos using the same production images

## 🔧 Test Environment Features

### Database

- **SQLite** - uses in-memory SQLite for faster test execution
- **Test data seeding** - automatic setup of test data
- **Automatic cleanup** between test runs

### Celery

- **Always eager** execution (no background workers)
- **Synchronous** task processing
- **No Redis service** - not included in test environment
- **No Celery workers** - tasks run synchronously in the main process

### Email

- **Console backend** - emails printed to console
- **No external email service** required
- **Easy debugging** of email content

### Performance Optimizations

- **Eager Celery tasks** - no background workers needed
- **Console email backend** - emails printed to console for debugging
- **Minimal services** - only web, frontend, backend, and cypress
- **No external dependencies** - no Redis, PostgreSQL, or Celery workers

## 📁 Configuration Files

### Docker Compose

- [`compose.test.yaml`](../compose.test.yaml) - Test-specific service configuration
- **Local**: Uses `build` with `--target=production` for integration testing
- **CI/CD**: Modified by [`scripts/update-compose.py`](../scripts/update-compose.py) to use registry images
- Separate port (8081) to avoid conflicts
- Minimal service dependencies

### Django Settings

- [`backend/service/settings/test.py`](../backend/service/settings/test.py) - Test-specific Django settings
- Console email backend for debugging
- Eager Celery tasks (no background workers)
- Redis settings to prevent package errors (no Redis service in test environment)

### Cypress Configuration

- [`cypress/cypress.config.js`](../cypress/cypress.config.js)
- Base URL: `http://localhost:8081`

## 🧪 Test Data Management

### Automatic Setup

The test environment automatically:

1. Clears any existing test data
2. Runs database migrations
3. Seeds fresh test data
4. Verifies the environment is ready

### Test Data Seeder

The `seed_test_data` management command creates:

- Test users with accounts
- Open and closed draws
- Prizes for each draw type
- Assigned and unassigned ballots

### Database Cleanup

Each test run:

- Clears all data before starting
- Seeds fresh data for isolation
- Ensures consistent test state

## 🔄 Test Commands

### Available Commands

```bash
./scripts/run-tests.sh            # Run all tests (frontend + backend + E2E)
```

### Environment Variables

The test environment uses these environment variables (from [`test.env`](../test.env)):

```bash
# Frontend test environment
NODE_ENV=development

# Backend test environment
LAYER=test
SECRET_KEY=test-secret-key-for-testing-only
TIME_ZONE=Europe/Amsterdam
DEFAULT_FROM_EMAIL=noreply@lottery.com
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=/tmp/test_db.sqlite3
REDIS_HOST=localhost
REDIS_PORT=6379

# Cypress settings
CYPRESS_baseUrl=http://web
CYPRESS_video=true
CYPRESS_screenshotOnRunFailure=true
```

## 🐛 Debugging

### Common Issues

1. **Port conflicts**

   ```bash
   # Check if port 8081 is in use
   lsof -i :8081

   # Kill process if needed
   kill -9 <PID>
   ```

2. **Container issues**

   ```bash
   # Check container status
   docker compose -f compose.test.yaml ps

   # View logs
   docker compose -f compose.test.yaml logs

   # Restart containers
   docker compose -f compose.test.yaml restart
   ```

3. **Database issues**
   ```bash
   # Reset database
   docker compose -f compose.test.yaml down
   docker compose -f compose.test.yaml up -d
   ```

### Debug Commands

```bash
# Open Django shell
docker compose -f compose.test.yaml exec backend python manage.py shell

# Check database
docker compose -f compose.test.yaml exec backend python manage.py dbshell

# View test data
docker compose -f compose.test.yaml exec backend python manage.py shell
```

## 📊 Performance

### Startup Time

- **~30 seconds** for initial setup
- **~10 seconds** for subsequent runs
- **~5 seconds** for test execution

### Resource Usage

- **Minimal memory** usage (SQLite database, no external services)
- **Fast database** operations (SQLite)
- **No background processes** (eager Celery, no Redis/PostgreSQL)

## 🔒 Security

### Test Isolation

- **Separate database** from development
- **No external services** required
- **Clean environment** for each test run

### Test Data

- **No sensitive data** in test environment
- **Fake credentials** for testing
- **Console email** (no external email)

## 🚀 CI/CD Integration

The test environment is integrated into the GitHub Actions CI/CD pipeline:

### Pipeline Jobs

- **Build Backend**: Builds and pushes production image, then builds tester image for linting/unit tests
- **Build Frontend**: Builds and pushes production image, then builds tester image for linting/unit tests
- **Integration Tests**: Uses production images from registry to run Cypress E2E tests
- **Demo**: Creates demo video for product owner review
- **Deploy**: Deploys to Kubernetes cluster (manual approval required)

### Integration Testing Workflow

1. **Image Preparation**: Uses production-optimized images from `ghcr.io/ganzevoort/bynderlottery`
2. **Compose File Update**: [`scripts/update-compose.py`](../scripts/update-compose.py) modifies `compose.test.yaml` to use registry images instead of building locally
3. **Environment Setup**: Starts all services using the updated `compose.test.yaml`
4. **Test Execution**: Runs Cypress tests from `cypress/e2e/tests/`
5. **Cleanup**: Stops containers and cleans up resources

### Demo Creation Workflow

1. **Same Infrastructure**: Uses identical `compose.test.yaml` setup as integration tests
2. **Different Specs**: Runs Cypress tests from `cypress/e2e/demo/` directory
3. **Video Output**: Generates demo videos showing complete user journeys
4. **Artifact Upload**: Videos are uploaded to GitHub Actions for product owner review

### Key Features

- **Parallel execution**: Frontend, backend, and integration tests run simultaneously
- **Production images**: Integration tests use the exact images that will be deployed
- **Environment consistency**: Uses `test.env` for consistent test environment
- **Artifact uploads**: Demo videos are uploaded as artifacts for review
- **Dual purpose**: Same infrastructure serves both testing and demo creation

## 📈 Benefits

### Speed

- **Faster startup** than development environment
- **No external dependencies** (PostgreSQL, Redis)
- **Optimized for testing** performance

### Reliability

- **Consistent environment** across runs
- **Isolated test data** for each run
- **No interference** with development

### Simplicity

- **Single command** setup
- **Automatic cleanup** after tests
- **Easy debugging** with console output

## 🔮 Future Enhancements

Planned improvements:

1. **Parallel test execution** with multiple Cypress instances
2. **Test data factories** for more realistic data
3. **Performance benchmarking** tests
4. **Visual regression** testing
5. **Mobile device** testing

---

For more information, see the main [TESTING.md](./TESTING.md) file.
