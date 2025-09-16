# Stage 1: Build Stage - Install all dependencies (including dev)
FROM python:3.11-slim AS builder
WORKDIR /app

# Install system dependencies
RUN apt-get update --allow-insecure-repositories && apt-get install -y postgresql-client && apt-get clean

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Stage 2: Final Stage - Copy only what's needed for production
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY . .

# Copy entrypoint script
COPY entrypoint.sh .

# Expose port 8000
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
