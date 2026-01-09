#!/usr/bin/env bash
set -euo pipefail

echo "Activating uv virtual environment..."
uv -e /app/.venv pytest "$@"

echo "Tests completed successfully!"
