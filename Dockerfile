FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set Flask environment variables
ENV FLASK_APP=__init__:create_app
ENV FLASK_ENV=development

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

# Add a small script to wait for Postgres and run migrations
# Then start Flask
CMD python - <<'EOF'
import os
import time
import subprocess
import socket

db_host = os.environ.get("DB_HOST", "127.0.0.1")
db_port = int(os.environ.get("DB_PORT", 5432))

# Wait for DB to be ready
while True:
    try:
        with socket.create_connection((db_host, db_port), timeout=2):
            break
    except Exception:
        print("Waiting for Postgres...")
        time.sleep(1)

print("Postgres is up!")

# Run migrations
subprocess.run(["python", "-m", "flask", "db", "upgrade"], check=True)

# Start Flask server
subprocess.run([
    "python", "-m", "flask", "run",
    "--host=0.0.0.0", "--port=5000"
])
EOF

# ENTRYPOINT ["/app/entrypoint.sh"]
