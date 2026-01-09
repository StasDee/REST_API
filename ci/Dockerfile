# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.0

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python virtual environment manager)
RUN pip install --upgrade pip && \
    pip install uv==0.6.5

# Copy project files
COPY . /app

# Create and activate uv virtual environment
RUN uv -e /app/.venv pip install -e .

# Set the default command to run pytest inside the uv environment
CMD ["uv", "-e", "/app/.venv", "pytest", "-v", "-m", "async or concurrency"]
