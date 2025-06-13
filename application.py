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

# Set default environment variables if they don't exist
default_env_vars = {
    'AZURE_OPENAI_ENDPOINT': 'https://example.openai.azure.com/',
    'AZURE_OPENAI_DEPLOYMENT': 'gpt-35-turbo',
    'AZURE_OPENAI_API_KEY': 'dummy_key_for_development',
    'AZURE_AI_SEARCH_ENDPOINT': 'https://example.search.windows.net',
    'AZURE_AI_SEARCH_INDEX': 'example-index',
    'AZURE_AI_SEARCH_API_KEY': 'dummy_key_for_development',
    'AZURE_GEN_SEARCH_ENDPOINT': 'https://example.cognitiveservices.azure.com/',
    'AZURE_GEN_SEARCH_DEPLOYMENT': 'gpt-35-turbo',
    'AZURE_GEN_SEARCH_API_KEY': 'dummy_key_for_development',
    'FLASK_ENV': 'development',
    'FLASK_DEBUG': '1'
}

# Set default environment variables if they don't exist
for key, value in default_env_vars.items():
    if key not in os.environ:
        logger.info(f"Setting default value for missing environment variable: {key}")
        os.environ[key] = value
    else:
        logger.info(f"Using existing environment variable: {key}")

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

app = Flask(__name__, static_folder='build')
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
    
    # Initialize search client
    logger.info('Initializing search client...')
    search_client = SearchClient()
    logger.info('Search client initialized')
    
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

# Routes
@app.route('/api/test', methods=['GET'])
def test():
    logger.info('Test endpoint called')
    return jsonify({'status': 'ok', 'message': 'API is working'})

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
def serve(path):
    logger.info(f'Serving path: {path}')
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except:
            return jsonify({
                "status": "error",
                "message": "Application is running but static files not found",
                "python_path": str(sys.path),
                "current_directory": os.getcwd(),
                "directory_contents": str(os.listdir(os.getcwd()))
            })

# This allows the app to be run directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
