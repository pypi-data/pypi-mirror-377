"""
Utility functions for Snowflake Connector.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with consistent formatting."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger


def sanitize_query(query: str) -> str:
    """Sanitize SQL query for logging (remove sensitive information)."""
    # Basic sanitization - remove potential passwords, tokens etc.
    import re
    
    # Remove quoted strings that might contain sensitive data
    sanitized = re.sub(r"'[^']*'", "'***'", query)
    sanitized = re.sub(r'"[^"]*"', '"***"', sanitized)
    
    return sanitized


def format_connection_info(config: Dict[str, Any]) -> str:
    """Format connection information for logging (without sensitive data)."""
    safe_config = config.copy()
    
    # Remove sensitive information
    sensitive_keys = ['password', 'private_key_path', 'private_key_passphrase']
    for key in sensitive_keys:
        if key in safe_config:
            safe_config[key] = '***'
    
    return str(safe_config)


def validate_query(query: str) -> bool:
    """Basic validation of SQL queries."""
    if not query or not query.strip():
        return False
    
    # Check for potentially dangerous operations (basic protection)
    dangerous_keywords = ['drop', 'delete', 'truncate', 'alter']
    query_lower = query.lower().strip()
    
    # Allow these operations but log them
    for keyword in dangerous_keywords:
        if query_lower.startswith(keyword):
            logging.getLogger(__name__).warning(
                f"Potentially destructive operation detected: {keyword.upper()}"
            )
    
    return True


def parse_snowflake_identifier(identifier: str) -> Dict[str, Optional[str]]:
    """Parse Snowflake three-part identifier (database.schema.object)."""
    parts = identifier.split('.')
    
    if len(parts) == 1:
        return {'database': None, 'schema': None, 'object': parts[0]}
    elif len(parts) == 2:
        return {'database': None, 'schema': parts[0], 'object': parts[1]}
    elif len(parts) == 3:
        return {'database': parts[0], 'schema': parts[1], 'object': parts[2]}
    else:
        raise ValueError(f"Invalid Snowflake identifier: {identifier}")


def convert_snowflake_timestamp(timestamp_str: str) -> datetime:
    """Convert Snowflake timestamp string to Python datetime."""
    try:
        # Handle common Snowflake timestamp formats
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")
    
    except Exception as e:
        raise ValueError(f"Error parsing timestamp {timestamp_str}: {str(e)}")
