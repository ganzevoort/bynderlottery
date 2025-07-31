# Test Environment Setup

This document describes the dedicated test environment for the Lottery System, which runs separately from the main development environment.

## 🏗️ Architecture

The test environment uses a separate Docker Compose configuration ([`compose.test.yaml`](../compose.test.yaml)) with the following services:

- **web** (nginx) - Reverse proxy on port 8081
- **frontend** (Next.js) - React frontend with test configuration
- **backend** (Django) - Python backend with test settings
- **cypress** - End-to-end testing framework

## 🚀 Quick Start

### 1. Run all tests

```bash
./scripts/run-tests.sh
```

This command automatically:

- Starts all test containers
- Runs frontend linting and unit tests
- Runs backend unit tests and formatting checks
- Runs Cypress E2E tests
- Cleans up containers when done

## 🔧 Test Environment Features

### Database

- **SQLite** instead of PostgreSQL for faster startup
- **In-memory** database for maximum speed
- **Automatic cleanup** between test runs

### Celery

- **Always eager** execution (no background workers)
- **Synchronous** task processing
- **No Redis** dependency

### Email

- **Console backend** - emails printed to console
- **No external email service** required
- **Easy debugging** of email content

### Performance Optimizations

- **MD5 password hashing** for faster authentication
- **Disabled logging** for cleaner output
- **In-memory cache** instead of Redis
- **No static file collection** during tests

## 📁 Configuration Files

### Docker Compose

- [`compose.test.yaml`](../compose.test.yaml) - Test-specific service configuration
- Separate port (8081) to avoid conflicts
- Minimal service dependencies

### Django Settings

- [`backend/service/settings/test.py`](../backend/service/settings/test.py) - Test-specific Django settings
- SQLite database configuration
- Eager Celery tasks
- Console email backend

### Cypress Configuration

- [`cypress/cypress.config.ts`](../cypress/cypress.config.ts) - Updated for test environment
- Base URL: `http://localhost:8081`
- Optimized timeouts and settings

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
POSTGRES_DB=testdb
POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
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

- **Minimal memory** usage (no PostgreSQL/Redis)
- **Fast database** operations (SQLite)
- **No background processes** (eager Celery)

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

- **Frontend Tests**: Linting and unit tests using development image
- **Backend Tests**: Linting, formatting checks, and unit tests using development image
- **Integration Tests**: Cypress E2E tests using production images from registry
- **Demo**: Creates demo video for product owner review
- **Deploy**: Deploys to Kubernetes cluster (manual approval required)

### Key Features

- **Parallel execution**: Frontend, backend, and integration tests run simultaneously
- **Production images**: Integration tests use the exact images that will be deployed
- **Environment consistency**: Uses `test.env` for consistent test environment
- **Artifact uploads**: Demo videos are uploaded as artifacts for review

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
