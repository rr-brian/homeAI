"""
Standard entry point for Azure App Service.
Azure App Service will look for an application.py file with an 'app' variable.
"""
import os
import sys
import logging
import importlib.util
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add all possible paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Current directory: {current_dir}")

paths_to_add = [
    current_dir,
    os.path.join(current_dir, 'backend'),
    os.path.dirname(current_dir),
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)
        logger.info(f"Added to sys.path: {path}")

# Print debug information
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir(os.getcwd())}")
logger.info(f"Python path: {sys.path}")

# Set default values for missing environment variables
for env_var, default_value in [
    ('AZURE_AI_SEARCH_ENDPOINT', 'https://example.search.windows.net'),
    ('AZURE_AI_SEARCH_INDEX', 'example-index'),
    ('AZURE_AI_SEARCH_API_KEY', 'example-key'),
    ('AZURE_OPENAI_API_KEY', 'example-key'),
    ('AZURE_OPENAI_ENDPOINT', 'https://example.openai.azure.com'),
    ('AZURE_OPENAI_DEPLOYMENT', 'example-deployment'),
    ('AZURE_GEN_SEARCH_ENDPOINT', 'https://example.openai.azure.com'),
    ('AZURE_GEN_SEARCH_API_KEY', 'example-key'),
    ('AZURE_GEN_SEARCH_DEPLOYMENT', 'example-deployment'),
]:
    if not os.environ.get(env_var):
        os.environ[env_var] = default_value
        logger.info(f"Setting default value for missing {env_var}")

# Determine if we're running in development mode with placeholder values
DEV_MODE = (
    os.environ.get('AZURE_AI_SEARCH_ENDPOINT') == 'https://example.search.windows.net' or
    os.environ.get('AZURE_AI_SEARCH_API_KEY') == 'example-key'
)

# Determine if we're running in Azure App Service
RUNNING_IN_AZURE = os.environ.get('WEBSITE_SITE_NAME') is not None

if DEV_MODE:
    logger.warning("Running in DEVELOPMENT MODE with placeholder credentials. Some features will be limited.")
if RUNNING_IN_AZURE:
    logger.info("Running in Azure App Service environment")
    # Log important Azure environment variables
    logger.info(f"Azure site name: {os.environ.get('WEBSITE_SITE_NAME')}")
    logger.info(f"Azure instance ID: {os.environ.get('WEBSITE_INSTANCE_ID')}")
    logger.info(f"Azure hostname: {os.environ.get('WEBSITE_HOSTNAME')}")
    logger.info(f"Azure deployment ID: {os.environ.get('DEPLOYMENT_ID', 'Not available')}")
    # Set Flask to production mode in Azure
    os.environ['FLASK_ENV'] = 'production'

# Function to check if a module exists
def module_exists(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except ModuleNotFoundError:
        return False

# Create a simple Flask app as fallback
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

# Try to import the search client
try:
    if module_exists('backend.rt_search.search_client'):
        from backend.rt_search.search_client import SearchClient
        from backend.rt_search.env_loader import load_env
        logger.info("Successfully imported from backend.rt_search")
    elif module_exists('rt_search.search_client'):
        from rt_search.search_client import SearchClient
        from rt_search.env_loader import load_env
        logger.info("Successfully imported from rt_search")
    else:
        # Create dummy versions
        logger.warning("Could not import search client, using dummy version")
        raise ImportError("Could not import search client modules")
except Exception as e:
    logger.warning(f"Exception during import: {e}")
    # Continue with dummy versions
    class SearchClient:
        def __init__(self):
            self.cognitive_search_client = None
            logger.warning("Using dummy SearchClient")
            
        def search_contract_language(self, query):
            return [{"error": "SearchClient not properly initialized"}]
            
    def load_env():
        logger.warning("Using dummy load_env function")
        return {}
    
    # Load environment variables
    logger.info('Loading environment variables...')
    env_vars = load_env()
    logger.info(f'Using search index: {os.getenv("AZURE_AI_SEARCH_INDEX")}')
    logger.info(f'Using search endpoint: {os.getenv("AZURE_AI_SEARCH_ENDPOINT")}')
    
    # Import and initialize search client
    if DEV_MODE:
        # In development mode, use a mock search client
        logger.info("Using mock SearchClient in development mode")
        class SearchClient:
            def __init__(self):
                self.cognitive_search_client = None
                logger.warning("Using mock SearchClient in development mode")
                
            def search_contract_language(self, query):
                # Return mock search results
                return [
                    {"title": "Sample Document 1", "content": "This is a sample search result.", "score": 0.95},
                    {"title": "Sample Document 2", "content": "Another sample search result.", "score": 0.85}
                ]
        
        search_client = SearchClient()
        logger.info("Mock search client initialized")
    else:
        # In production mode, use the real search client
        try:
            from backend.rt_search.search_client import SearchClient
            logger.info("Successfully imported SearchClient")
            search_client = SearchClient()
            logger.info("Search client initialized")
        except Exception as e:
            logger.error(f"Error initializing search client: {e}")
            logger.error(traceback.format_exc())
            # Create dummy versions as fallback
            class SearchClient:
                def __init__(self):
                    self.cognitive_search_client = None
                    logger.warning("Using dummy SearchClient due to error")
                    
                def search_contract_language(self, query):
                    return [{"error": "SearchClient not properly initialized due to error"}]
                    
            search_client = SearchClient()

# API endpoints
@app.route('/api/test')
def test():
    return jsonify({"status": "ok", "message": "API is working"})

@app.route('/api/diagnostics')
def diagnostics():
    """Diagnostic endpoint to help troubleshoot Azure deployment issues"""
    try:
        return jsonify({
            "status": "ok",
            "environment": {
                "dev_mode": DEV_MODE,
                "running_in_azure": RUNNING_IN_AZURE,
                "python_version": sys.version,
                "flask_env": os.environ.get('FLASK_ENV', 'not set'),
                "app_service_name": os.environ.get('WEBSITE_SITE_NAME', 'not set'),
                "hostname": os.environ.get('WEBSITE_HOSTNAME', 'not set'),
                "instance_id": os.environ.get('WEBSITE_INSTANCE_ID', 'not set'),
                "deployment_id": os.environ.get('DEPLOYMENT_ID', 'not set'),
                "current_directory": os.getcwd(),
                "directory_contents": os.listdir(os.getcwd()),
                "build_exists": os.path.exists('build'),
                "build_contents": os.listdir('build') if os.path.exists('build') else [],
                "static_folder": app.static_folder,
                "static_folder_exists": os.path.exists(app.static_folder) if app.static_folder else False,
                "static_folder_contents": os.listdir(app.static_folder) if app.static_folder and os.path.exists(app.static_folder) else []
            }
        })
    except Exception as e:
        logger.error(f"Error in diagnostics endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/test.html')
def test_html():
    return send_from_directory(os.getcwd(), 'test.html')

@app.route('/test')
def simple_test():
    return jsonify({
        "status": "ok", 
        "message": "Simple test endpoint is working",
        "environment": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set"),
            "HOME": os.environ.get("HOME", "Not set"),
            "WEBSITE_SITE_NAME": os.environ.get("WEBSITE_SITE_NAME", "Not set"),
            "PORT": os.environ.get("PORT", "Not set"),
            "HTTP_PLATFORM_PORT": os.environ.get("HTTP_PLATFORM_PORT", "Not set")
        },
        "file_system": {
            "cwd": os.getcwd(),
            "directory_contents": os.listdir(os.getcwd()),
            "build_exists": os.path.exists(os.path.join(os.getcwd(), "build")),
            "build_contents": os.listdir(os.path.join(os.getcwd(), "build")) if os.path.exists(os.path.join(os.getcwd(), "build")) else []
        }
    })

@app.route('/api/search', methods=['POST'])
def search():
    try:
        logger.info('Received search request')
        
        if not request.is_json:
            error_msg = 'Request must be JSON'
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
            
        query = request.json.get('query', '')
        logger.info(f'Query: {query}')
        
        # Execute search
        logger.info('Executing search...')
        results = search_client.search_contract_language(query)
        logger.info(f'Got {len(results)} results')
        
        return jsonify(results)
        
    except Exception as e:
        error_msg = f'Search error: {str(e)}'
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({'error': error_msg}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    try:
        logger.info(f"Serving path: {path}")
        
        # Special case for API endpoints
        if path.startswith('api/'):
            return jsonify({"error": "API endpoint not found"}), 404
        
        # Check for static files in build/static directory (most common for React apps)
        if path.startswith('static/') and os.path.exists(os.path.join('build', path)):
            logger.info(f"Serving static file: {path}")
            return send_from_directory('build', path)
        
        # Check for any other files in the build directory
        if path and os.path.exists(os.path.join('build', path)):
            logger.info(f"Serving file from build directory: {path}")
            return send_from_directory('build', path)
        
        # For all other paths, serve the React app's index.html
        if os.path.exists(os.path.join('build', 'index.html')):
            logger.info(f"Serving index.html for path: {path}")
            return send_from_directory('build', 'index.html')
        
        # If build/index.html doesn't exist, check if we have a static folder
        if app.static_folder and os.path.exists(os.path.join(app.static_folder, 'index.html')):
            logger.info(f"Serving index.html from static folder for path: {path}")
            return send_from_directory(app.static_folder, 'index.html')
        
        # If we get here, nothing worked, return a diagnostic response
        logger.error("Could not find any static files to serve")
        return jsonify({
            "status": "error",
            "message": "Application is running but could not find static files",
            "path_requested": path,
            "static_folder": app.static_folder,
            "cwd": os.getcwd(),
            "directory_contents": os.listdir(os.getcwd()),
            "build_exists": os.path.exists('build'),
            "build_contents": os.listdir('build') if os.path.exists('build') else []
        }), 404
    except Exception as e:
        logger.error(f"Error serving {path or 'index.html'}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to serve {path or 'index.html'}",
            "error": str(e),
            "path": path,
            "static_folder": app.static_folder,
            "cwd": os.getcwd(),
            "directory_contents": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else []
        })

# This allows the app to be run directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
