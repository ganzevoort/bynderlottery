describe('Password Reset Journey', () => {
    const testUser = {
        name: 'Test User 1',
        email: 'testuser1@example.com',
        password: 'testpass123',
        newPassword: 'newpassword123'
    };

    beforeEach(() => {
        cy.clearDatabase();
        cy.seedTestData();
        cy.waitForTestEnv();
    });

    it('Complete password reset journey: forgot password, get tokens, change password, signin', () => {
        // Step 1: Go to forgot password page
        cy.visit('/auth/forgot-password')
        cy.get('input[name="email"]').type(testUser.email)
        cy.get('button[type="submit"]').click()

        // Should show success message
        cy.contains('If an account with that email exists, you will receive a password reset link shortly.').should('be.visible')

        // Step 2: Get password reset token and change password
        cy.getTestTokens(testUser.email).then((response) => {
            expect(response.status).to.eq(200)
            const passwordToken = response.body.password_reset_token

            // Visit password reset page with the token
            cy.visit(`/auth/reset-password/${passwordToken}`)
            cy.get('input[name="password"]').type(testUser.newPassword)
            cy.get('input[name="confirmPassword"]').type(testUser.newPassword)
            cy.get('button[type="submit"]').click()

            // Should show success message
            cy.contains('Password reset successfully! You can now sign in with your new password.').should('be.visible')
        })

        // Step 3: Sign in with new password
        cy.visit('/auth/signin')
        cy.get('input[name="email"]').type(testUser.email)
        cy.get('input[name="password"]').type(testUser.newPassword)
        cy.get('button[type="submit"]').click()

        // Wait for signin to complete and check for success message
        cy.wait(3000)
        cy.get('div').contains('Successfully signed in!').should('be.visible')

        // Should redirect to home page after successful signin
        cy.url().should('eq', 'http://web/')

        // Verify user is authenticated by checking if we can access protected pages
        cy.visit('/my-ballots')
        cy.url().should('include', '/my-ballots')
    });
});
