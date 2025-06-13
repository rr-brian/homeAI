import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the path so we can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Print debug information
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir(os.getcwd())}")
logger.info(f"Python path: {sys.path}")

# Import the app from our application.py file
try:
    # First try to import from application.py
    from application import app
    logger.info("Successfully imported app from application.py")
except ImportError as e:
    logger.error(f"Error importing app from application.py: {e}")
    
    try:
        # Try importing from backend.wsgi
        from backend.wsgi import app
        logger.info("Successfully imported app from backend.wsgi")
    except ImportError as e2:
        logger.error(f"Error importing app from backend.wsgi: {e2}")
        
        # Create a simple Flask app as fallback
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return jsonify({
                "status": "error",
                "message": "Application failed to load properly",
                "details": f"Import errors: {str(e)}, {str(e2)}",
                "python_path": str(sys.path),
                "current_directory": os.getcwd(),
                "directory_contents": str(os.listdir(os.getcwd()))
            })

# Expose the application variable that Azure App Service is looking for
application = app

# This allows the app to be run directly with python wsgi.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
