describe('Signup Journey', () => {
    const testUser = {
        name: 'Signup Test User',
        email: 'signup-test@example.com',
        password: 'password123'
    };

    beforeEach(() => {
        cy.clearDatabase();
        cy.seedTestData();
        cy.waitForTestEnv();
    });

    it('Complete signup journey: signup, verify email, signin', () => {
        // Step 1: Visit home page
        cy.visit('/')
        cy.contains('Welcome to the Lottery System').should('be.visible')
        cy.contains('Get Started').should('be.visible')

        // Step 2: Sign up
        cy.visit('/auth/signup')
        cy.get('input[name="name"]').type(testUser.name)
        cy.get('input[name="email"]').type(testUser.email)
        cy.get('input[name="password1"]').type(testUser.password)
        cy.get('input[name="password2"]').type(testUser.password)
        cy.get('button[type="submit"]').click()

        // Should show success message
        cy.contains('Account created successfully').should('be.visible')
        cy.contains('Please check your email to verify your account').should('be.visible')

        // Step 3: Get tokens and verify email via UI
        cy.getTestTokens(testUser.email).then((response) => {
            expect(response.status).to.eq(200)
            const emailToken = response.body.email_verification_token

            // Visit email verification page with the token
            cy.visit(`/auth/verify-email/${emailToken}`)
            cy.contains('Email verified successfully').should('be.visible')
        })

        // Step 4: Sign in (after email verification)
        cy.visit('/auth/signin')
        cy.get('input[id="email"]').type(testUser.email)
        cy.get('input[id="password"]').type(testUser.password)
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
