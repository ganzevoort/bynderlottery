describe('Profile Management Journey', () => {
    const testUser = {
        name: 'User 1',
        email: 'testuser1@example.com',
        password: 'testpass123'
    };

    beforeEach(() => {
        cy.clearDatabase();
        cy.seedTestData();
        cy.waitForTestEnv();
    });

    it('Complete profile journey: signin, update profile, change bank account', () => {
        // Step 1: Sign in with pre-seeded user
        cy.visit('/auth/signin')
        cy.get('input[id="email"]').type(testUser.email)
        cy.get('input[id="password"]').type(testUser.password)
        cy.get('button[type="submit"]').click()

        // Wait for signin to complete and check for success message
        cy.wait(3000)
        cy.get('body').should('contain', 'Successfully signed in!')

        // Step 2: Update profile
        cy.visit('/profile')
        cy.contains('Profile Settings').should('be.visible')

        // Clear and type the bank account
        cy.get('input[id="bankaccount"]').clear().type('NL91ABNA0417164300')

        // Submit the form
        cy.get('button[type="submit"]').click()

        // Wait for the update to complete
        cy.wait(3000)

        // Step 3: Verify profile was updated by checking the input value
        cy.get('input[id="bankaccount"]').should('have.value', 'NL91ABNA0417164300')
        cy.url().should('include', '/profile')

        // Step 4: Sign out using user menu
        cy.get('[data-testid="user-menu"]').click()
        cy.get('button').contains('Sign Out').click()

        // Should redirect to signin page
        cy.url().should('include', '/auth/signin')
    });
});
