#!/bin/bash

# Startup script for Azure App Service with debugging
echo "Starting application setup..."

# Print current directory and contents
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Set up Python paths for Azure App Service
echo "Setting up Python paths for Azure App Service..."

# Check for different Python locations in Azure App Service
PYTHON_LOCATIONS=(
    "/usr/bin/python3"
    "/usr/bin/python"
    "/home/site/wwwroot/env/bin/python"
    "/opt/python/latest/bin/python"
    "/home/python/python39/bin/python"
)

PYTHON_CMD=""
for loc in "${PYTHON_LOCATIONS[@]}"; do
    if [ -f "$loc" ]; then
        PYTHON_CMD="$loc"
        echo "Found Python at: $PYTHON_CMD"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Could not find Python executable!"
    echo "Searching in PATH:"
    which python || which python3 || echo "Python not found in PATH"
    exit 1
fi

# Print Python version
echo "Python version:"
$PYTHON_CMD --version

# Set up pip
PIP_CMD="$PYTHON_CMD -m pip"
echo "Using pip command: $PIP_CMD"

# Print pip version
echo "Pip version:"
$PIP_CMD --version

# Install requirements
echo "Installing requirements..."
$PIP_CMD install -r requirements.txt

# Install local rt_search module
echo "Installing local rt_search module..."
$PIP_CMD install -e .

# Try to find and run the application
if [ -f "application.py" ]; then
    echo "Found application.py, running with gunicorn"
    $PIP_CMD install gunicorn
    $PYTHON_CMD -m gunicorn --bind=0.0.0.0:8000 --log-level debug application:app
elif [ -f "app.py" ]; then
    echo "Found app.py, running directly"
    $PYTHON_CMD app.py
elif [ -f "wsgi.py" ]; then
    echo "Found wsgi.py, running with gunicorn"
    $PIP_CMD install gunicorn
    $PYTHON_CMD -m gunicorn --bind=0.0.0.0:8000 --log-level debug wsgi:app
else
    echo "ERROR: Could not find application.py, app.py or wsgi.py"
    echo "Directory contents: $(ls -la)"
    exit 1
fi
