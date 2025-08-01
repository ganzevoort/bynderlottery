#!/usr/bin/env python3

"""
Update the compose file to use the correct images.

Change:
  frontend:
    build:
      context: frontend
      target: production
    env_file: test.env

To:
  frontend:
    image: ghcr.io/ganzevoort/bynderlottery/frontend:build-1234567890
    env_file: test.env

"""


import yaml
import sys
from os import environ


compose_file = 'compose.test.yaml'
images = {
    'backend': environ['BACKEND_IMAGE'],
    'frontend': environ['FRONTEND_IMAGE']
}


# Read the compose file
with open(compose_file, 'r') as f:
    data = yaml.safe_load(f)

# Update services
for service_name, service in data['services'].items():
    if (
        (build := service.get('build')) and
        (context := build.get('context')) and
        (image := images.get(context))
    ):
        service['image'] = f'{image}:build-{sys.argv[1]}'
        del service['build']

# Write the updated compose file
with open(compose_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
