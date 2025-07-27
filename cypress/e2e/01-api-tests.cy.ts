describe('API Endpoints', () => {
    beforeEach(() => {
        // Setup test environment with fresh data
        cy.setupTestData()
    })

    it('Should handle user registration via API', () => {
        const userData = {
            email: `api-test-${Date.now()}@example.com`,
            password1: 'TestPassword123!',
            password2: 'TestPassword123!',
            name: 'API Test User'
        }

        cy.request('POST', '/api/accounts/signup/', userData).then((response) => {
            expect(response.status).to.eq(201)
            expect(response.body).to.have.property('message')
            expect(response.body).to.have.property('user_id')
        })
    })

    it('Should handle user authentication via API', () => {
        // First create a user
        const userData = {
            email: `auth-test-${Date.now()}@example.com`,
            password1: 'TestPassword123!',
            password2: 'TestPassword123!',
            name: 'Auth Test User'
        }

        cy.request('POST', '/api/accounts/signup/', userData).then((signupResponse) => {
            expect(signupResponse.status).to.eq(201)

            // Verify the user for testing
            cy.request('POST', '/api/test/verify-user/', { email: userData.email }).then((verifyResponse) => {
                expect(verifyResponse.status).to.eq(200)

                // Then sign in
                cy.request('POST', '/api/accounts/signin/', {
                    email: userData.email,
                    password: userData.password1
                }).then((response) => {
                    expect(response.status).to.eq(200)
                    expect(response.body).to.have.property('message')
                    expect(response.body).to.have.property('user')
                })
            })
        })
    })

    it('Should return lottery statistics', () => {
        cy.request('GET', '/api/lottery/stats/').then((response) => {
            expect(response.status).to.eq(200)
            expect(response.body).to.have.property('total_draws')
            expect(response.body).to.have.property('open_draws') // Changed from 'active_draws'
            expect(response.body).to.have.property('total_prizes_awarded')
            expect(response.body).to.have.property('total_amount_awarded')
        })
    })

    it('Should return open draws', () => {
        cy.request('GET', '/api/lottery/draws/open/').then((response) => {
            expect(response.status).to.eq(200)
            expect(response.body).to.be.an('array')

            if (response.body.length > 0) {
                const draw = response.body[0]
                expect(draw).to.have.property('id')
                expect(draw).to.have.property('drawtype')
                expect(draw).to.have.property('date')
                expect(draw).to.have.property('prizes')
            }
        })
    })

    it('Should return closed draws', () => {
        cy.request('GET', '/api/lottery/draws/closed/').then((response) => {
            expect(response.status).to.eq(200)
            expect(response.body).to.be.an('array')

            if (response.body.length > 0) {
                const draw = response.body[0]
                expect(draw).to.have.property('id')
                expect(draw).to.have.property('drawtype')
                expect(draw).to.have.property('closed')
                expect(draw).to.have.property('winners')
            }
        })
    })

    it('Should handle ballot purchase via API', () => {
        // First create and sign in a user
        const userData = {
            email: `ballot-test-${Date.now()}@example.com`,
            password1: 'TestPassword123!',
            password2: 'TestPassword123!',
            name: 'Ballot Test User'
        }

        cy.request('POST', '/api/accounts/signup/', userData).then((signupResponse) => {
            expect(signupResponse.status).to.eq(201)

            // Verify the user for testing
            cy.request('POST', '/api/test/verify-user/', { email: userData.email }).then((verifyResponse) => {
                expect(verifyResponse.status).to.eq(200)

                cy.request('POST', '/api/accounts/signin/', {
                    email: userData.email,
                    password: userData.password1
                }).then((signInResponse) => {
                    // Get cookies from sign in response
                    const cookies = signInResponse.headers['set-cookie']

                    // Get CSRF token
                    cy.getCSRFToken().then((csrfToken) => {
                        // Purchase ballots
                        cy.request({
                            method: 'POST',
                            url: '/api/lottery/purchase-ballots/',
                            body: {
                                quantity: 5,
                                card_number: '1234567890123456',
                                expiry_month: 12,
                                expiry_year: 2025,
                                cvv: '123'
                            },
                            headers: {
                                'Cookie': cookies,
                                'X-CSRFToken': csrfToken
                            }
                        }).then((response) => {
                            expect(response.status).to.eq(201) // Changed from 200 to 201 (Created)
                            expect(response.body).to.have.property('message')
                            expect(response.body).to.have.property('ballots_created')
                            expect(response.body.ballots_created).to.eq(5)
                        })
                    })
                })
            })
        })
    })

    it('Should handle ballot assignment via API', () => {
        // First create user and buy ballots
        const userData = {
            email: `assign-test-${Date.now()}@example.com`,
            password1: 'TestPassword123!',
            password2: 'TestPassword123!',
            name: 'Assign Test User'
        }

        cy.request('POST', '/api/accounts/signup/', userData).then((signupResponse) => {
            expect(signupResponse.status).to.eq(201)

            // Verify the user for testing
            cy.request('POST', '/api/test/verify-user/', { email: userData.email }).then((verifyResponse) => {
                expect(verifyResponse.status).to.eq(200)

                cy.request('POST', '/api/accounts/signin/', {
                    email: userData.email,
                    password: userData.password1
                }).then((signInResponse) => {
                    const cookies = signInResponse.headers['set-cookie']

                    // Get CSRF token
                    cy.getCSRFToken().then((csrfToken) => {
                        // Buy ballots first
                        cy.request({
                            method: 'POST',
                            url: '/api/lottery/purchase-ballots/',
                            body: {
                                quantity: 2,
                                card_number: '1234567890123456',
                                expiry_month: 12,
                                expiry_year: 2025,
                                cvv: '123'
                            },
                            headers: {
                                'Cookie': cookies,
                                'X-CSRFToken': csrfToken
                            }
                        }).then(() => {
                            // Get user ballots to find ballot ID
                            cy.request({
                                method: 'GET',
                                url: '/api/lottery/my-ballots/',
                                headers: {
                                    'Cookie': cookies
                                }
                            }).then((ballotsResponse) => {
                                const unassignedBallots = ballotsResponse.body.unassigned_ballots
                                if (unassignedBallots.length > 0) {
                                    const ballotId = unassignedBallots[0].id

                                    // Assign ballot to draw
                                    cy.request({
                                        method: 'POST',
                                        url: `/api/lottery/ballots/${ballotId}/assign/`,
                                        body: {
                                            draw_id: 1
                                        },
                                        headers: {
                                            'Cookie': cookies,
                                            'X-CSRFToken': csrfToken
                                        }
                                    }).then((response) => {
                                        expect(response.status).to.eq(200)
                                        expect(response.body).to.have.property('message')
                                    })
                                }
                            })
                        })
                    })
                })
            })
        })
    })

    it('Should handle profile update via API', () => {
        // First create and sign in a user
        const userData = {
            email: `profile-test-${Date.now()}@example.com`,
            password1: 'TestPassword123!',
            password2: 'TestPassword123!',
            name: 'Profile Test User'
        }

        cy.request('POST', '/api/accounts/signup/', userData).then((signupResponse) => {
            expect(signupResponse.status).to.eq(201)

            // Verify the user for testing
            cy.request('POST', '/api/test/verify-user/', { email: userData.email }).then((verifyResponse) => {
                expect(verifyResponse.status).to.eq(200)

                cy.request('POST', '/api/accounts/signin/', {
                    email: userData.email,
                    password: userData.password1
                }).then((signInResponse) => {
                    const cookies = signInResponse.headers['set-cookie']

                    // Get CSRF token
                    cy.getCSRFToken().then((csrfToken) => {
                        // Update profile
                        cy.request({
                            method: 'PUT',
                            url: '/api/accounts/profile/',
                            body: {
                                name: 'Updated Name',
                                bankaccount: 'NL91ABNA0417164300'
                            },
                            headers: {
                                'Cookie': cookies,
                                'X-CSRFToken': csrfToken
                            }
                        }).then((response) => {
                            expect(response.status).to.eq(200)
                            expect(response.body).to.have.property('user')
                            expect(response.body.user).to.have.property('name', 'Updated Name')
                            expect(response.body).to.have.property('bankaccount', 'NL91ABNA0417164300')
                        })
                    })
                })
            })
        })
    })

    it('Should handle test environment health check', () => {
        cy.request('GET', '/api/test/health-check/').then((response) => {
            expect(response.status).to.eq(200)
            expect(response.body).to.have.property('status', 'healthy')
            expect(response.body).to.have.property('database', 'connected')
        })
    })
}) 
