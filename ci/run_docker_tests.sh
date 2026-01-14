#!/usr/bin/env bash
set -euo pipefail

# Build and run the Docker image in one command
docker build -t mockapi-tests -f ci/Dockerfile .
docker run --rm mockapi-tests
