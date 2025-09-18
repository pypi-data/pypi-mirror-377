"""
Configuration management for Snowflake Connector.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, validator
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class SnowflakeConfig(BaseModel):
    """Configuration class for Snowflake connection parameters - PKCS#8 KEY-BASED AUTH ONLY."""

    account: str
    user: str
    # SECURITY: Password authentication removed - PKCS#8 private key only!
    private_key_path: str  # REQUIRED - path to PKCS#8 private key file (.p8 or .pk8)
    private_key_passphrase: Optional[str] = None  # Recommended for encrypted PKCS#8 keys
    warehouse: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    role: Optional[str] = None
    authenticator: str = "snowflake"
    ocsp_response_cache_filename: Optional[str] = None
    network_timeout: int = 60
    login_timeout: int = 120
    
    # Connection pooling configuration
    use_connection_pool: bool = False
    pool_min_connections: int = 1
    pool_max_connections: int = 10
    pool_max_connection_age: int = 3600  # 1 hour
    pool_max_idle_time: int = 300        # 5 minutes
    pool_health_check_interval: int = 60  # 1 minute
    pool_connection_timeout: int = 30     # 30 seconds
    pool_enable_health_checks: bool = True
    pool_auto_cleanup: bool = True
    
    @validator('private_key_path')
    def validate_private_key_path(cls, v):
        """Ensure PKCS#8 private key path is provided and valid."""
        if not v:
            raise ValueError("private_key_path is required - only PKCS#8 private key authentication supported")

        # Check if file exists
        import os
        if not os.path.exists(v):
            raise ValueError(f"PKCS#8 private key file not found: {v}")

        # Validate PKCS#8 format
        try:
            with open(v, 'r') as f:
                key_content = f.read()
            
            # Fix common formatting issues (literal \n to actual newlines)
            if '\\n' in key_content:
                key_content = key_content.replace('\\n', '\n')
            
            # Check for PKCS#8 format headers
            valid_pkcs8_headers = [
                "-----BEGIN PRIVATE KEY-----",        # Unencrypted PKCS#8
                "-----BEGIN ENCRYPTED PRIVATE KEY-----"  # Encrypted PKCS#8
            ]
            
            if not any(header in key_content for header in valid_pkcs8_headers):
                raise ValueError(
                    f"Invalid key format. Only PKCS#8 format keys are supported. "
                    f"Expected: 'BEGIN PRIVATE KEY' or 'BEGIN ENCRYPTED PRIVATE KEY', "
                    f"but found: {key_content[:50]}..."
                )
                
        except Exception as e:
            if "Invalid key format" in str(e):
                raise e
            else:
                raise ValueError(f"Cannot validate PKCS#8 key format: {e}")

        # Check file permissions (should be readable only by owner)
        try:
            import stat
            file_stat = os.stat(v)
            if file_stat.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
                raise ValueError(f"PKCS#8 key file has insecure permissions: {v}. Use: chmod 600 {v}")
        except Exception:
            pass  # Skip permission check on systems that don't support it

        return v
    
    @validator('private_key_passphrase')
    def validate_passphrase_security(cls, v, values):
        """Recommend using encrypted private keys."""
        if not v and values.get('private_key_path'):
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Consider using an encrypted private key with passphrase for enhanced security")
        return v
    
    @classmethod
    def _get_passphrase_from_env(cls) -> Optional[str]:
        """Get passphrase from environment variables or file."""
        # Try direct environment variable first
        passphrase = (
            os.getenv('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE') or
            os.getenv('SF_PASSPHRASE') or
            os.getenv('SNOWFLAKE_PASSPHRASE')
        )
        
        if passphrase:
            return passphrase
        
        # Try reading from passphrase file
        passphrase_file = (
            os.getenv('SF_PASSPHRASE_FILE') or
            os.getenv('SNOWFLAKE_PASSPHRASE_FILE')
        )
        
        if passphrase_file and os.path.exists(passphrase_file):
            try:
                with open(passphrase_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass  # Fall back to None
        
        return None
    
    @classmethod
    def from_env(cls) -> 'SnowflakeConfig':
        """Create configuration from environment variables."""
        # Support multiple private key environment variable names
        private_key_path = (
            os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH') or 
            os.getenv('SF_PRIVATE_KEY_PEP8') or 
            os.getenv('SF_PRIVATE_KEY') or
            os.getenv('SNOWFLAKE_PRIVATE_KEY')
        )
        
        if not private_key_path:
            raise ValueError(
                "PKCS#8 private key path is required. Supported environment variables: "
                "SNOWFLAKE_PRIVATE_KEY_PATH, SF_PRIVATE_KEY_PEP8, SF_PRIVATE_KEY, or SNOWFLAKE_PRIVATE_KEY. "
                "Only PKCS#8 format keys (.p8, .pk8) are supported."
            )
        
        return cls(
            account=os.getenv('SNOWFLAKE_ACCOUNT', ''),
            user=os.getenv('SNOWFLAKE_USER', ''),
            # SECURITY: Password authentication removed
            private_key_path=private_key_path,
            private_key_passphrase=cls._get_passphrase_from_env(),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            role=os.getenv('SNOWFLAKE_ROLE'),
            authenticator=os.getenv('SNOWFLAKE_AUTHENTICATOR', 'snowflake'),
            network_timeout=int(os.getenv('SNOWFLAKE_NETWORK_TIMEOUT', '60')),
            login_timeout=int(os.getenv('SNOWFLAKE_LOGIN_TIMEOUT', '120')),
            
            # Connection pool settings from environment
            use_connection_pool=os.getenv('SNOWFLAKE_USE_POOL', 'false').lower() == 'true',
            pool_min_connections=int(os.getenv('SNOWFLAKE_POOL_MIN_CONNECTIONS', '1')),
            pool_max_connections=int(os.getenv('SNOWFLAKE_POOL_MAX_CONNECTIONS', '10')),
            pool_max_connection_age=int(os.getenv('SNOWFLAKE_POOL_MAX_CONNECTION_AGE', '3600')),
            pool_max_idle_time=int(os.getenv('SNOWFLAKE_POOL_MAX_IDLE_TIME', '300')),
            pool_health_check_interval=int(os.getenv('SNOWFLAKE_POOL_HEALTH_CHECK_INTERVAL', '60')),
            pool_connection_timeout=int(os.getenv('SNOWFLAKE_POOL_CONNECTION_TIMEOUT', '30')),
            pool_enable_health_checks=os.getenv('SNOWFLAKE_POOL_ENABLE_HEALTH_CHECKS', 'true').lower() == 'true',
            pool_auto_cleanup=os.getenv('SNOWFLAKE_POOL_AUTO_CLEANUP', 'true').lower() == 'true'
        )
    
    def to_connection_params(self) -> Dict[str, Any]:
        """Convert config to connection parameters dictionary."""
        params = {
            'account': self.account,
            'user': self.user,
            'authenticator': self.authenticator,
            'network_timeout': self.network_timeout,
            'login_timeout': self.login_timeout
        }
        
        # SECURITY: Only PKCS#8 private key authentication supported
        # Convert encrypted PKCS#8 key to format Snowflake expects
        try:
            # Import cryptography for PKCS#8 key processing
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            
            # Read the PKCS#8 private key and fix format if needed
            with open(self.private_key_path, 'r') as f:
                key_content = f.read()
            
            # Fix common formatting issues (literal \n to actual newlines)
            if '\\n' in key_content:
                key_content = key_content.replace('\\n', '\n')
            
            pkcs8_key_data = key_content.encode()
            
            # Decrypt the PKCS#8 private key using the passphrase
            passphrase_bytes = self.private_key_passphrase.encode() if self.private_key_passphrase else None
            private_key = load_pem_private_key(pkcs8_key_data, password=passphrase_bytes)
            
            # Convert to unencrypted DER PKCS#8 format (what Snowflake expects)
            der_private_key = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Pass the unencrypted DER PKCS#8 key to Snowflake
            params['private_key'] = der_private_key
            # Don't pass passphrase since we've already decrypted the key
            
        except ImportError:
            # Fallback if cryptography not available
            import logging
            logger = logging.getLogger(__name__)
            logger.error("cryptography library required for PKCS#8 encrypted private keys")
            params['private_key_path'] = self.private_key_path
            if self.private_key_passphrase:
                params['private_key_passphrase'] = self.private_key_passphrase
                
        except Exception as e:
            # Fallback to file path method
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"PKCS#8 key conversion failed, using fallback: {e}")
            params['private_key_path'] = self.private_key_path
            if self.private_key_passphrase:
                params['private_key_passphrase'] = self.private_key_passphrase
        
        if self.warehouse:
            params['warehouse'] = self.warehouse
        if self.database:
            params['database'] = self.database
        if self.schema:
            params['schema'] = self.schema
        if self.role:
            params['role'] = self.role
        if self.ocsp_response_cache_filename:
            params['ocsp_response_cache_filename'] = self.ocsp_response_cache_filename
            
        return params
