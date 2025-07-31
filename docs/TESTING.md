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

### Test Scenarios

#### 1. API Tests ([e2e/tests/01-api-tests.cy.ts](../cypress/e2e/tests/01-api-tests.cy.ts))

Tests all backend API endpoints:

```typescript
describe("API Endpoints", () => {
  it("Should handle user registration via API", () => {
    const userData = {
      email: `api-test-${Date.now()}@example.com`,
      password1: "TestPassword123!",
      password2: "TestPassword123!",
      name: "API Test User",
    };

    cy.request("POST", "/api/accounts/signup/", userData).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property("message");
      expect(response.body).to.have.property("user_id");
    });
  });
});
```

#### 2. Token Tests ([e2e/tests/02-token-tests.cy.ts](../cypress/e2e/tests/02-token-tests.cy.ts))

Tests email verification and password reset token functionality:

```typescript
describe("Token Testing", () => {
  it("Should get email verification and password reset tokens for testing", () => {
    // Test token retrieval for testing email-dependent flows
    cy.getTestTokens("testuser1@example.com").then((tokens) => {
      expect(tokens.email_verification_token).to.be.a("string");
      expect(tokens.password_reset_token).to.be.a("string");
    });
  });
});
```

#### 3. Signup Journey ([e2e/tests/03-signup-journey.cy.ts](../cypress/e2e/tests/03-signup-journey.cy.ts))

Tests the complete signup and email verification flow:

```typescript
describe("Signup Journey", () => {
  it("Complete signup journey: signup, verify email, signin", () => {
    // 1. Sign up new user
    cy.visit("/auth/signup");
    cy.get('input[id="name"]').type("Test User");
    cy.get('input[id="email"]').type("newuser@example.com");
    cy.get('input[id="password1"]').type("password123");
    cy.get('input[id="password2"]').type("password123");
    cy.get('button[type="submit"]').click();

    // 2. Verify email
    cy.getTestTokens("newuser@example.com").then((tokens) => {
      cy.visit(`/auth/verify-email/${tokens.email_verification_token}`);
    });

    // 3. Sign in
    cy.visit("/auth/signin");
    cy.get('input[id="email"]').type("newuser@example.com");
    cy.get('input[id="password"]').type("password123");
    cy.get('button[type="submit"]').click();
  });
});
```

#### 4. Password Reset Journey ([e2e/tests/04-password-reset-journey.cy.ts](../cypress/e2e/tests/04-password-reset-journey.cy.ts))

Tests the password reset workflow:

```typescript
describe("Password Reset Journey", () => {
  it("Complete password reset journey: forgot password, get tokens, change password, signin", () => {
    // 1. Sign in with existing user
    cy.visit("/auth/signin");
    cy.get('input[id="email"]').type("testuser1@example.com");
    cy.get('input[id="password"]').type("testpass123");
    cy.get('button[type="submit"]').click();

    // 2. Request password reset
    cy.request("POST", "/api/accounts/forgot-password/", {
      email: "testuser1@example.com",
    });

    // 3. Get reset token and change password
    cy.getTestTokens("testuser1@example.com").then((tokens) => {
      cy.visit(`/auth/reset-password/${tokens.password_reset_token}`);
      cy.get('input[id="password1"]').type("newpassword123");
      cy.get('input[id="password2"]').type("newpassword123");
      cy.get('button[type="submit"]').click();
    });

    // 4. Sign in with new password
    cy.visit("/auth/signin");
    cy.get('input[id="email"]').type("testuser1@example.com");
    cy.get('input[id="password"]').type("newpassword123");
    cy.get('button[type="submit"]').click();
  });
});
```

#### 5. Profile Journey ([e2e/tests/05-profile-journey.cy.ts](../cypress/e2e/tests/05-profile-journey.cy.ts))

Tests profile management and updates:

```typescript
describe("Profile Management Journey", () => {
  it("Complete profile journey: signin, update profile, change bank account", () => {
    // 1. Sign in with existing user
    cy.visit("/auth/signin");
    cy.get('input[id="email"]').type("testuser1@example.com");
    cy.get('input[id="password"]').type("testpass123");
    cy.get('button[type="submit"]').click();

    // 2. Update profile
    cy.visit("/profile");
    cy.get('input[id="bankaccount"]').clear().type("NL91ABNA0417164300");
    cy.get('button[type="submit"]').click();

    // 3. Sign out
    cy.get('[data-testid="user-menu"]').click();
    cy.get('[data-testid="sign-out"]').click();
    cy.url().should("include", "/auth/signin");
  });
});
```

#### 6. Ballot Journey ([e2e/tests/06-ballot-journey.cy.ts](../cypress/e2e/tests/06-ballot-journey.cy.ts))

Tests ballot purchase and assignment:

```typescript
describe("Ballot Journey", () => {
  it("Complete ballot journey: signin, buy ballots", () => {
    // 1. Sign in with existing user
    cy.visit("/auth/signin");
    cy.get('input[id="email"]').type("testuser1@example.com");
    cy.get('input[id="password"]').type("testpass123");
    cy.get('button[type="submit"]').click();

    // 2. Buy ballots
    cy.visit("/my-ballots");
    cy.contains("Purchase New Ballots").click();
    cy.get('input[name="quantity"]').type("3");
    cy.get('input[name="card_number"]').type("1234567890123456");
    cy.get('input[name="expiry_month"]').type("12");
    cy.get('input[name="expiry_year"]').type("2025");
    cy.get('input[name="cvv"]').type("123");
    cy.get('button[type="submit"]').click();

    // 3. Sign out
    cy.get('[data-testid="user-menu"]').click();
    cy.get('[data-testid="sign-out"]').click();
    cy.url().should("include", "/auth/signin");
  });
});
```

#### 7. Closed Draws Journey ([e2e/tests/07-closed-draws-journey.cy.ts](../cypress/e2e/tests/07-closed-draws-journey.cy.ts))

Tests viewing closed draws and results:

```typescript
describe("Closed Draws Journey", () => {
  it("Complete closed draws journey: signin, view closed draws", () => {
    // 1. Sign in with existing user
    cy.visit("/auth/signin");
    cy.get('input[id="email"]').type("testuser1@example.com");
    cy.get('input[id="password"]').type("testpass123");
    cy.get('button[type="submit"]').click();

    // 2. View closed draws
    cy.visit("/draws/closed");
    cy.get('[data-testid="closed-draw"]').should("have.length.at.least", 1);

    // 3. Sign out
    cy.get('[data-testid="user-menu"]').click();
    cy.get('[data-testid="sign-out"]').click();
    cy.url().should("include", "/auth/signin");
  });
});
```

#### 8. User Journey Overview (08-user-journey.cy.ts)

Overview test that verifies all user journeys are working:

```typescript
describe("Lottery User Journeys", () => {
  it("Should have all user journeys working", () => {
    // This test verifies that all user journeys are properly configured
    // and the test environment is working correctly
    cy.visit("/");
    cy.get("body").should("contain", "Lottery System");
  });
});
```

### Custom Commands

The test suite includes custom Cypress commands for common operations:

```typescript
// User management
cy.signUp(email, password, name);
cy.signIn(email, password);
cy.signOut();

// Ballot operations
cy.buyBallots(quantity);
cy.assignBallot(drawId);

// Test utilities
cy.clearDatabase();
cy.seedTestData();
cy.waitForApi();
cy.isAuthenticated();
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
