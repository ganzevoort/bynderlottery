# Test Environment Setup

This document describes the dedicated test environment for the Lottery System, which runs separately from the main development environment.

## 🏗️ Architecture

The test environment uses a separate Docker Compose configuration (`compose.test.yaml`) with the following services:

- **web** (nginx) - Reverse proxy on port 8081
- **frontend** (Next.js) - React frontend with test configuration
- **backend** (Django) - Python backend with test settings
- **cypress** - End-to-end testing framework

## 🚀 Quick Start

### 1. Set up the test environment

```bash
./run-tests.sh setup
```

This command:
- Starts all test containers
- Runs database migrations
- Seeds test data
- Makes the application available at `http://localhost:8081`

### 2. Run tests

```bash
# Run all tests
./run-tests.sh all

# Run specific test suites
./run-tests.sh user-journey
./run-tests.sh api

# Interactive mode for debugging
./run-tests.sh interactive
```

### 3. Clean up

```bash
./run-tests.sh clean
```

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
- `compose.test.yaml` - Test-specific service configuration
- Separate port (8081) to avoid conflicts
- Minimal service dependencies

### Django Settings
- `backend/service/settings/test.py` - Test-specific Django settings
- SQLite database configuration
- Eager Celery tasks
- Console email backend

### Cypress Configuration
- `cypress/cypress.config.ts` - Updated for test environment
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
./run-tests.sh setup      # Set up test environment
./run-tests.sh all        # Run all tests
./run-tests.sh user-journey  # Run user journey tests
./run-tests.sh api        # Run API tests
./run-tests.sh interactive # Open Cypress UI
./run-tests.sh clean      # Clean up environment
./run-tests.sh logs       # View logs
./run-tests.sh status     # Check container status
./run-tests.sh restart    # Restart containers
./run-tests.sh shell      # Open Django shell
./run-tests.sh migrate    # Run migrations
./run-tests.sh seed       # Seed test data
```

### Environment Variables

The test environment uses these environment variables:

```bash
# Django
DJANGO_SETTINGS_MODULE=service.settings.test
DATABASE_URL=sqlite:///test_db.sqlite3
CELERY_TASK_ALWAYS_EAGER=true
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEBUG=true
SECRET_KEY=test-secret-key-for-testing-only

# Cypress
CYPRESS_baseUrl=http://web:80
CYPRESS_video=false
CYPRESS_screenshotOnRunFailure=false
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
   ./run-tests.sh status
   
   # View logs
   ./run-tests.sh logs
   
   # Restart containers
   ./run-tests.sh restart
   ```

3. **Database issues**
   ```bash
   # Reset database
   ./run-tests.sh clean
   ./run-tests.sh setup
   ```

### Debug Commands

```bash
# Open Django shell
./run-tests.sh shell

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

The test environment is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          chmod +x run-tests.sh
          ./run-tests.sh setup
          ./run-tests.sh all
```

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

For more information, see the main [TESTING.md](TESTING.md) file. 
