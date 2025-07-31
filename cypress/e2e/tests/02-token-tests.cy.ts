describe('Token Testing', () => {
    const testUser = {
        name: 'Token Test User',
        email: 'token-test@example.com',
        password: 'password123'
    };

    beforeEach(() => {
        // Clear database and seed test data
        cy.clearDatabase();
        cy.seedTestData();
        cy.waitForTestEnv();
    });

    it('Should get email verification and password reset tokens for testing', () => {
        // Step 1: Create a user via signup
        cy.visit('/auth/signup')
        cy.get('input[name="name"]').type(testUser.name)
        cy.get('input[name="email"]').type(testUser.email)
        cy.get('input[name="password1"]').type(testUser.password)
        cy.get('input[name="password2"]').type(testUser.password)
        cy.get('button[type="submit"]').click()

        // Should show success message
        cy.contains('Account created successfully').should('be.visible')

        // Step 2: Generate password reset token via forgot-password endpoint
        cy.request('POST', '/api/accounts/forgot-password/', {
            email: testUser.email
        }).then((forgotResponse) => {
            expect(forgotResponse.status).to.eq(200)
        })

        // Step 3: Get tokens for testing
        cy.getTestTokens(testUser.email).then((response) => {
            expect(response.status).to.eq(200)
            expect(response.body).to.have.property('email_verification_token')
            expect(response.body).to.have.property('password_reset_token')
            expect(response.body.email_verification_token).to.be.a('string')
            expect(response.body.password_reset_token).to.be.a('string')

            // Store tokens for later use
            const emailToken = response.body.email_verification_token
            const passwordToken = response.body.password_reset_token

            // Step 4: Test email verification using the token (frontend URL)
            cy.visit(`/auth/verify-email/${emailToken}`)
            cy.contains('Email verified successfully').should('be.visible')

            // Step 5: Test password reset using the token (frontend URL)
            cy.visit(`/auth/reset-password/${passwordToken}`)
            cy.get('input[name="password"]').type('newpassword123')
            cy.get('input[name="confirmPassword"]').type('newpassword123')
            cy.get('button[type="submit"]').click()
            cy.contains('Password reset successfully! You can now sign in with your new password.').should('be.visible')
        })
    })

    it('Should handle token generation for existing users', () => {
        // First create a user
        cy.visit('/auth/signup')
        cy.get('input[name="name"]').type(testUser.name)
        cy.get('input[name="email"]').type(testUser.email)
        cy.get('input[name="password1"]').type(testUser.password)
        cy.get('input[name="password2"]').type(testUser.password)
        cy.get('button[type="submit"]').click()

	cy.wait(1000)
        // Get tokens multiple times to ensure they're generated
        cy.getTestTokens(testUser.email).then((firstResponse) => {
            expect(firstResponse.status).to.eq(200)
            const firstEmailToken = firstResponse.body.email_verification_token
            const firstPasswordToken = firstResponse.body.password_reset_token

            // Get tokens again - should return the same tokens
            cy.getTestTokens(testUser.email).then((secondResponse) => {
                expect(secondResponse.status).to.eq(200)
                expect(secondResponse.body.email_verification_token).to.eq(firstEmailToken)
                expect(secondResponse.body.password_reset_token).to.eq(firstPasswordToken)
            })
        })
    })

    it('Should handle non-existent user gracefully', () => {
        cy.request({
            method: 'POST',
            url: '/api/test/get-tokens/',
            body: { email: 'nonexistent@example.com' },
            failOnStatusCode: false
        }).then((response) => {
            expect(response.status).to.eq(404)
            expect(response.body).to.have.property('error', 'User not found')
        })
    })
})
