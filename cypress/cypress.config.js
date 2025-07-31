const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://web', // Test environment - matches Docker Compose
    supportFile: 'support/e2e.js',
    specPattern: 'e2e/**/*.cy.ts',
    viewportWidth: 1024,
    viewportHeight: 1366,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    videosFolder: 'videos',
    screenshotsFolder: 'screenshots',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
})
