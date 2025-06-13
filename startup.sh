#!/bin/bash

# Startup script for Azure App Service with debugging
echo "Starting application setup..."

# Print current directory and contents
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Print Python version
echo "Python version:"
python --version

# Print pip version
echo "Pip version:"
pip --version

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install local rt_search module
echo "Installing local rt_search module..."
pip install -e .

# Try to find and run the application
if [ -f "application.py" ]; then
    echo "Found application.py, running with gunicorn"
    gunicorn --bind=0.0.0.0:8000 --log-level debug application:app
elif [ -f "app.py" ]; then
    echo "Found app.py, running directly"
    python app.py
elif [ -f "wsgi.py" ]; then
    echo "Found wsgi.py, running with gunicorn"
    gunicorn --bind=0.0.0.0:8000 --log-level debug wsgi:app
else
    echo "ERROR: Could not find application.py, app.py or wsgi.py"
    echo "Directory contents: $(ls -la)"
    exit 1
fi
