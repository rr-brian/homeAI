import os
import sys

# Add the backend directory to the path so we can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import the app from the backend
from backend.wsgi import app

# This allows the app to be run directly with python wsgi.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
