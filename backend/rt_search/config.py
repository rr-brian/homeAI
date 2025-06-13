"""Configuration module for Azure Cognitive Search and OpenAI."""
import os
import logging
from typing import Dict
from .env_loader import load_env

logger = logging.getLogger(__name__)

def get_required_search_vars() -> Dict[str, str]:
    """Get required environment variables for search"""
    # Load environment variables first
    env_vars = load_env()
    
    # Use variables directly from env_loader
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_DEPLOYMENT',
        'AZURE_OPENAI_API_KEY',
        'AZURE_AI_SEARCH_ENDPOINT',
        'AZURE_AI_SEARCH_INDEX',
        'AZURE_AI_SEARCH_API_KEY'
    ]
    
    # Get all required variables
    vars = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f'Required environment variable {var} is not set')
        vars[var] = value
        
        # Log non-sensitive values
        if 'KEY' not in var and 'SECRET' not in var:
            logger.info(f'{var}: {value}')
    
    # Double check search index
    logger.info(f'Confirmed search index: {vars["AZURE_AI_SEARCH_INDEX"]}')
    
    return vars
