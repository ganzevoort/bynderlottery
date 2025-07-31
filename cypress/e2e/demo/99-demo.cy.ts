describe('Lottery System - Complete User Journey Demo', () => {
    beforeEach(() => {
        cy.clearDatabase();
        cy.seedTestData();
        cy.waitForTestEnv();
    });

    it('Complete user journey: signup - verify - forgotpassword - resetpassword - signin - profile - open draws - closed draws - ballot purchase - allocate', () => {
        // ===== STEP 1: SIGNUP =====
        cy.log('=== Step 1: User Signup ===')

        const newUser = {
            name: 'Signup Test User',
            email: 'signup-test@example.com',
            password: 'password123'
        };

        // Visit home page
        cy.visit('/')
        cy.contains('Welcome to the Lottery System').should('be.visible')

        // Sign up new user
        cy.visit('/auth/signup')
        cy.get('input[name="name"]').type(newUser.name)
        cy.get('input[name="email"]').type(newUser.email)
        cy.get('input[name="password1"]').type(newUser.password)
        cy.get('input[name="password2"]').type(newUser.password)
        cy.get('button[type="submit"]').click()

        // Should show success message
        cy.contains('Account created successfully').should('be.visible')
        cy.contains('Please check your email to verify your account').should('be.visible')

        // ===== STEP 2: EMAIL VERIFICATION =====
        cy.log('=== Step 2: Email Verification ===')

        // Get tokens and verify email via UI
        cy.getTestTokens(newUser.email).then((response) => {
            expect(response.status).to.eq(200)
            const emailToken = response.body.email_verification_token

            // Visit email verification page with the token
            cy.visit(`/auth/verify-email/${emailToken}`)
            cy.contains('Email verified successfully').should('be.visible')
        })

        // ===== STEP 3: FORGOT PASSWORD =====
        cy.log('=== Step 3: Forgot Password ===')

        // Go to forgot password page
        cy.visit('/auth/forgot-password')
        cy.get('input[name="email"]').type(newUser.email)
        cy.get('button[type="submit"]').click()

        // Verify success message
        cy.contains('If an account with that email exists, you will receive a password reset link shortly.').should('be.visible')

        // ===== STEP 4: PASSWORD RESET =====
        cy.log('=== Step 4: Password Reset ===')

        // Get password reset token and change password
        cy.getTestTokens(newUser.email).then((response) => {
            expect(response.status).to.eq(200)
            const passwordToken = response.body.password_reset_token

            // Visit password reset page with the token
            cy.visit(`/auth/reset-password/${passwordToken}`)
            cy.get('input[name="password"]').type('newpassword123')
            cy.get('input[name="confirmPassword"]').type('newpassword123')
            cy.get('button[type="submit"]').click()

            // Verify success message
            cy.contains('Password reset successfully! You can now sign in with your new password.').should('be.visible')
        })

        // ===== STEP 5: SIGN IN =====
        cy.log('=== Step 5: Sign In ===')

        // Sign in with new password
        cy.visit('/auth/signin')
        cy.get('input[id="email"]').type(newUser.email)
        cy.get('input[id="password"]').type('newpassword123')
        cy.get('button[type="submit"]').click()

        // Wait for signin to complete
        cy.wait(3000)
        cy.get('div').contains('Successfully signed in!').should('be.visible')
        cy.url().should('eq', 'http://web/')

        // ===== STEP 6: PROFILE MANAGEMENT =====
        cy.log('=== Step 6: Profile Management ===')

        // Update profile
        cy.visit('/profile')
        cy.contains('Profile Settings').should('be.visible')

        // Update bank account
        cy.get('input[id="bankaccount"]').clear().type('NL91ABNA0417164300')
        cy.get('button[type="submit"]').click()

        // Wait for the update to complete
        cy.wait(3000)

        // Verify profile was updated
        cy.get('input[id="bankaccount"]').should('have.value', 'NL91ABNA0417164300')

        // ===== STEP 7: OPEN DRAWS =====
        cy.log('=== Step 7: View Open Draws ===')

        // Visit open draws page
        cy.visit('/draws')
        cy.get('[data-testid="draw-card"]').should('have.length.at.least', 1)

        // ===== STEP 8: CLOSED DRAWS =====
        cy.log('=== Step 8: View Closed Draws ===')

        // Visit closed draws page
        cy.visit('/draws/closed')
        cy.get('[data-testid="closed-draw"]').should('have.length.at.least', 1)

        // ===== STEP 9: BALLOT PURCHASE =====
        cy.log('=== Step 9: Ballot Purchase ===')

        // Purchase ballots via UI
        cy.visit('/my-ballots')
        cy.wait(3000)
        cy.url().should('include', '/my-ballots')

        cy.contains('Purchase New Ballots').click()

        // Fill in the purchase form
        cy.get('input[name="quantity"]').type('3')
        cy.get('input[name="card_number"]').type('1234567890123456')
        cy.get('input[name="expiry_month"]').type('12')
        cy.get('input[name="expiry_year"]').type('2025')
        cy.get('input[name="cvv"]').type('123')

        // Submit the form
        cy.get('button[type="submit"]').click()

        // Wait for response and check for success
        cy.wait(3000)
        cy.get('div').contains('ballots').should('be.visible')

        // ===== STEP 10: BALLOT ALLOCATION =====
        cy.log('=== Step 10: Ballot Allocation ===')

        // Check that we have unassigned ballots (0 from seed + 3 purchased = 3)
        cy.get('[data-testid="unassigned-ballots-title"]').should('contain', '3')

        // Expand the unassigned ballots section to see the form
        cy.get('[data-testid="unassigned-ballots-title"]').click()

        // Verify the assignment form is visible
        cy.get('select[name="draw_id"]').should('be.visible')
        cy.get('select[name="draw_id"] option').should('have.length.at.least', 2) // At least 1 option + placeholder
        cy.get('input[name="quantity"]').should('be.visible')
        cy.get('input[name="quantity"]').should('have.value', '1')

        // Select a draw from the dropdown
        cy.get('select[name="draw_id"]').select('1')

        // Set quantity to 2
        cy.get('input[name="quantity"]').clear().type('2')

        // Submit the assignment
        cy.get('[data-testid="assign-button"]').click()

        // Wait for response
        cy.wait(3000)

        // Check for success message
        cy.contains('successfully').should('be.visible')

        // Verify the unassigned count has decreased from 3 to 1
        cy.get('[data-testid="unassigned-ballots-title"]').should('contain', '1')

        // Verify the assigned count has increased from 0 to 2
        cy.get('[data-testid="assigned-ballots-title"]').should('contain', '2')

        cy.log('=== Complete User Journey Demo Finished Successfully ===')
    });
});
