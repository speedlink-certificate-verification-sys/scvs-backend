#!/bin/bash

echo "Waiting for Postgres..."

# Wait for DB before continuing
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
done

echo "Postgres is up!"

# Install Poppler
apt-get update && apt-get install -y poppler-utils

# Set Flask app
export FLASK_APP=app:create_app
export FLASK_ENV=development
# export FLASK_DEBUG=1

# Run migrations
flask db upgrade

# Start flask
flask run --host=0.0.0.0 --port=5000
