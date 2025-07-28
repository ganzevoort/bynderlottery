FROM node:18

USER node
WORKDIR /code
COPY --link yarn.lock package.json ./
RUN yarn install
COPY --link ./ ./
RUN yarn build
CMD ["yarn", "start"]
