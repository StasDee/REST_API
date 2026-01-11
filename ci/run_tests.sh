#!/usr/bin/env bash
set -e

echo "Starting test execution..."

# Ensure venv exists
if [ ! -d ".venv" ]; then
  echo "Virtual environment not found"
  exit 1
fi

# Activate venv
source .venv/bin/activate

# Run pytest (arguments may be overridden by Docker/K8s)
pytest -v -s "$@"

