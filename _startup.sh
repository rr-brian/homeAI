#!/bin/bash

# Set error handling
set -e

# Debug output
echo "Starting app_start.sh..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Set environment variables
export PORT=${PORT:-8000}
export PYTHONUNBUFFERED=1

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Install Gunicorn if not present
python -m pip install gunicorn

# Create gunicorn config
cat > gunicorn.conf.py << EOL
bind = "0.0.0.0:${PORT}"
workers = 4
threads = 2
timeout = 600
keepalive = 5
worker_class = "sync"
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True
EOL

# Start Gunicorn
echo "Starting Gunicorn on port ${PORT}..."
exec python -m gunicorn wsgi:app -c gunicorn.conf.py
