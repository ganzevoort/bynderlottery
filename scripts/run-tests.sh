#!/bin/sh

set -ex

# Linters and unittests are in "tester" build stages
docker build --target=tester --tag=lottery-backend-tester  backend
docker build --target=tester --tag=lottery-frontend-tester frontend

# Integration test:
export COMPOSE_FILE=compose.test.yaml
docker compose pull --quiet
docker compose build  # should be fast, chached from tester
docker compose up --force-recreate --detach
docker compose exec cypress cypress run --spec "e2e/tests/**/*.cy.ts"
docker compose down
