#!/bin/bash

# GuestFlow Backend Deployment Script

echo "🚀 Starting GuestFlow Backend Deployment..."

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗃️ Running database migrations..."
python manage.py migrate

echo "✅ Deployment preparation complete!"
