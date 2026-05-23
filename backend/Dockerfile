# Multi-stage Dockerfile for Real-Time Weather Pipeline
# Stage 1: Builder - Install dependencies and prepare Python environment
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
WORKDIR /build
COPY backend/requirements.txt .

# Install Python dependencies into venv
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt


# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim

# Metadata
LABEL maintainer="Weather Pipeline Team" \
      version="1.0.0" \
      description="Real-Time Weather Data Pipeline Backend"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash appuser

# Create app directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser backend/ .

# Create necessary directories with proper permissions
RUN mkdir -p logs archives && \
    chown -R appuser:appuser logs archives

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${API_PORT:-8000}/api/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4
