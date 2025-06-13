#!/bin/bash

# Simple startup script for Azure App Service
echo "Starting application with Gunicorn..."
gunicorn --bind=0.0.0.0:8000 wsgi:app
