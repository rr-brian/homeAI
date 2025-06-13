import os
import sys

# Add the backend directory to the path so we can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Try different import approaches for rt_search
try:
    # First try to add the rt_search module to the Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
    
    # Import the app from the backend
    from backend.wsgi import app
    print("Successfully imported app from backend.wsgi")
except ImportError as e:
    print(f"Error importing app: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir(os.getcwd())}")
    
    try:
        # Try an alternative import approach
        from wsgi import app
        print("Successfully imported app from wsgi")
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        
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

# This allows the app to be run directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
