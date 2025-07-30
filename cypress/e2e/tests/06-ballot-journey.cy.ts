describe('Ballot Journey', () => {
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

    it('Complete ballot journey: signin, buy ballots, assign ballots', () => {
        // Step 1: Sign in with pre-seeded user
        cy.visit('/auth/signin')
        cy.get('input[name="email"]').type(testUser.email)
        cy.get('input[name="password"]').type(testUser.password)
        cy.get('button[type="submit"]').click()

        // Wait for signin to complete and check for success message
        cy.wait(3000)
        cy.get('div').contains('Successfully signed in!').should('be.visible')

        // Step 2: Purchase ballots via UI
        cy.visit('/my-ballots')

        // Wait for the page to load and check if we're on the correct page
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

        // Wait for response and check for any toast message
        cy.wait(3000)
        cy.get('div').contains('ballots').should('be.visible')

        // Step 3: Test ballot assignment functionality
        cy.log('=== Testing Ballot Assignment ===')

        // Check if we have unassigned ballots
        cy.get('[data-testid="unassigned-ballots-title"]').should('be.visible')

        // Check that we have unassigned ballots (5 from seed + 3 purchased = 8)
        cy.get('[data-testid="unassigned-ballots-title"]').should('contain', '8')

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

        // Verify the assign button is enabled
        cy.get('[data-testid="assign-button"]').should('be.visible')

        // Submit the assignment
        cy.get('[data-testid="assign-button"]').click()

        // Wait for response
        cy.wait(3000)

        // Check for success message
        cy.contains('successfully').should('be.visible')

        // Verify the unassigned count has decreased from 8 to 6
        cy.get('[data-testid="unassigned-ballots-title"]').should('contain', '6')

        // Verify the assigned count has increased from 0 to 2
        cy.get('[data-testid="assigned-ballots-title"]').should('contain', '2')

        // Verify the form is closed
        cy.contains('Assign Ballot to Draw').should('not.exist')

        // Step 4: Sign out using user menu (works on all screen sizes)
        cy.get('[data-testid="user-menu"]').click()
        cy.get('button').contains('Sign Out').click()

        // Should redirect to signin page
        cy.url().should('include', '/auth/signin')
    });
}); 
