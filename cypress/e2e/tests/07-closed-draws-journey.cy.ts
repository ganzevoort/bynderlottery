describe('Closed Draws Journey', () => {
    const testUser = {
        name: 'Test User 1',
        email: 'testuser1@example.com',
        password: 'testpass123'
    };

    beforeEach(() => {
        cy.clearDatabase();
        cy.seedTestData();
        cy.waitForTestEnv();
    });

    it('Complete closed draws journey: signin, view closed draws', () => {
        // Step 1: Sign in with pre-seeded user
        cy.visit('/auth/signin')
        cy.get('input[name="email"]').type(testUser.email)
        cy.get('input[name="password"]').type(testUser.password)
        cy.get('button[type="submit"]').click()

        // Wait for signin to complete and check for success message
        cy.wait(3000)
        cy.get('div').contains('Successfully signed in!').should('be.visible')

        // Step 2: Navigate to closed draws page and verify UI
        cy.visit('/draws/closed')

        // Verify the page loads and shows closed draws
        cy.get('h1').contains('Past Results').should('be.visible')

        // Check that closed draws are displayed (at least one should exist)
        cy.get('[data-testid="closed-draw"]').should('have.length.greaterThan', 0)

        // Verify we can see winner information
        cy.contains('Winners').should('be.visible')

        // Step 3: Sign out using user menu
        cy.get('[data-testid="user-menu"]').click()
        cy.get('button').contains('Sign Out').click()

        // Should redirect to signin page
        cy.url().should('include', '/auth/signin')
    });
});
