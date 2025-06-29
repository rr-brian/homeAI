"""Environment variable loader module."""
import os
import logging
from dotenv import load_dotenv
from typing import Dict

def load_env() -> Dict[str, str]:
    """Load environment variables."""
    logger = logging.getLogger(__name__)
    logger.info('Loading environment variables...')
    
    # Don't clear existing environment variables as they might be set by Azure App Service
    # Just log what we have
    for key in ['AZURE_AI_SEARCH_INDEX', 'AZURE_AI_SEARCH_ENDPOINT', 'AZURE_AI_SEARCH_API_KEY',
                'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_DEPLOYMENT', 'AZURE_OPENAI_API_KEY']:
        if key in os.environ:
            logger.info(f'Found existing environment variable: {key}')
        else:
            logger.info(f'Environment variable not found: {key}')
    
    # Read .env file directly first
    try:
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            logger.info(f'Reading .env file directly: {env_path}')
            with open(env_path, 'r') as f:
                env_contents = f.read()
                logger.info('Raw .env contents:')
                for line in env_contents.splitlines():
                    if line.startswith('AZURE_AI_SEARCH_INDEX='):
                        logger.info(f'Found index line: {line}')
                        index_value = line.split('=')[1]
                        os.environ['AZURE_AI_SEARCH_INDEX'] = index_value
                        logger.info(f'Set AZURE_AI_SEARCH_INDEX to: {index_value}')
            
            # Now load all variables
            logger.info('Loading all variables from .env')
            load_dotenv(env_path, override=True)
            
            # Verify the index name
            index_name = os.getenv('AZURE_AI_SEARCH_INDEX')
            logger.info(f'Final index name: {index_name}')
            if index_name != 'idxlegalv2':
                logger.warning(f'Expected index name idxlegalv2 but got {index_name}')
    except Exception as e:
        logger.error(f'Error loading .env file: {str(e)}')
    
    # Required environment variables
    required_vars = {
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI endpoint',
        'AZURE_OPENAI_DEPLOYMENT': 'Azure OpenAI deployment name',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI credential',
        'AZURE_AI_SEARCH_ENDPOINT': 'Azure AI Search endpoint',
        'AZURE_AI_SEARCH_INDEX': 'Azure AI Search index name',
        'AZURE_AI_SEARCH_API_KEY': 'Azure AI Search credential'
    }
    
    # Default values for development environment
    default_values = {
        'AZURE_OPENAI_ENDPOINT': 'https://example.openai.azure.com/',
        'AZURE_OPENAI_DEPLOYMENT': 'gpt-35-turbo',
        'AZURE_OPENAI_API_KEY': 'dummy_key_for_development',
        'AZURE_AI_SEARCH_ENDPOINT': 'https://example.search.windows.net',
        'AZURE_AI_SEARCH_INDEX': 'example-index',
        'AZURE_AI_SEARCH_API_KEY': 'dummy_key_for_development',
        'AZURE_GEN_SEARCH_ENDPOINT': 'https://example.cognitiveservices.azure.com/',
        'AZURE_GEN_SEARCH_DEPLOYMENT': 'gpt-35-turbo',
        'AZURE_GEN_SEARCH_API_KEY': 'dummy_key_for_development',
    }

    # Check for missing environment variables
    missing_vars = []
    env_vars = {}
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"{var} ({description})")
            # Set default value in development mode
            if os.environ.get('FLASK_ENV') == 'development' and var in default_values:
                os.environ[var] = default_values[var]
                logger.warning(f"Using default value for {var} in development mode")
        else:
            # Log variable found (without revealing sensitive values)
            if 'KEY' in var or 'CREDENTIAL' in var:
                logger.info(f'Found {var} in environment [value hidden]')
                logger.debug(f'{var} length: {len(value)}')
            else:
                logger.info(f'Found {var} in environment: {value}')
            env_vars[var] = value

    if missing_vars:
        error = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.warning(error)
        
        # Only raise error if not in development mode
        if os.environ.get('FLASK_ENV') != 'development':
            raise ValueError(error)
        else:
            logger.warning("Continuing with default values in development mode")
            
    # Set optional environment variables with defaults if not present
    for var, value in default_values.items():
        if var not in required_vars and not os.environ.get(var):
            os.environ[var] = value
            logger.info(f"Set default value for optional variable {var}")
            
    # Log summary
    logger.info('Environment variables loaded successfully:')
    logger.info(f'OpenAI endpoint: {env_vars.get("AZURE_OPENAI_ENDPOINT", "[missing]")}') 
    logger.info(f'OpenAI deployment: {env_vars.get("AZURE_OPENAI_DEPLOYMENT", "[missing]")}') 
    logger.info(f'Search endpoint: {env_vars.get("AZURE_AI_SEARCH_ENDPOINT", "[missing]")}') 
    logger.info(f'Search index: {env_vars.get("AZURE_AI_SEARCH_INDEX", "[missing]")}') 

    # Log final status
    logger.info('Environment variables loaded successfully')
            
    # Return the environment variables
    return env_vars
