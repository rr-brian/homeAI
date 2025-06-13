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

# Print Python path
echo "Python path:"
python -c "import sys; print(sys.path)"

# Start the application
echo "Starting application with Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --log-level debug wsgi:app
