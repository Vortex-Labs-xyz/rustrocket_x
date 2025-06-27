# Multi-stage build for rustrocket_x Python package
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.4

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy source code
COPY rustrocket_x/ ./rustrocket_x/
COPY README.md ./

# Install the package
RUN poetry install --only main

# Default entrypoint
CMD ["python", "-m", "rustrocket_x"] 