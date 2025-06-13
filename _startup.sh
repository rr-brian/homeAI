#!/bin/bash

# Set error handling
set -e

# Debug output
echo "Starting _startup.sh..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Set environment variables
export PORT=${PORT:-8000}
export PYTHONUNBUFFERED=1

# Find the correct directory
SCRIPT_DIR=$(pwd)
echo "Script directory: $SCRIPT_DIR"

# Check if required files exist
echo "Checking for required files..."
if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt in current directory"
    REQUIREMENTS_PATH="requirements.txt"
elif [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Found requirements.txt in script directory"
    REQUIREMENTS_PATH="$SCRIPT_DIR/requirements.txt"
elif [ -f "/home/site/wwwroot/requirements.txt" ]; then
    echo "Found requirements.txt in wwwroot"
    REQUIREMENTS_PATH="/home/site/wwwroot/requirements.txt"
else
    echo "ERROR: requirements.txt not found!"
    find / -name "requirements.txt" -type f 2>/dev/null | head -n 5
    exit 1
fi

echo "Using requirements file: $REQUIREMENTS_PATH"

# Check for wsgi.py
if [ -f "wsgi.py" ]; then
    echo "Found wsgi.py in current directory"
elif [ -f "$SCRIPT_DIR/wsgi.py" ]; then
    echo "Found wsgi.py in script directory"
elif [ -f "/home/site/wwwroot/wsgi.py" ]; then
    echo "Found wsgi.py in wwwroot"
else
    echo "ERROR: wsgi.py not found!"
    find / -name "wsgi.py" -type f 2>/dev/null | head -n 5
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "$REQUIREMENTS_PATH"

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

# Show final environment before starting
echo "Final directory contents: $(ls -la)"
echo "Environment variables:"
env | grep -v SECRET | grep -v KEY | sort

# Start Gunicorn
echo "Starting Gunicorn on port ${PORT}..."
exec python -m gunicorn wsgi:app -c gunicorn.conf.py
