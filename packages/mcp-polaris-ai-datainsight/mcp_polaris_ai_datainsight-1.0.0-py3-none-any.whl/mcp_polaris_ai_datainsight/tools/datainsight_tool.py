import json
import logging
import os
from pathlib import Path
import traceback
from polaris_ai_datainsight import PolarisAIDataInsightExtractor
    
logger = logging.getLogger(__name__)

def call_datainsight_api(file_path: str) -> str:
    """
    Extract content from a document using Polaris AI DataInsight API.
    
    Args:
        file_path: Absolute path to the input document
        
    Returns:
        Extracted content in JSON format or error message
    """
    # Check if API Key is set in the environment variable
    if "POLARIS_AI_DATA_INSIGHT_API_KEY" not in os.environ:
        return "Please set the `POLARIS_AI_DATA_INSIGHT_API_KEY` environment variable."
    
    # Check if the resources directory is accessible and writable
    try:
        resources_dir = Path(os.environ.get("POLARIS_AI_DATA_INSIGHT_RESOURCES_DIR"))
                
        if not resources_dir.exists():
            return "The `resources_dir` is not found. Retry with a absolute file path."
        if not resources_dir.is_dir():
            return f"The `resources_dir` Path is not a directory: {resources_dir}"
        if not os.access(resources_dir, os.W_OK):
            return f"The `resources_dir` is not writable: {resources_dir}"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error: {str(e)}"
    
    # Check if the file path is valid
    try:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            return f"File is not found: {file_path}"
        if not file_path.is_file():
            return f"The path is not a regular file: {file_path}"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error checking file path: {str(e)}"
    
    # Check if the result directory exists and is writable
    try:
        resources_dir = Path(resources_dir).resolve()
        if not resources_dir.exists():
            return f"Result directory does not exist: {resources_dir}"
        if not resources_dir.is_dir():
            return f"Result path is not a directory: {resources_dir}"
        if not os.access(resources_dir, os.W_OK):
            return f"Result directory is not writable: {resources_dir}"
    except Exception as e:
        return f"Error checking result directory: {str(e)}"
    
    try:
        extractor = PolarisAIDataInsightExtractor(
            file_path=file_path, resources_dir=resources_dir
        )
        docs = extractor.extract()
        if not docs:
            return "No content extracted."
            
        try:
            docs_str = json.dumps(docs, indent=2, ensure_ascii=False)
            return docs_str            
        except json.JSONDecodeError:
            return "Error decoding JSON from extracted content."
        
    except Exception as e:
        return f"Error during extraction: {str(e)}"
