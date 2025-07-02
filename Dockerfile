# GuestFlow Backend Dockerfile - Security Hardened
FROM python:3.11-slim-bookworm

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

# Copy requirements and install Python dependencies
COPY requirements_deploy.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements_deploy.txt

# Copy project
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/static /app/mediafiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "guestflow_project.wsgi:application"]
