#!/bin/bash

# Start bot script
cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start bot
echo "Starting bot..."
python -m app.main
