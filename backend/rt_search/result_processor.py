"""Process and transform search results."""
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def extract_filepath(item: Dict) -> Dict:
    """Extract filepath information from search result item."""
    # Log the raw item for debugging
    logger.info(f'Raw search result item: {json.dumps(item, indent=2)}')
    
    # Initialize result with all possible fields
    result = {
        'filename': '',
        'filepath': item.get('filepath', ''),
        'metadata_storage_path': item.get('metadata_storage_path', ''),
        'metadata_storage_name': item.get('metadata_storage_name', ''),
        'url': item.get('url', '')
    }
    
    # Log all available fields
    logger.info('Available fields:')
    for key, value in item.items():
        logger.info(f'{key}: {value}')
    
    # First try metadata_storage_name as it's the most reliable source
    if item.get('metadata_storage_name'):
        filename = item['metadata_storage_name']
        logger.info(f'Using metadata_storage_name: {filename}')
        result['filename'] = filename
        return result
        
    # Try other fields that might contain the filename
    filename_fields = ['filename', 'filepath', 'metadata_storage_path', 'path', 'url']
    for field in filename_fields:
        value = item.get(field)
        if not value:
            continue
            
        filepath = str(value)
        logger.info(f'Checking {field}: {filepath}')
        
        # If it's just a filename (no path separators), use it
        if '/' not in filepath and '\\' not in filepath:
            logger.info(f'Using clean filename from {field}: {filepath}')
            result['filename'] = filepath
            return result
    
    # If no clean filename found, try to extract from paths
    for field in fallback_fields:
        value = item.get(field)
        if not value:
            continue
            
        filepath = str(value)
        logger.info(f'Extracting filename from path in {field}: {filepath}')
        
        # Handle different path formats
        if filepath.startswith('http'):
            # Handle URL
            base_url = filepath.split('?')[0]
            parts = base_url.rstrip('/').split('/')
            if parts and parts[-1]:
                result['filename'] = parts[-1]
                logger.info(f'Extracted filename from URL: {result["filename"]}')
                return result
        elif '\\' in filepath:
            # Handle Windows path
            parts = filepath.rstrip('\\').split('\\')
            if parts and parts[-1]:
                result['filename'] = parts[-1]
                logger.info(f'Extracted filename from Windows path: {result["filename"]}')
                return result
        elif '/' in filepath:
            # Handle Unix path
            parts = filepath.rstrip('/').split('/')
            if parts and parts[-1]:
                result['filename'] = parts[-1]
                logger.info(f'Extracted filename from Unix path: {result["filename"]}')
                return result
    
    # If still no filename, use metadata_storage_name as fallback
    if item.get('metadata_storage_name'):
        result['filename'] = item['metadata_storage_name']
        logger.info(f'Using metadata_storage_name as fallback: {result["filename"]}')
        return result
    
    logger.warning('No filename found in any field')
    return result

def transform_result(item: Dict, idx: int) -> Dict:
    """Transform a single search result."""
    # Extract required fields with validation
    content = str(item.get('content', ''))
    context = str(item.get('context', ''))
    score = item.get('@search.score', 0)
    
    # Get highlights if available
    highlights = item.get('@search.highlights', {})
    highlighted_content = highlights.get('content', [content])[0] if highlights else content
    
    # Get semantic details if available
    captions = item.get('@search.captions', [])
    caption = captions[0].get('text') if captions else ''
    
    # Extract filepath information
    filepath_info = extract_filepath(item)
    
    # Ensure we have a filename, even if it's from the content
    filename = filepath_info['filename']
    if not filename:
        # Generate a preview from content as fallback
        content_preview = content[:50].strip()
        if len(content_preview) == 50:
            content_preview += '...'
        filename = content_preview
    
    # Combine all fields into result
    result = {
        'content': highlighted_content,  # Keep the highlighted content
        'context': context,
        'relevance': float(score),
        'summary': caption or context[:200] + '...' if context else '',
        'filename': filename,
        'filepath': filepath_info['filepath'],
        'metadata_storage_path': filepath_info['metadata_storage_path'],
        'metadata_storage_name': filepath_info['metadata_storage_name'],
        'url': filepath_info['url']
    }
    
    logger.info(f'\nTransformed result {idx + 1}:')
    logger.info(f'Result: {json.dumps(result, indent=2)}')
    
    # Additional debug logging
    logger.info(f'Filename in result: {result["filename"]}')
    logger.info(f'Metadata storage name: {result["metadata_storage_name"]}')
    logger.info(f'Filepath: {result["filepath"]}')
    
    print(f'Processing result {idx + 1}:')
    print(f'Filename: {result["filename"]}')
    print(f'Storage name: {result["metadata_storage_name"]}')
    print(f'Filepath: {result["filepath"]}')
    
    return result

def process_results(results: Dict) -> List[Dict]:
    """Process and transform search results."""
    if not isinstance(results, dict):
        logger.error(f'Expected dict response, got {type(results)}')
        return []
    
    if 'error' in results:
        logger.error(f'Search API error: {results}')
        return []
    
    # Get value array and handle no results case
    value = results.get('value', [])
    transformed = []
    
    for idx, item in enumerate(value):
        try:
            result = transform_result(item, idx)
            transformed.append(result)
        except Exception as e:
            logger.error(f'Error transforming result {idx}: {e}')
            continue
    
    logger.info(f'Transformed {len(transformed)} valid results')
    if transformed:
        logger.info(f'First result example: {transformed[0]}')
    
    return transformed
