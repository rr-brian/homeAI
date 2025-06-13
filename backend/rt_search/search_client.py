"""Search client module combining Azure Cognitive Search and OpenAI."""
import logging
from typing import Dict, List, Union
from .cognitive_search_client import CognitiveSearchClient
from .openai_client import OpenAIClient
from .config import get_required_search_vars

logger = logging.getLogger(__name__)

class SearchClient:
    def __init__(self):
        """Initialize the client"""
        try:
            # Get required variables
            required_vars = get_required_search_vars()
            
            # Log configuration with detailed debugging
            logger.info('\n' + '='*50)
            logger.info('Search Client Configuration:')
            logger.info(f'Search endpoint: {required_vars["AZURE_AI_SEARCH_ENDPOINT"]}')
            logger.info(f'Search index: {required_vars["AZURE_AI_SEARCH_INDEX"]}')
            logger.info(f'OpenAI endpoint: {required_vars["AZURE_OPENAI_ENDPOINT"]}')
            logger.info(f'OpenAI deployment: {required_vars["AZURE_OPENAI_DEPLOYMENT"]}')
            
            # Validate API keys (log last 4 chars only)
            logger.info(f'Search API key present: {bool(required_vars["AZURE_AI_SEARCH_API_KEY"])} (ends with: ...{required_vars["AZURE_AI_SEARCH_API_KEY"][-4:] if required_vars["AZURE_AI_SEARCH_API_KEY"] else "None"})')
            logger.info(f'OpenAI API key present: {bool(required_vars["AZURE_OPENAI_API_KEY"])} (ends with: ...{required_vars["AZURE_OPENAI_API_KEY"][-4:] if required_vars["AZURE_OPENAI_API_KEY"] else "None"})')
            
            # Initialize Cognitive Search client
            logger.info('\nInitializing Cognitive Search client...')
            self.cognitive_search_client = CognitiveSearchClient(
                endpoint=required_vars['AZURE_AI_SEARCH_ENDPOINT'],
                index_name=required_vars['AZURE_AI_SEARCH_INDEX'],
                api_key=required_vars['AZURE_AI_SEARCH_API_KEY']
            )
            
            # Initialize OpenAI client
            logger.info('Initializing OpenAI client...')
            self.openai_client = OpenAIClient(
                endpoint=required_vars['AZURE_OPENAI_ENDPOINT'],
                deployment=required_vars['AZURE_OPENAI_DEPLOYMENT'],
                api_key=required_vars['AZURE_OPENAI_API_KEY']
            )
            
            logger.info('SearchClient initialization complete')
            logger.info('='*50)
            
        except Exception as e:
            logger.error('='*50)
            logger.error('Error initializing SearchClient:')
            logger.exception(str(e))
            logger.error('='*50)
            raise

    def search_contract_language(self, query: str) -> Union[Dict, List[Dict]]:
        """Search for contract language and get OpenAI completion"""
        try:
            # Execute search
            search_results = self.cognitive_search_client.search(query)
            
            if not search_results:
                logger.warning('No search results found')
                return []
            
            # Extract content from results
            content = []
            for result in search_results:
                if isinstance(result, dict) and 'content' in result:
                    content.append(result['content'])
            
            # Get completion from OpenAI
            context = '\n'.join(content)
            completion = self.openai_client.get_completion(query, context)
            
            # Return formatted results with all fields
            formatted_results = []
            for idx, result in enumerate(search_results):
                # Start with all fields from the result
                formatted_result = dict(result)
                
                # Add or update specific fields
                formatted_result.update({
                    'content': result.get('content', ''),
                    'context': result.get('context', ''),
                    'relevance': result.get('@search.score', 0),
                    'summary': completion if idx == 0 else '',
                    'filepath': result.get('filepath', ''),
                    'metadata_storage_path': result.get('metadata_storage_path', ''),
                    'metadata_storage_name': result.get('metadata_storage_name', ''),
                    'url': result.get('url', '')
                })
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f'Search failed: {str(e)}')
            return {'error': str(e)}
