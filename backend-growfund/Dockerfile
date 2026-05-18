# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (no database access needed here)
RUN python manage.py collectstatic --noinput --clear || true

# Copy and make start script executable
COPY start.sh .
RUN chmod +x start.sh

# Expose port (Render will override with $PORT)
EXPOSE 8000

# Run startup script (migrations + gunicorn)
CMD ["./start.sh"]
