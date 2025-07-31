#!/usr/bin/env python3
import yaml
import sys

# Read the compose file
with open('compose.test.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Update backend service
if 'backend' in data['services']:
    data['services']['backend']['image'] = f'{sys.argv[1]}/lottery-backend:build-{sys.argv[2]}'
    if 'build' in data['services']['backend']:
        del data['services']['backend']['build']

# Update frontend service
if 'frontend' in data['services']:
    data['services']['frontend']['image'] = f'{sys.argv[1]}/lottery-frontend:build-{sys.argv[2]}'
    if 'build' in data['services']['frontend']:
        del data['services']['frontend']['build']

# Write the updated compose file
with open('compose.test.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
