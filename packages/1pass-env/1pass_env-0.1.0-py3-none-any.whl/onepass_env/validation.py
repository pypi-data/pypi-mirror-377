"""Input validation utilities for 1pass-env."""

import os
from pathlib import Path
from typing import List, Optional, Tuple


def validate_output_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate that we can write to the output file path.
    
    Args:
        file_path: Path to the output file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if directory exists and is writable
        directory = os.path.dirname(os.path.abspath(file_path))
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except PermissionError:
                return False, f"Cannot create directory '{directory}' - permission denied"
        
        # Check if we can write to the directory
        if not os.access(directory, os.W_OK):
            return False, f"Directory '{directory}' is not writable"
        
        # If file exists, check if it's writable
        if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
            return False, f"File '{file_path}' exists but is not writable"
        
        return True, None
    except Exception as e:
        return False, f"Path validation error: {str(e)}"


def validate_fields(field_names: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate field names for basic format.
    
    Args:
        field_names: List of field names to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not field_names:
        return True, None
    
    invalid_fields = []
    for field in field_names:
        # Basic validation: no spaces, not empty, reasonable length
        if not field.strip():
            invalid_fields.append("(empty)")
        elif ' ' in field:
            invalid_fields.append(f"'{field}' (contains spaces)")
        elif len(field) > 100:
            invalid_fields.append(f"'{field}' (too long)")
    
    if invalid_fields:
        return False, f"Invalid field names: {', '.join(invalid_fields)}"
    
    return True, None


def validate_input_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate that an input file exists and is readable.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"Input file '{file_path}' not found"
    
    if not os.access(file_path, os.R_OK):
        return False, f"Input file '{file_path}' is not readable"
    
    return True, None