# -----------------------------
# Base image
# -----------------------------
FROM python:3.13.7-slim

# -----------------------------
# Environment variables
# -----------------------------
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# -----------------------------
# Working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    bash \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install uv (venv manager)
# -----------------------------
RUN pip install --upgrade pip && \
    pip install uv==0.6.5 python-dotenv

# -----------------------------
# Copy the entire project into the container
# -----------------------------
COPY . /app

# -----------------------------
# Copy .env if exists (so Docker can see it)
# -----------------------------
# If you have a .env in your project, it will be available inside Docker
# So run_tests.sh and mockapi_client.config.py can pick it up automatically
COPY .env /app/.env

# -----------------------------
# Create uv-managed virtual environment
# -----------------------------
RUN uv venv /app/.venv

# -----------------------------
# Bootstrap pip inside venv
# -----------------------------
RUN curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN /app/.venv/bin/python get-pip.py
RUN rm get-pip.py

# -----------------------------
# Upgrade setuptools and wheel
# -----------------------------
RUN /app/.venv/bin/pip install --upgrade setuptools wheel

# -----------------------------
# Install the project with test extras
# -----------------------------
RUN /app/.venv/bin/pip install -e /app[test]

# -----------------------------
# Install pytest in venv
# -----------------------------
RUN /app/.venv/bin/pip install pytest pytest-asyncio pytest-xdist

# -----------------------------
# Make test script executable
# -----------------------------
RUN chmod +x ci/run_tests.sh

# -----------------------------
# Default command: run tests
# -----------------------------
CMD ["/bin/bash", "ci/run_tests.sh"]
