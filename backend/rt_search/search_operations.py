"""Search operations for Azure Cognitive Search."""
import json
import logging
import re
from typing import Dict, List

import requests
from .base_client import BaseSearchClient
from .result_processor import process_results

logger = logging.getLogger(__name__)

class SearchOperations(BaseSearchClient):
    """Search operations implementation."""
    
    def search(self, query: str) -> List[Dict]:
        """Execute a search query."""
        logger.info('='*50)
        logger.info(f'Search Configuration:')
        logger.info(f'Endpoint: {self._endpoint}')
        logger.info(f'Index: {self._index_name}')
        logger.info(f'Query: {query}')
        logger.info('='*50)
        
        # Clean and process the query
        cleaned_query = query.strip()
        print(f'\nProcessing query: {cleaned_query}')
        
        # Basic cleaning - only remove special characters
        cleaned_query = re.sub(r'[^\w\s]', '', cleaned_query)
        print(f'Cleaned query: {cleaned_query}')
        
        # Split into terms for fuzzy search
        terms = cleaned_query.split()
        print(f'Search terms: {terms}')
        
        # Build fuzzy search query
        if terms:
            # Add fuzzy search for each term
            fuzzy_terms = [f'{term}~1' for term in terms]
            cleaned_query = ' OR '.join(fuzzy_terms)
            print(f'Fuzzy search query: {cleaned_query}')
        logger.info(f'Cleaned query: {cleaned_query}')
        
        # Get fields from index inspection
        select_fields = self.retrievable_fields if hasattr(self, 'retrievable_fields') else ['*']
        search_fields = self.searchable_fields if hasattr(self, 'searchable_fields') else ['content', 'title']
        
        # Log available fields
        logger.info(f'Available retrievable fields: {select_fields}')
        logger.info(f'Available searchable fields: {search_fields}')
        
        # Prepare search parameters
        search_params = {
            'search': cleaned_query,
            'queryType': 'full',  # Use full Lucene query syntax for fuzzy search
            'top': 50,
            'select': ','.join(select_fields),  # Use all retrievable fields
            'searchFields': ','.join(search_fields),  # Use all searchable fields
            'searchMode': 'any',  # Allow any term to match for fuzzy search
            'count': True,
            'orderby': 'search.score() desc',
            'highlight': 'content,title',  # Highlight matches in both content and title
            'highlightPreTag': '<mark>',
            'highlightPostTag': '</mark>',
            'minimumCoverage': 25  # Allow more partial matches
        }
        
        # Log search configuration
        logger.info('Search configuration:')
        for key, value in search_params.items():
            logger.info(f'  {key}: {value}')
        
        try:
            # Log request details
            headers = {
                'Content-Type': 'application/json',
                'api-key': self._auth,
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Log full request details
            print('\nSearch request details:')
            print(f'URL: {self.search_url}')
            print('Headers:', {k: v if k != 'api-key' else '***' for k, v in headers.items()})
            print('Search parameters:', json.dumps(search_params, indent=2))
            
            # Make request
            logger.info('Making search request...')
            response = requests.post(
                self.search_url,
                headers=headers,
                json=search_params
            )
            
            # Log response details
            print('\nSearch response details:')
            print(f'Status code: {response.status_code}')
            print('Response headers:', dict(response.headers))
            print('Response content:', response.text)
            
            try:
                # Parse and log raw response
                results = response.json()
                print(f'Got {len(results.get("value", []))} results')
                
                # Log raw search results with all available fields
                print('Raw search results from Azure Search:')
                if results.get('value'):
                    for idx, result in enumerate(results['value']):
                        print('='*80)
                        print(f'Result {idx + 1} fields:')
                        
                        # Log all available fields
                        field_names = sorted(result.keys())
                        print('Available fields: ' + ', '.join(field_names))
                        
                        # Log metadata fields
                        metadata_fields = [f for f in field_names if f.startswith('metadata_')]
                        if metadata_fields:
                            print('\nMetadata fields:')
                            for field in metadata_fields:
                                print(f'{field}: {result[field]}')
                        
                        # Log filename-related fields
                        filename_fields = ['filename', 'filepath', 'url', 'path', 'name']
                        found_fields = [f for f in filename_fields if f in field_names]
                        if found_fields:
                            print('\nFilename-related fields:')
                            for field in found_fields:
                                print(f'{field}: {result[field]}')
                        
                        # Log content preview
                        if 'content' in result:
                            content = str(result['content'])
                            print(f'\nContent preview (first 200 chars):\n{content[:200]}...')
                        
                        # Log search score
                        if '@search.score' in result:
                            print(f'\nSearch score: {result["@search.score"]}')
                        
                        print('\n') # Add extra newline for readability
                
                # Log complete raw response for debugging
                logger.info('\nComplete raw response:')
                logger.info(json.dumps(results, indent=2))
                
                # Log raw search results
                logger.info('Raw search results:')
                print('\nRaw search results:')
                print(json.dumps(results, indent=2))
                
                for idx, result in enumerate(results.get('value', [])):
                    logger.info(f'\nResult {idx + 1}:')
                    logger.info('Available fields: ' + ', '.join(result.keys()))
                    print(f'\nResult {idx + 1}:')
                    print('Available fields:', ', '.join(result.keys()))
                    
                    # Log all fields for debugging
                    for field, value in result.items():
                        logger.info(f'{field}: {value}')
                        print(f'{field}: {value}')
                    
                    # Specifically log filename-related fields
                    logger.info(f'filepath: {result.get("filepath")}')
                    logger.info(f'metadata_storage_path: {result.get("metadata_storage_path")}')
                    logger.info(f'metadata_storage_name: {result.get("metadata_storage_name")}')
                    logger.info(f'url: {result.get("url")}')
                
                # Process results
                processed_results = process_results(results)
                
                # Log processed results
                logger.info('\nProcessed results:')
                for idx, result in enumerate(processed_results):
                    logger.info(f'\nProcessed result {idx + 1}:')
                    logger.info('Available fields: ' + ', '.join(result.keys()))
                    logger.info(f'filename: {result.get("filename")}')
                    logger.info(f'filepath: {result.get("filepath")}')
                    logger.info(f'metadata_storage_path: {result.get("metadata_storage_path")}')
                
                return processed_results
                
            except ValueError as e:
                logger.error(f'Failed to parse JSON response: {e}')
                logger.error(f'Raw response text: {response.text[:1000]}')
                return []
        
        except Exception as e:
            logger.error(f'Search failed: {str(e)}')
            logger.error(f'Exception type: {type(e).__name__}')
            if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
                logger.error(f'Response status: {e.response.status_code}')
                logger.error(f'Response text: {e.response.text[:1000]}')
            return []
