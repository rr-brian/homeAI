#!/bin/bash

# Startup script for Azure App Service with debugging
echo "Starting application setup..."

# Print current directory and contents
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Simple approach - use system Python
echo "Using system Python"
PYTHON_CMD="python3"

# Print Python version
echo "Python version:"
$PYTHON_CMD --version

# Install requirements
echo "Installing requirements..."
$PYTHON_CMD -m pip install -r requirements.txt

# Check if build directory exists
if [ ! -d "build" ]; then
    echo "ERROR: build directory not found!"
    echo "Current directory contents:"
    ls -la
else
    echo "Build directory found with contents:"
    ls -la build/
fi

# Create a simple test.html file to verify static file serving
echo "<html><body><h1>Test Page</h1><p>This is a test page to verify static file serving.</p></body></html>" > test.html
echo "Created test.html file"

# Create a simple wsgi.py file as a fallback
if [ ! -f "wsgi.py" ]; then
    echo "Creating fallback wsgi.py file"
    echo 'from application import app as application\nif __name__ == "__main__":\n    application.run()' > wsgi.py
fi

# Run the application with Gunicorn
echo "Starting application with Gunicorn..."

# Install Gunicorn
$PYTHON_CMD -m pip install gunicorn

# Set the port from environment variable or default to 8000
PORT=${PORT:-8000}
echo "Using port: $PORT"

# Run with Gunicorn
if [ -f "application.py" ]; then
    echo "Found application.py, running with gunicorn"
    exec gunicorn --bind=0.0.0.0:$PORT --timeout 600 --log-level debug application:app
elif [ -f "wsgi.py" ]; then
    echo "Found wsgi.py, running with gunicorn"
    exec gunicorn --bind=0.0.0.0:$PORT --timeout 600 --log-level debug wsgi:application
else
    echo "ERROR: Could not find application.py or wsgi.py"
    echo "Directory contents: $(ls -la)"
    exit 1
fi
