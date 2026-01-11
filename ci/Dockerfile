# Base image
FROM python:3.9-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --upgrade pip && \
    pip install uv==0.6.5

# Copy project
COPY . /app

# Install project into uv-managed virtual environment
RUN uv -e /app/.venv pip install -e .

# Default command: run async + concurrency tests
CMD ["/bin/bash", "ci/run_tests.sh"]
