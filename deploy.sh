#!/bin/bash

# Deployment script for AlwaysData

echo "🚀 Starting deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --user -r requirements.txt

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start bot
echo "✅ Starting bot..."
python -m app.main
