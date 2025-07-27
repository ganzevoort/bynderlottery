// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Helper function to get CSRF token
Cypress.Commands.add('getCSRFToken', () => {
  return cy.getCookie('csrftoken').then((cookie) => {
    return cookie ? cookie.value : null
  })
})

// Custom command to sign up a new user
Cypress.Commands.add('signUp', (email, password, name) => {
  cy.visit('/auth/signup')
  
  // Fill in the signup form
  cy.get('input[name="name"]').type(name)
  cy.get('input[name="email"]').type(email)
  cy.get('input[name="password1"]').type(password)
  cy.get('input[name="password2"]').type(password)
  
  // Submit the form
  cy.get('button[type="submit"]').click()
  
  // Should show success message
  cy.contains('Account created successfully').should('be.visible')
  
  // Verify the user programmatically for testing
  cy.request('POST', '/api/test/verify-user/', { email })
})

// Custom command to sign in a user
Cypress.Commands.add('signIn', (email, password) => {
  cy.visit('/auth/signin')
  
  // Fill in the signin form
  cy.get('input[name="email"]').type(email)
  cy.get('input[name="password"]').type(password)
  
  // Submit the form
  cy.get('button[type="submit"]').click()
  
  // Should redirect to home page
  cy.url().should('eq', 'http://web/')
  
  // Verify user is authenticated by checking API directly
  cy.request('GET', '/api/accounts/profile/').then((response) => {
    expect(response.status).to.eq(200)
  })
})

// Custom command to sign out
Cypress.Commands.add('signOut', () => {
  // Click on user menu and sign out
  cy.get('[data-testid="user-menu"]').click()
  cy.get('[data-testid="sign-out"]').click()
  
  // Should redirect to home page
  cy.url().should('eq', 'http://web/')
})

// Custom command to buy ballots
Cypress.Commands.add('buyBallots', (quantity) => {
  cy.visit('/my-ballots')
  
  // Expand the purchase section
  cy.contains('Purchase New Ballots').click()
  
  // Fill in the purchase form
  cy.get('input[name="quantity"]').type(quantity.toString())
  cy.get('input[name="card_number"]').type('1234567890123456')
  cy.get('input[name="expiry_month"]').type('12')
  cy.get('input[name="expiry_year"]').type('2025')
  cy.get('input[name="cvv"]').type('123')
  
  // Submit the form
  cy.get('button[type="submit"]').click()
  
  // Should show success message
  cy.contains('Successfully purchased').should('be.visible')
})

// Custom command to assign ballot to a draw
Cypress.Commands.add('assignBallot', (drawId) => {
  cy.visit('/my-ballots')
  
  // Find an unassigned ballot and assign it
  cy.get('[data-testid="unassigned-ballot"]').first().within(() => {
    cy.get('[data-testid="assign-button"]').click()
    cy.get('select').select(drawId.toString())
    cy.get('button[type="submit"]').click()
  })
  
  // Should show success message
  cy.contains('Ballot assigned successfully').should('be.visible')
})

// Override visit command to wait for page load
Cypress.Commands.overwrite('visit', (originalFn, url, options) => {
  return originalFn(url, {
    ...options,
    timeout: 30000,
  })
})

// Custom command to wait for API requests to complete
Cypress.Commands.add('waitForApi', () => {
  cy.wait('@api', { timeout: 10000 })
})

// Custom command to check if user is authenticated
Cypress.Commands.add('isAuthenticated', () => {
  cy.get('body').then(($body) => {
    return $body.find('[data-testid="user-menu"]').length > 0
  })
})

// Custom command to clear database (for test isolation)
Cypress.Commands.add('clearDatabase', () => {
  cy.request('POST', '/api/test/clear-database/')
})

// Custom command to seed test data
Cypress.Commands.add('seedTestData', () => {
  cy.request('POST', '/api/test/seed-data/')
})

// Custom command to wait for test environment to be ready
Cypress.Commands.add('waitForTestEnv', () => {
  // Wait for backend to be ready
  cy.request('GET', '/api/test/health-check/').then((response) => {
    expect(response.status).to.eq(200)
  })
})

// Custom command to setup test data
Cypress.Commands.add('setupTestData', () => {
  cy.clearDatabase()
  cy.seedTestData()
  cy.waitForTestEnv()
})

// Custom command to get test tokens for an email
Cypress.Commands.add('getTestTokens', (email) => {
  return cy.request('POST', '/api/test/get-tokens/', { email })
}) 
