# Multi-stage build for MoodleLogSmart Backend

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files and source code
COPY pyproject.toml poetry.lock* ./
COPY src ./src

# Install dependencies and package
RUN poetry config virtualenvs.in-project true && \
    poetry install --without dev --no-root

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY src ./src
COPY pyproject.toml ./

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Add venv to PATH and set PYTHONPATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1

# Create necessary directories
RUN mkdir -p /app/uploads /app/results /app/temp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "moodlelogsmart.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
