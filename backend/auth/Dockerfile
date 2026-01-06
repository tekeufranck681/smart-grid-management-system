FROM python:3.12-slim

# Install system dependencies + Postgres client
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code, Alembic migrations, and entrypoint
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY entrypoint.sh .

# Expose FastAPI port
EXPOSE 8000

# Run entrypoint script
CMD ["/app/entrypoint.sh"]
