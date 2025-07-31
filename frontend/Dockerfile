# Build stage
FROM node:18-alpine AS base
WORKDIR /code
COPY --link yarn.lock package.json ./
RUN yarn install --frozen-lockfile

# Run linters and unittests
FROM base AS tester
COPY --link ./ ./
RUN yarn lint
RUN yarn eslint
RUN yarn test

FROM base AS builder
COPY --link ./ ./
RUN yarn build
CMD ["/bin/true"]

# Production stage
FROM node:18-alpine AS production
WORKDIR /app

# Copy standalone output from builder
COPY --from=builder --link /code/.next/standalone ./
COPY --from=builder --link /code/.next/static ./.next/static
COPY --from=builder --link /code/public ./public

EXPOSE 3000
CMD ["node", "server.js"]

# Dev image
FROM base AS dev
EXPOSE 3000
CMD ["yarn", "dev"]
