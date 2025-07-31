# Build stage
FROM node:18-alpine AS base
WORKDIR /code

# Install dependencies first for better caching
COPY --link yarn.lock package.json ./
RUN yarn install --frozen-lockfile

# Testing stage: run linters and unittests
FROM base AS tester
COPY --link ./ ./
RUN yarn lint
RUN yarn eslint
RUN yarn test

# Builder stage for production
FROM base AS builder
COPY --link ./ ./
RUN yarn build

# Production stage
FROM node:18-alpine AS production
WORKDIR /app

# Copy standalone output from builder
COPY --from=builder --link /code/.next/standalone ./
COPY --from=builder --link /code/.next/static ./.next/static
COPY --from=builder --link /code/public ./public

EXPOSE 3000
CMD ["node", "server.js"]

# Development stage (default)
FROM base AS dev
EXPOSE 3000
CMD ["yarn", "dev"]
