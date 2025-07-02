# GuestFlow Backend Dockerfile - Security Hardened
FROM python:3.11.8-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=guestflow_project.settings
ENV PYTHONPATH=/app
ENV USER=appuser
ENV UID=1000
ENV GID=1000

# Create non-root user
RUN groupadd -g $GID $USER && \
    useradd -u $UID -g $GID -m -s /bin/bash $USER

# Set work directory
WORKDIR /app

# Update and install system dependencies with security fixes
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        curl \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* \
        && rm -rf /tmp/* \
        && rm -rf /var/tmp/*

# Copy requirements and install Python dependencies with security updates
COPY requirements_deploy.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --upgrade -r requirements_deploy.txt && \
    pip check

# Create directories for static and media files
RUN mkdir -p /app/static /app/mediafiles && \
    chown -R $USER:$USER /app

# Copy project files
COPY . .

# Set proper permissions
RUN chown -R $USER:$USER /app && \
    chmod -R 755 /app

# Switch to non-root user
USER $USER

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application as non-root user
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "sync", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "100", "guestflow_project.wsgi:application"]
