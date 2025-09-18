"""
Private key utilities for handling different key formats.

This module provides utilities to handle various private key formats
that organizations might use, ensuring compatibility with Snowflake.
"""

import os
import re
from typing import Optional
from .utils import setup_logger


def load_and_process_private_key(private_key_path: str, passphrase: Optional[str] = None) -> str:
    """
    Load and process private key to ensure Snowflake compatibility.
    
    Args:
        private_key_path: Path to the private key file
        passphrase: Optional passphrase for encrypted keys
        
    Returns:
        Processed private key content
        
    Raises:
        ValueError: If key cannot be processed
    """
    logger = setup_logger(__name__)
    
    try:
        # Read the private key file
        with open(private_key_path, 'r') as f:
            key_content = f.read()
        
        logger.debug(f"Loaded private key from: {private_key_path}")
        
        # Handle different key formats
        processed_key = _normalize_private_key_format(key_content)
        
        # Validate the key format
        if not _is_valid_private_key_format(processed_key):
            raise ValueError("Invalid private key format")
        
        return processed_key
        
    except Exception as e:
        logger.error(f"Failed to load private key from {private_key_path}: {e}")
        raise ValueError(f"Cannot load private key: {e}")


def _normalize_private_key_format(key_content: str) -> str:
    """
    Normalize private key format for Snowflake compatibility.
    
    Different organizations may use different formats:
    - Standard PEM format
    - PKCS#8 format
    - Custom certificate formats
    """
    # Remove any extra whitespace
    key_content = key_content.strip()
    
    # Check if it's already in proper PEM format
    if _is_valid_private_key_format(key_content):
        return key_content
    
    # Try to extract key from certificate format
    if "-----BEGIN CERTIFICATE-----" in key_content:
        # This is a certificate, not a private key
        raise ValueError("Certificate provided instead of private key")
    
    # Handle PKCS#8 format
    if "-----BEGIN PRIVATE KEY-----" in key_content:
        return key_content
    
    # Handle traditional RSA format
    if "-----BEGIN RSA PRIVATE KEY-----" in key_content:
        return key_content
    
    # Handle encrypted private key
    if "-----BEGIN ENCRYPTED PRIVATE KEY-----" in key_content:
        return key_content
    
    # If no headers, try to add them (some systems strip headers)
    lines = key_content.split('\n')
    if len(lines) > 1 and not any('-----BEGIN' in line for line in lines):
        # Assume it's a base64-encoded key without headers
        clean_content = ''.join(lines)
        return f"-----BEGIN PRIVATE KEY-----\n{clean_content}\n-----END PRIVATE KEY-----"
    
    return key_content


def _is_valid_private_key_format(key_content: str) -> bool:
    """Check if the key content is in a valid format for Snowflake."""
    # Check for standard PEM headers
    valid_headers = [
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN RSA PRIVATE KEY-----", 
        "-----BEGIN ENCRYPTED PRIVATE KEY-----"
    ]
    
    return any(header in key_content for header in valid_headers)


def extract_public_key_for_snowflake(private_key_path: str, passphrase: Optional[str] = None) -> str:
    """
    Extract public key from private key in format suitable for Snowflake.
    
    Args:
        private_key_path: Path to private key file
        passphrase: Optional passphrase
        
    Returns:
        Public key in format for Snowflake ALTER USER command
    """
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        
        # Load private key
        with open(private_key_path, 'rb') as f:
            private_key_data = f.read()
        
        # Parse private key
        passphrase_bytes = passphrase.encode() if passphrase else None
        private_key = load_pem_private_key(private_key_data, password=passphrase_bytes)
        
        # Extract public key
        public_key = private_key.public_key()
        
        # Serialize public key in PEM format
        public_pem = public_key.serialize(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Convert to Snowflake format (remove headers and newlines)
        public_key_content = public_pem.decode('utf-8')
        lines = public_key_content.split('\n')
        key_data = ''.join(line for line in lines if not line.startswith('-----'))
        
        return key_data
        
    except ImportError:
        raise ValueError("cryptography library required for key extraction")
    except Exception as e:
        raise ValueError(f"Failed to extract public key: {e}")


def validate_key_pair_compatibility(private_key_path: str, passphrase: Optional[str] = None) -> bool:
    """
    Validate that the private key is properly formatted and accessible.
    
    Args:
        private_key_path: Path to private key
        passphrase: Optional passphrase
        
    Returns:
        True if key is valid and accessible
    """
    try:
        # Try to load and process the key
        processed_key = load_and_process_private_key(private_key_path, passphrase)
        
        # Try to extract public key (validates key can be parsed)
        public_key = extract_public_key_for_snowflake(private_key_path, passphrase)
        
        return len(public_key) > 100  # Basic sanity check
        
    except Exception:
        return False


def get_snowflake_key_setup_sql(private_key_path: str, username: str, passphrase: Optional[str] = None) -> str:
    """
    Generate SQL command to set up public key in Snowflake.
    
    Args:
        private_key_path: Path to private key
        username: Snowflake username
        passphrase: Optional passphrase
        
    Returns:
        SQL command to run in Snowflake
    """
    try:
        public_key = extract_public_key_for_snowflake(private_key_path, passphrase)
        
        sql = f"""
-- Set up public key for user {username}
ALTER USER {username} SET RSA_PUBLIC_KEY='{public_key}';

-- Verify the key was set
DESCRIBE USER {username};
"""
        return sql
        
    except Exception as e:
        return f"-- Error generating SQL: {e}"
