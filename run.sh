#!/bin/bash

# This script is a simple wrapper to call startup.sh
echo "Starting run.sh wrapper script..."
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Execute startup.sh if it exists
if [ -f "startup.sh" ]; then
    echo "Found startup.sh, executing it..."
    chmod +x startup.sh
    ./startup.sh
else
    echo "startup.sh not found, trying to run app directly..."
    
    # Try to find and run app.py
    if [ -f "app.py" ]; then
        echo "Found app.py, running directly"
        python app.py
    elif [ -f "wsgi.py" ]; then
        echo "Found wsgi.py, running with gunicorn"
        gunicorn --bind=0.0.0.0:8000 wsgi:app
    else
        echo "ERROR: Could not find app.py or wsgi.py"
        echo "Directory contents: $(ls -la)"
        exit 1
    fi
fi
