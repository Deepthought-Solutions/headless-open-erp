#!/bin/sh
set -e

# Wait for the database to be ready
# This is a simple loop, a more robust solution might use wait-for-it.sh
# However, the docker-compose healthcheck should handle this.

# Run database migrations
echo "Running API migrations..."
python run_migrations.py

# Start the Gunicorn server
echo "Starting Gunicorn..."
exec gunicorn --access-logfile - --error-logfile - --log-level debug -w 4 -k uvicorn.workers.UvicornWorker infrastructure.web.wsgi:app -b 0.0.0.0:8000
