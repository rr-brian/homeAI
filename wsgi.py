import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Print environment variables for debugging
logger.info("Environment variables:")
for key, value in os.environ.items():
    if "SECRET" not in key.upper() and "KEY" not in key.upper() and "PASSWORD" not in key.upper():
        logger.info(f"{key}: {value}")

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Print debug information
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir(os.getcwd())}")
logger.info(f"Python path: {sys.path}")

# Check if build directory exists
if os.path.exists('build'):
    logger.info(f"Build directory exists with contents: {os.listdir('build')}")
else:
    logger.warning("Build directory not found!")

# Import the app from our application.py file
try:
    # First try to import from application.py
    from application import app
    logger.info("Successfully imported app from application.py")
except Exception as e:
    logger.error(f"Error importing app from application.py: {e}")
    logger.error(traceback.format_exc())
    
    try:
        # Create a simple Flask app as fallback
        from flask import Flask, jsonify, send_from_directory
        app = Flask(__name__, static_folder='build', static_url_path='')
        
        @app.route('/api/diagnostics')
        def diagnostics():
            return jsonify({
                "status": "error",
                "message": "Using fallback Flask app",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "environment": {
                    "python_path": str(sys.path),
                    "current_directory": os.getcwd(),
                    "directory_contents": os.listdir(os.getcwd()),
                    "build_exists": os.path.exists('build'),
                    "build_contents": os.listdir('build') if os.path.exists('build') else []
                }
            })
        
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path.startswith('api/'):
                return jsonify({"error": "API endpoint not available"}), 404
            
            if os.path.exists(os.path.join('build', path)):
                return send_from_directory('build', path)
            
            return send_from_directory('build', 'index.html')
            
        logger.info("Created fallback Flask app")
    except Exception as e2:
        logger.error(f"Error creating fallback app: {e2}")
        logger.error(traceback.format_exc())
        raise

# Expose the application variable that Azure App Service is looking for
application = app

# This allows the app to be run directly with python wsgi.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
