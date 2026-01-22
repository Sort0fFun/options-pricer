# Stage 1: Builder - Install dependencies
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies to user directory for easy copying
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime system dependencies and create non-root user
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code with correct ownership
COPY --chown=appuser:appuser . .

# Create logs directory
RUN mkdir -p logs && chown appuser:appuser logs

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5001

# Expose Flask port
EXPOSE 5001

# Switch to non-root user
USER appuser

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "--timeout", "120", "flask_app:app"]
