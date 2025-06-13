import os
import sys
import logging

# Add the rt_search module to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import the modules
from flask import Flask, request, jsonify
from flask_cors import CORS

# Try different import approaches for rt_search
try:
    from rt_search.search_client import SearchClient
    from rt_search.env_loader import load_env
    print("Successfully imported rt_search modules")
except ImportError as e:
    print(f"Error importing rt_search: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir(os.getcwd())}")
    print(f"Backend directory contents: {os.listdir(os.path.join(os.getcwd(), 'backend'))}")
    
    # Try an alternative import approach
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from backend.rt_search.search_client import SearchClient
        from backend.rt_search.env_loader import load_env
        print("Successfully imported rt_search modules using alternative path")
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        # Create dummy versions of the required classes/functions to prevent startup failure
        class SearchClient:
            def __init__(self):
                self.cognitive_search_client = None
                print("WARNING: Using dummy SearchClient")
                
            def search_contract_language(self, query):
                return [{"error": "SearchClient not properly initialized"}]
                
        def load_env():
            print("WARNING: Using dummy load_env function")
            
from flask import send_from_directory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables first
logger.info('Loading environment variables...')
load_env()
logger.info(f'Using search index: {os.getenv("AZURE_AI_SEARCH_INDEX")}')
logger.info(f'Using search endpoint: {os.getenv("AZURE_AI_SEARCH_ENDPOINT")}')
logger.info('='*50)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['static_folder'] = 'static'
    app.config['static_url_path'] = ''
    
    # Add CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
        
    @app.route('/')
    def root():
        return app.send_static_file('index.html')
    
    @app.route('/test', methods=['GET'])
    def test():
        logger.info('Test endpoint called')
        return jsonify({'status': 'ok'})
    
    # Initialize search client
    logger.info('Initializing search client...')
    search_client = SearchClient()
    logger.info('Search client initialized')
    
    @app.route('/api/search', methods=['POST'])
    def search():
        try:
            logger.info('\n' + '='*50)
            logger.info('Received search request')
            logger.info(f'Request data: {request.get_data(as_text=True)}')
            
            if not request.is_json:
                error_msg = 'Request must be JSON'
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
                
            query = request.json.get('query', '')
            logger.info('Search Request Details:')
            logger.info(f'Query: {query}')
            logger.info(f'Search Index: {os.getenv("AZURE_AI_SEARCH_INDEX")}')
            logger.info(f'Search Endpoint: {os.getenv("AZURE_AI_SEARCH_ENDPOINT")}')
            logger.info('='*50)
            
            # Validate environment variables
            required_vars = [
                'AZURE_AI_SEARCH_ENDPOINT',
                'AZURE_AI_SEARCH_INDEX',
                'AZURE_AI_SEARCH_API_KEY'
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                error_msg = f'Missing required environment variables: {", ".join(missing_vars)}'
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 500
            
            # Execute search
            logger.info('Executing search...')
            results = search_client.search_contract_language(query)
            logger.info(f'Got {len(results)} results')
            
            # Log the structure of the first result
            if results and len(results) > 0:
                logger.info('First search result structure:')
                logger.info('Available fields: ' + ', '.join(sorted(results[0].keys())))
                
                # Log important fields first
                important_fields = ['filename', 'metadata_storage_name', 'metadata_storage_path', 'filepath', 'url']
                for field in important_fields:
                    if field in results[0]:
                        logger.info(f'{field}: {results[0][field]}')
                
                # Log other fields
                for key, value in sorted(results[0].items()):
                    if key not in important_fields:
                        if key == 'content':
                            logger.info(f'{key}: [Content length: {len(str(value))} chars]')
                        else:
                            logger.info(f'{key}: {value}')
            
            return jsonify(results)
            
        except Exception as e:
            import traceback
            error_msg = f'Search error: {str(e)}'
            stack = traceback.format_exc()
            logger.error(error_msg)
            logger.error(stack)
            # Return full error details to the frontend for debugging
            return jsonify({'error': error_msg, 'trace': stack}), 500

    @app.route('/api/document/<path:doc_id>', methods=['GET'])
    def get_document(doc_id):
        try:
            # Get document from search index
            doc = search_client.cognitive_search_client.get_document(doc_id)
            if doc:
                return jsonify(doc)
            return jsonify({'error': 'Document not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

app = create_app()

# Expose the application variable that Azure App Service is looking for
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    build_dir = os.path.join(os.path.dirname(__file__), '../build')
    if path != "" and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    else:
        return send_from_directory(build_dir, 'index.html')