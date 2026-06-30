# Use an official, lightweight Python runtime base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files to disk and force unbuffered stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (curl is highly recommended for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency blueprint first to maximize Docker build caching
COPY requirements.txt .

# Install your Python packages securely without saving local caches
RUN pip install --no-cache-dir -r requirements.txt

# Copy your actual FastAPI script into the container
COPY app.py .

# Expose the internal network port that your application listens on
EXPOSE 8000

# The startup command executing our web worker daemon
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1