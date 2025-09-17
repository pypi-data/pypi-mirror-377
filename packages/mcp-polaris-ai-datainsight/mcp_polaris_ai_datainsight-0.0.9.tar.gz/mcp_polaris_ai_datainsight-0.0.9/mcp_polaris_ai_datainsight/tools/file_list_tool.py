import os
from pathlib import Path
from typing import List

def list_files_in_directories(directories: List[Path]) -> List[str]:
    """
    List all files in the given directories.
    
    Args:
        directories: List of directory paths to scan
        
    Returns:
        List of absolute file paths for all files found in the directories
    """
    all_files = []
    
    for directory in directories:
        try:
            # Check if directory exists
            if not directory.exists():
                print(f"Directory does not exist: {directory}")
                continue
                
            # Check if it's actually a directory
            if not directory.is_dir():
                print(f"Directory is not a directory: {directory}")
                continue
                
            # Check if we have read permission
            if not os.access(directory, os.R_OK):
                print(f"Directory is not readable: {directory}")
                continue
                
            # Recursively find all files in the directory
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    all_files.append(str(file_path.resolve()))
                elif file_path.is_dir():
                    files_in_subdir = list_files_in_directories([file_path])
                    all_files.extend(files_in_subdir)
                    
        except Exception as e:
            # Log error but continue with other directories
            print(f"Error accessing directory {directory}: {e}")
            continue
    
    return all_files