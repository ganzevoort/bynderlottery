# Lottery System Testing Guide

This document provides a comprehensive guide to testing the Lottery System, including the new Cypress integration tests.

## 🧪 Testing Overview

The Lottery System includes multiple layers of testing:

1. **Unit Tests** - Django backend tests
2. **Integration Tests** - Cypress end-to-end tests
3. **API Tests** - Backend API endpoint validation
4. **Frontend Tests** - Next.js component tests with Jest and React Testing Library

## 🚀 Cypress Integration Tests

### Quick Start

```bash
# Run all tests
./scripts/run-tests.sh
```

The script automatically runs:

1. **Frontend Tests** (linting + unit tests)
2. **Backend Tests** (unit tests + formatting checks)
3. **E2E Tests** (Cypress integration tests)

### Test Environment

The integration tests use a dedicated test environment defined in [`compose.test.yaml`](../compose.test.yaml):

- **Purpose**: Integration testing and demo creation
- **Infrastructure**: Uses production-optimized images from container registry
- **Services**: nginx proxy, frontend, backend, and Cypress
- **Port**: Runs on port 8081 to avoid conflicts with development environment

#### Dual Purpose

1. **Integration Testing**: Primary purpose for running comprehensive E2E tests
2. **Demo Creation**: Special case for generating demo videos for product owner review

### Test Structure

The Cypress tests are organized in logical directories:

#### Functional Tests ([`e2e/tests/`](../cypress/e2e/tests/))

1. **[01-api-tests.cy.ts](../cypress/e2e/tests/01-api-tests.cy.ts)** - API endpoint validation
2. **[02-token-tests.cy.ts](../cypress/e2e/tests/02-token-tests.cy.ts)** - Email verification and password reset tokens
3. **[03-signup-journey.cy.ts](../cypress/e2e/tests/03-signup-journey.cy.ts)** - Complete signup and email verification flow
4. **[04-password-reset-journey.cy.ts](../cypress/e2e/tests/04-password-reset-journey.cy.ts)** - Password reset workflow
5. **[05-profile-journey.cy.ts](../cypress/e2e/tests/05-profile-journey.cy.ts)** - Profile management and updates
6. **[06-ballot-journey.cy.ts](../cypress/e2e/tests/06-ballot-journey.cy.ts)** - Ballot purchase and assignment
7. **[07-closed-draws-journey.cy.ts](../cypress/e2e/tests/07-closed-draws-journey.cy.ts)** - Viewing closed draws and results

#### Demo Tests ([`e2e/demo/`](../cypress/e2e/demo/))

- **[99-demo.cy.ts](../cypress/e2e/demo/99-demo.cy.ts)** - Complete demo journey for product owner

### Example: Signup Journey Test

Here's an example of how the tests are structured:

```typescript
describe('Signup Journey', () => {
    const testUser = {
        name: 'Signup Test User',
        email: 'signup-test@example.com',
        password: 'password123'
    }

    beforeEach(() => {
        cy.clearDatabase()
        cy.seedTestData()
        cy.waitForTestEnv()
    })

    it('Complete signup journey: signup, verify email, signin', () => {
        // Step 1: Visit home page
        cy.visit('/')
        cy.contains('Welcome to the Lottery System').should('be.visible')
        cy.contains('Get Started').should('be.visible')

        // Step 2: Sign up
        cy.visit('/auth/signup')
        cy.get('input[name='name']').type(testUser.name)
        cy.get('input[name='email']').type(testUser.email)
        cy.get('input[name='password1']').type(testUser.password)
        cy.get('input[name='password2']').type(testUser.password)
        cy.get('button[type='submit']').click()

        // Should show success message
        cy.contains('Account created successfully').should('be.visible')
        cy.contains('Please check your email to verify your account').should('be.visible')

        // Step 3: Get tokens and verify email via UI
        // Note: getTestTokens uses a test-only API endpoint to retrieve email verification
        // and password reset tokens, since accessing actual emails in tests is difficult
        cy.getTestTokens(testUser.email).then((response) => {
            expect(response.status).to.eq(200)
            const emailToken = response.body.email_verification_token

            // Visit email verification page with the token
            cy.visit(`/auth/verify-email/${emailToken}`)
            cy.contains('Email verified successfully').should('be.visible')
        })

        // Step 4: Sign in (after email verification)
        cy.visit('/auth/signin')
        cy.get('input[id='email']').type(testUser.email)
        cy.get('input[id='password']').type(testUser.password)
        cy.get('button[type='submit']').click()

        // Wait for signin to complete and check for success message
        cy.wait(3000)
        cy.get('div').contains('Successfully signed in!').should('be.visible')

        // Should redirect to home page after successful signin
        cy.url().should('eq', 'http://web/')

        // Verify user is authenticated by checking if we can access protected pages
        cy.visit('/my-ballots')
        cy.url().should('include', '/my-ballots')
    })
})
```

### Custom Commands

The test suite includes custom Cypress commands for common operations:

```typescript
// User management
cy.signUp(email, password, name)
cy.signIn(email, password)
cy.signOut()

// Ballot operations
cy.buyBallots(quantity)
cy.assignBallot(drawId)

// Test utilities
cy.clearDatabase()
cy.seedTestData()
cy.waitForApi()
cy.isAuthenticated()
```

## 🔧 Test Configuration

### Docker Setup

The Cypress tests run in a dedicated Docker container:

```yaml
cypress:
  image: cypress/included:13.6.1
  environment:
    - CYPRESS_baseUrl=http://web:80
    - CYPRESS_video=false
    - CYPRESS_screenshotOnRunFailure=false
  volumes:
    - ./cypress:/e2e
    - ./cypress/videos:/e2e/videos
    - ./cypress/screenshots:/e2e/screenshots
  depends_on:
    - web
    - frontend
    - backend
  working_dir: /e2e
  command: cypress run --browser chrome --headless
```

### Test Data Management

The backend provides test endpoints for database management:

- `POST /api/lottery/test/clear-database/` - Clear all test data
- `POST /api/lottery/test/seed-data/` - Seed fresh test data
- `GET /api/lottery/test/health-check/` - Health check endpoint

### Test Data Seeder

A Django management command seeds realistic test data:

```bash
# Run the seeder manually
docker compose exec backend python manage.py seed_test_data
```

This creates:

- Test users with accounts
- Open and closed draws
- Prizes for each draw type
- Assigned and unassigned ballots

## 📊 Test Reports

Cypress generates detailed test reports:

- **Test execution times**
- **Console logs** for debugging
- **Screenshots** on failure (configurable)
- **Video recordings** (configurable)

## 🐛 Debugging Tests

### Common Issues

1. **Timing Issues**

   ```bash
   # Increase timeouts in cypress.config.ts
   defaultCommandTimeout: 15000,
   requestTimeout: 15000,
   ```

2. **Database State Issues**

   ```bash
   # Clear and reseed database
   docker compose exec backend python manage.py seed_test_data
   ```

3. **Container Issues**

   ```bash
   # Check container status
   docker compose ps

   # View logs
   docker compose logs cypress
   ```

### Debug Commands

```bash
# Check test data in database
docker compose exec backend python manage.py shell

# View application logs
docker compose logs
```

## 🔄 Continuous Integration

The tests are designed for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Cypress Tests
on: [push, pull_request]

jobs:
  cypress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Cypress Tests
        run: |
          docker compose up -d
          docker compose run cypress
```

## 📈 Test Coverage

The Cypress tests cover:

### Frontend Functionality

- ✅ User registration and authentication
- ✅ Form validation and error handling
- ✅ Navigation and routing
- ✅ UI interactions and state management

### Backend Integration

- ✅ API endpoint functionality
- ✅ Database operations
- ✅ Session management
- ✅ Error handling

### Business Logic

- ✅ Ballot purchase workflow
- ✅ Ballot assignment to draws
- ✅ Draw browsing and results
- ✅ Profile management

## 🚀 Best Practices

1. **Test Isolation**: Each test clears and reseeds the database
2. **Realistic Data**: Tests use realistic user scenarios
3. **Error Handling**: Tests verify both success and error cases
4. **Performance**: Tests are optimized for speed
5. **Maintainability**: Custom commands reduce code duplication

## 🔮 Future Enhancements

Planned improvements to the test suite:

1. **Mobile Testing**: Add responsive design tests
2. **Performance Tests**: Add load testing scenarios
3. **Accessibility Tests**: Add a11y compliance checks
4. **Visual Regression Tests**: Add screenshot comparison
5. **API Contract Tests**: Add OpenAPI schema validation

## 📚 Additional Resources

- [Cypress Documentation](https://docs.cypress.io/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Next.js Testing](https://nextjs.org/docs/testing)
- [Docker Compose Testing](https://docs.docker.com/compose/compose-file/)

## 🧪 Frontend Unit Tests

The frontend includes comprehensive unit testing using Jest and React Testing Library. For detailed information about frontend testing, see the [Frontend Testing Guide](../frontend/TESTING.md).

### Quick Start

```bash
# Run all tests (includes frontend unit tests and linting)
./scripts/run-tests.sh
```

The script automatically runs frontend linting, unit tests, backend tests, and E2E tests.

### Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── __tests__/
│   │   │   └── Navbar.test.tsx
│   │   └── Navbar.tsx
│   ├── lib/
│   │   ├── __tests__/
│   │   │   ├── auth.test.ts
│   │   │   └── utils.test.ts
│   │   ├── auth.tsx
│   │   ├── utils.ts
│   │   └── test-utils.tsx
│   └── app/
│       └── __tests__/
│           └── (page tests)
├── jest.config.js
├── jest.setup.js
└── package.json
```

### Testing Stack

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **@testing-library/jest-dom**: Custom Jest matchers for DOM testing
- **@testing-library/user-event**: User interaction simulation

### Coverage Goals

- **Lines**: 70% minimum
- **Functions**: 70% minimum
- **Branches**: 70% minimum
- **Statements**: 70% minimum

For comprehensive frontend testing documentation, examples, and best practices, see [Frontend Testing Guide](../frontend/TESTING.md).

---

For questions or issues with testing, please refer to the [`cypress/README.md`](../cypress/README.md) file or contact the development team.
