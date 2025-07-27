# Cypress Integration Tests for Lottery System

This directory contains comprehensive integration tests for the Lottery System using Cypress.

## 🚀 Quick Start

### Running Tests

1. **Start the application:**
   ```bash
   docker compose up -d
   ```

2. **Run all tests:**
   ```bash
   docker compose run cypress
   ```

3. **Run specific test suites:**
   ```bash
   # API tests
   docker compose run cypress cypress run --spec 'cypress/e2e/01-api-tests.cy.ts'
   
   # Token tests
   docker compose run cypress cypress run --spec 'cypress/e2e/02-token-tests.cy.ts'
   
   # Signup journey
   docker compose run cypress cypress run --spec 'cypress/e2e/03-signup-journey.cy.ts'
   
   # Password reset journey
   docker compose run cypress cypress run --spec 'cypress/e2e/04-password-reset-journey.cy.ts'
   
   # Profile journey
   docker compose run cypress cypress run --spec 'cypress/e2e/05-profile-journey.cy.ts'
   
   # Ballot journey
   docker compose run cypress cypress run --spec 'cypress/e2e/06-ballot-journey.cy.ts'
   
   # Closed draws journey
   docker compose run cypress cypress run --spec 'cypress/e2e/07-closed-draws-journey.cy.ts'
   
   # Complete demo journey
   docker compose run cypress cypress run --spec 'cypress/e2e/99-demo.cy.ts'
   ```

4. **Run tests in interactive mode:**
   ```bash
   docker compose run -it cypress cypress open
   ```

## 📁 Test Structure

```
cypress/
├── cypress.config.ts          # Cypress configuration
├── support/
│   ├── e2e.ts                # Global test setup and custom commands
│   └── commands.ts           # Custom Cypress commands
├── e2e/
│   ├── 01-api-tests.cy.ts              # API endpoint validation
│   ├── 02-token-tests.cy.ts            # Email verification and password reset tokens
│   ├── 03-signup-journey.cy.ts         # Complete signup and email verification flow
│   ├── 04-password-reset-journey.cy.ts # Password reset workflow
│   ├── 05-profile-journey.cy.ts        # Profile management and updates
│   ├── 06-ballot-journey.cy.ts         # Ballot purchase and assignment
│   ├── 07-closed-draws-journey.cy.ts   # Viewing closed draws and results
│   └── 99-demo.cy.ts                   # Complete demo journey for product owner
└── README.md                           # This file
```

## 🧪 Test Scenarios

### API Tests (01-api-tests.cy.ts)

Tests all backend API endpoints:

1. **Authentication APIs**
   - User registration
   - User signin
   - Profile management

2. **Lottery APIs**
   - Statistics retrieval
   - Open draws listing
   - Closed draws with winners
   - Ballot purchase
   - Ballot assignment

3. **Data Integrity**
   - Response format validation
   - Status code verification
   - Data consistency checks

### Token Tests (02-token-tests.cy.ts)

Tests email verification and password reset token functionality:

1. **Token Retrieval**
   - Get email verification tokens
   - Get password reset tokens
   - Handle non-existent users gracefully

2. **Token Usage**
   - Email verification flow
   - Password reset flow

### Signup Journey (03-signup-journey.cy.ts)

Tests the complete signup and email verification flow:

1. **User Registration**
   - Sign up with valid credentials
   - Form validation (empty fields, password mismatch)
   - Success message verification

2. **Email Verification**
   - Retrieve verification token
   - Complete email verification
   - Sign in after verification

### Password Reset Journey (04-password-reset-journey.cy.ts)

Tests the password reset workflow:

1. **Password Reset Request**
   - Request password reset via API
   - Retrieve reset token
   - Change password with token

2. **Password Change**
   - Validate new password
   - Sign in with new password

### Profile Journey (05-profile-journey.cy.ts)

Tests profile management and updates:

1. **Profile Updates**
   - Update user profile information
   - Bank account management
   - Form validation

2. **Authentication**
   - Sign in with existing user
   - Sign out with redirect

### Ballot Journey (06-ballot-journey.cy.ts)

Tests ballot purchase and assignment:

1. **Ballot Purchase**
   - Purchase ballots with payment simulation
   - Form validation
   - Success confirmation

2. **User Flow**
   - Sign in with existing user
   - Navigate to ballot purchase
   - Sign out with redirect

### Closed Draws Journey (07-closed-draws-journey.cy.ts)

Tests viewing closed draws and results:

1. **Draw Results**
   - View closed draws
   - Check for winners
   - Verify draw information

2. **User Flow**
   - Sign in with existing user
   - Navigate to closed draws
   - Sign out with redirect

### Complete Demo Journey (99-demo.cy.ts)

Comprehensive demo test that showcases the complete user journey for product owners:

1. **Complete User Flow**
   - User signup and email verification
   - Password reset workflow
   - Profile management
   - Ballot purchase and assignment
   - Draw browsing and results viewing

2. **System Showcase**
   - All major features demonstrated
   - End-to-end user experience
   - Success message verification
   - Data consistency checks

## 🛠️ Custom Commands

The following custom commands are available in tests:

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
cy.getTestTokens(email)
```

## 🔧 Configuration

### Environment Variables

- `CYPRESS_baseUrl`: Set to `http://web:80` (nginx proxy)
- `CYPRESS_video`: Disabled for faster runs
- `CYPRESS_screenshotOnRunFailure`: Disabled

### Test Data

Tests use a dedicated test database that gets cleared and reseeded between test runs:

- **Test Users**: `testuser1@example.com`, `testuser2@example.com`, `winner@example.com`
- **Test Draws**: Daily and weekly draws (open and closed)
- **Test Ballots**: Assigned and unassigned ballots for testing

### Database Management

The backend provides test endpoints for database management:

- `POST /api/lottery/test/clear-database/` - Clear all test data
- `POST /api/lottery/test/seed-data/` - Seed fresh test data
- `GET /api/lottery/test/health-check/` - Health check endpoint

## 📊 Test Reports

Cypress generates detailed test reports including:

- **Video recordings** (disabled for performance)
- **Screenshots** on failure (disabled)
- **Console logs** for debugging
- **Test execution times**

## 🐛 Debugging

### Common Issues

1. **Tests failing due to timing:**
   - Increase `defaultCommandTimeout` in `cypress.config.ts`
   - Add explicit waits for API responses

2. **Database state issues:**
   - Ensure `clearDatabase()` is called in `beforeEach`
   - Check that test data is properly seeded

3. **Authentication problems:**
   - Verify session cookies are properly handled
   - Check that user accounts are created correctly

### Debug Commands

```bash
# Run single test with verbose output
docker compose run cypress cypress run --spec 'cypress/e2e/user-journey.cy.ts' --headed

# Open Cypress in interactive mode
docker compose run -it cypress cypress open

# Check test data in database
docker compose exec backend python manage.py shell
```

## 🔄 Continuous Integration

The Cypress tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Cypress Tests
  run: |
    docker compose up -d
    docker compose run cypress
```

## 📈 Best Practices

1. **Test Isolation**: Each test clears and reseeds the database
2. **Realistic Data**: Tests use realistic user scenarios
3. **Error Handling**: Tests verify both success and error cases
4. **Performance**: Tests are optimized for speed (no videos/screenshots)
5. **Maintainability**: Custom commands reduce code duplication

## 🎯 Test Coverage

The tests cover:

- ✅ User registration and authentication
- ✅ Ballot purchase and assignment
- ✅ Draw browsing and results viewing
- ✅ Profile management
- ✅ Form validation and error handling
- ✅ API endpoint functionality
- ✅ Database operations
- ✅ Session management

## 🚀 Next Steps

To extend the test suite:

1. Add more edge cases and error scenarios
2. Test mobile responsiveness
3. Add performance tests
4. Test email functionality
5. Add accessibility tests 
