"""Base client for Azure Cognitive Search."""
import json
import logging

import requests

logger = logging.getLogger(__name__)

class BaseSearchClient:
    """Base client with core functionality."""
    
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        """Initialize the base client.
        
        Args:
            endpoint (str): Azure Cognitive Search endpoint
            index_name (str): Name of the search index
            api_key (str): API key for authentication
        """
        self._endpoint = endpoint.rstrip('/')
        self._index_name = index_name
        self._auth = api_key
        self._api_version = '2023-07-01-Preview'
        self.search_url = f'{self._endpoint}/indexes/{self._index_name}/docs/search?api-version={self._api_version}'
        
        # Initialize by inspecting index
        self.inspect_index()
    
    def inspect_index(self):
        """Inspect the search index to understand its schema."""
        try:
            logger.info('\n' + '='*50)
            logger.info('INSPECTING SEARCH INDEX')
            logger.info(f'Endpoint: {self._endpoint}')
            logger.info(f'Index: {self._index_name}')
            
            # Get index definition
            index_url = f"{self._endpoint}/indexes/{self._index_name}?api-version={self._api_version}"
            logger.info(f'Requesting index schema from: {index_url}')
            
            response = requests.get(
                index_url,
                headers={
                    'Content-Type': 'application/json',
                    'api-key': self._auth
                }
            )
            
            logger.info(f'Response status: {response.status_code}')
            
            if response.status_code == 200:
                index_def = response.json()
                logger.info('\nIndex Configuration:')
                logger.info(f'Name: {index_def.get("name")}')
                logger.info(f'ETag: {index_def.get("@odata.etag")}')
                
                # Log field information
                fields = index_def.get('fields', [])
                logger.info(f'\nFound {len(fields)} fields:')
                
                # Track important fields
                has_filename = False
                has_content = False
                has_metadata = False
                
                # Log each field's details
                for field in fields:
                    field_info = {
                        'name': field.get('name'),
                        'type': field.get('type'),
                        'key': field.get('key', False),
                        'searchable': field.get('searchable', False),
                        'filterable': field.get('filterable', False),
                        'sortable': field.get('sortable', False),
                        'facetable': field.get('facetable', False),
                        'retrievable': field.get('retrievable', False)
                    }
                    
                    # Check for important fields
                    if field_info['name'] == 'filename':
                        has_filename = True
                    elif field_info['name'] == 'content':
                        has_content = True
                    elif field_info['name'].startswith('metadata_'):
                        has_metadata = True
                    
                    logger.info(f'\nField: {field_info["name"]}')
                    logger.info(f'Type: {field_info["type"]}')
                    logger.info(f'Properties: ' + 
                              f'key={field_info["key"]}, ' +
                              f'searchable={field_info["searchable"]}, ' +
                              f'filterable={field_info["filterable"]}, ' +
                              f'sortable={field_info["sortable"]}, ' +
                              f'facetable={field_info["facetable"]}, ' +
                              f'retrievable={field_info["retrievable"]}')
                
                # Store field information for later use
                self.searchable_fields = [f['name'] for f in fields if f.get('searchable', False)]
                self.retrievable_fields = [f['name'] for f in fields if f.get('retrievable', False)]
                
                # Log field availability summary
                logger.info('\nField Availability Summary:')
                logger.info(f'Filename field present: {has_filename}')
                logger.info(f'Content field present: {has_content}')
                logger.info(f'Metadata fields present: {has_metadata}')
                logger.info(f'Total searchable fields: {len(self.searchable_fields)}')
                logger.info(f'Total retrievable fields: {len(self.retrievable_fields)}')
                
                # Log searchable and retrievable fields
                logger.info('\nSearchable fields:')
                for field in self.searchable_fields:
                    logger.info(f'- {field}')
                    
                logger.info('\nRetrievable fields:')
                for field in self.retrievable_fields:
                    logger.info(f'- {field}')
                
            else:
                logger.error(f'Failed to get index definition: {response.status_code}')
                logger.error(f'Response: {response.text}')
                
            logger.info('='*50)
                
        except Exception as e:
            logger.error('='*50)
            logger.error('Error inspecting index:')
            logger.exception(str(e))
            logger.error('='*50)
