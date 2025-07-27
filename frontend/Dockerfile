FROM node:18

USER node
WORKDIR /code
COPY --link yarn.lock package.json ./
RUN yarn install
COPY --link ./ ./
COPY --link ./ ./
CMD ["yarn", "dev"]
