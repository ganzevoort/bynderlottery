#!/bin/sh

set -ex

export COMPOSE_FILE=compose.yaml
docker compose pull
docker compose build
docker compose up --force-recreate --detach frontend backend
docker compose exec frontend yarn lint
docker compose exec frontend yarn test
docker compose exec backend python manage.py test -v2
docker compose exec backend flake8
docker compose exec backend black --check .
docker compose down

export COMPOSE_FILE=compose.test.yaml
docker compose pull
docker compose build
docker compose up --force-recreate --detach
docker compose exec cypress cypress run --spec "e2e/tests/**/*.cy.ts"
docker compose down
