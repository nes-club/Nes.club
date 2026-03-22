#!/bin/bash
set -e

CMD="${SERVICE_CMD:-docker-run-production}"
echo "Starting service: make $CMD"
exec make "$CMD"
