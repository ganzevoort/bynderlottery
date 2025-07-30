# Build stage
FROM node:18-alpine AS base
WORKDIR /code
COPY --link yarn.lock package.json ./
RUN yarn install --frozen-lockfile

FROM base AS builder
COPY --link ./ ./
# envs, args, secrets
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

# Dev image
FROM base AS dev
EXPOSE 3000
CMD ["yarn", "dev"]
