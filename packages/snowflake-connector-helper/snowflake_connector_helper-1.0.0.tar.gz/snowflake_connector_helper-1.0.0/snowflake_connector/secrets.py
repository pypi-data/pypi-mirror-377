"""
Secret Management Integration for Snowflake Connector.

This module provides integration with various secret management systems
for enhanced credential security beyond environment variables.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    import hvac
    HVAC_AVAILABLE = True
except ImportError:
    HVAC_AVAILABLE = False

from .config import SnowflakeConfig
from .exceptions import ConfigurationError
from .utils import setup_logger


@dataclass
class SecretManagerConfig:
    """Configuration for secret manager integration."""
    provider: str  # 'aws', 'vault', 'azure', 'gcp'
    region: Optional[str] = None
    vault_url: Optional[str] = None
    vault_token: Optional[str] = None
    secret_path: Optional[str] = None
    role_arn: Optional[str] = None


class SecretProvider(ABC):
    """Abstract base class for secret providers."""
    
    @abstractmethod
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret from the provider."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class AWSSecretsManagerProvider(SecretProvider):
    """AWS Secrets Manager integration."""
    
    def __init__(self, config: SecretManagerConfig):
        self.config = config
        self.logger = setup_logger(self.__class__.__name__)
        
        if not BOTO3_AVAILABLE:
            raise ConfigurationError("boto3 is required for AWS Secrets Manager")
        
        self.client = boto3.client(
            'secretsmanager',
            region_name=config.region or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            self.logger.debug(f"Retrieving secret from AWS Secrets Manager: {secret_name}")
            
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            
            # Parse JSON secret
            try:
                secret_data = json.loads(secret_string)
                self.logger.info(f"Successfully retrieved secret from AWS Secrets Manager")
                return secret_data
            except json.JSONDecodeError:
                # Return as plain string if not JSON
                return {'value': secret_string}
                
        except ClientError as e:
            self.logger.error(f"Failed to retrieve secret from AWS: {e}")
            raise ConfigurationError(f"AWS Secrets Manager error: {e}")
    
    def is_available(self) -> bool:
        """Check if AWS Secrets Manager is available."""
        try:
            self.client.list_secrets(MaxResults=1)
            return True
        except Exception:
            return False


class HashiCorpVaultProvider(SecretProvider):
    """HashiCorp Vault integration."""
    
    def __init__(self, config: SecretManagerConfig):
        self.config = config
        self.logger = setup_logger(self.__class__.__name__)
        
        if not HVAC_AVAILABLE:
            raise ConfigurationError("hvac is required for HashiCorp Vault")
        
        self.client = hvac.Client(
            url=config.vault_url or os.getenv('VAULT_ADDR'),
            token=config.vault_token or os.getenv('VAULT_TOKEN')
        )
    
    def get_secret(self, secret_path: str) -> Dict[str, Any]:
        """Retrieve secret from HashiCorp Vault."""
        try:
            self.logger.debug(f"Retrieving secret from Vault: {secret_path}")
            
            if not self.client.is_authenticated():
                raise ConfigurationError("Vault client is not authenticated")
            
            # Try KV v2 first, then v1
            try:
                response = self.client.secrets.kv.v2.read_secret_version(path=secret_path)
                secret_data = response['data']['data']
            except Exception:
                response = self.client.secrets.kv.v1.read_secret(path=secret_path)
                secret_data = response['data']
            
            self.logger.info(f"Successfully retrieved secret from Vault")
            return secret_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret from Vault: {e}")
            raise ConfigurationError(f"Vault error: {e}")
    
    def is_available(self) -> bool:
        """Check if Vault is available."""
        try:
            return self.client.is_authenticated()
        except Exception:
            return False


class EnvironmentSecretProvider(SecretProvider):
    """Environment variable fallback provider."""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
    
    def get_secret(self, env_prefix: str = "SNOWFLAKE") -> Dict[str, Any]:
        """Retrieve secrets from environment variables."""
        secrets = {}
        
        env_mapping = {
            'account': f'{env_prefix}_ACCOUNT',
            'user': f'{env_prefix}_USER',
            # SECURITY: Password authentication removed
            'private_key_path': f'{env_prefix}_PRIVATE_KEY_PATH',
            'private_key_passphrase': f'{env_prefix}_PRIVATE_KEY_PASSPHRASE',
            'warehouse': f'{env_prefix}_WAREHOUSE',
            'database': f'{env_prefix}_DATABASE',
            'schema': f'{env_prefix}_SCHEMA',
            'role': f'{env_prefix}_ROLE'
        }
        
        for key, env_var in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                secrets[key] = value
        
        self.logger.debug(f"Retrieved {len(secrets)} secrets from environment")
        return secrets
    
    def is_available(self) -> bool:
        """Environment is always available."""
        return True


class SecretManager:
    """Central secret management coordinator."""
    
    def __init__(self, config: Optional[SecretManagerConfig] = None):
        self.config = config
        self.logger = setup_logger(self.__class__.__name__)
        self.provider: Optional[SecretProvider] = None
        
        if config:
            self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the appropriate secret provider."""
        if not self.config:
            self.provider = EnvironmentSecretProvider()
            return
        
        provider_map = {
            'aws': AWSSecretsManagerProvider,
            'vault': HashiCorpVaultProvider,
            'environment': EnvironmentSecretProvider
        }
        
        provider_class = provider_map.get(self.config.provider.lower())
        if not provider_class:
            raise ConfigurationError(f"Unsupported secret provider: {self.config.provider}")
        
        try:
            if self.config.provider.lower() == 'environment':
                self.provider = provider_class()
            else:
                self.provider = provider_class(self.config)
                
            if not self.provider.is_available():
                self.logger.warning(f"Provider {self.config.provider} not available, falling back to environment")
                self.provider = EnvironmentSecretProvider()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize provider {self.config.provider}: {e}")
            self.logger.info("Falling back to environment variables")
            self.provider = EnvironmentSecretProvider()
    
    def get_snowflake_config(self, secret_name: str = "snowflake") -> SnowflakeConfig:
        """
        Get Snowflake configuration from secret manager.
        
        Args:
            secret_name: Name/path of the secret containing Snowflake credentials
            
        Returns:
            SnowflakeConfig with credentials from secret manager
        """
        if not self.provider:
            self.provider = EnvironmentSecretProvider()
        
        try:
            # Get secrets from provider
            if isinstance(self.provider, EnvironmentSecretProvider):
                secrets = self.provider.get_secret()
            else:
                secrets = self.provider.get_secret(secret_name)
            
            # Create config from secrets
            config_params = {}
            
            # Map secret keys to config parameters
            key_mapping = {
                'account': 'account',
                'user': 'user', 
                'username': 'user',  # Alternative key name
                # SECURITY: Password authentication removed
                'private_key_path': 'private_key_path',
                'private_key_passphrase': 'private_key_passphrase',
                'warehouse': 'warehouse',
                'database': 'database',
                'schema': 'schema',
                'role': 'role',
                'authenticator': 'authenticator'
            }
            
            for secret_key, config_key in key_mapping.items():
                if secret_key in secrets:
                    config_params[config_key] = secrets[secret_key]
            
            # Validate required parameters
            if not config_params.get('account') or not config_params.get('user'):
                raise ConfigurationError("Missing required credentials: account and user")
            
            if not config_params.get('private_key_path'):
                raise ConfigurationError("Missing required private_key_path: password authentication is disabled for security")
            
            self.logger.info(f"Successfully retrieved Snowflake configuration from {type(self.provider).__name__}")
            return SnowflakeConfig(**config_params)
            
        except Exception as e:
            self.logger.error(f"Failed to get Snowflake config from secret manager: {e}")
            raise ConfigurationError(f"Secret manager error: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the secret provider."""
        if not self.provider:
            return {"available": False, "error": "No provider configured"}
        
        try:
            available = self.provider.is_available()
            return {
                "available": available,
                "provider": type(self.provider).__name__,
                "config": self.config.provider if self.config else "environment"
            }
        except Exception as e:
            return {
                "available": False,
                "provider": type(self.provider).__name__,
                "error": str(e)
            }


# Convenience functions for common use cases
def from_aws_secrets_manager(secret_name: str, region: str = None) -> SnowflakeConfig:
    """
    Create SnowflakeConfig from AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        region: AWS region (defaults to AWS_DEFAULT_REGION)
    
    Returns:
        SnowflakeConfig with credentials from AWS Secrets Manager
    """
    config = SecretManagerConfig(provider='aws', region=region)
    manager = SecretManager(config)
    return manager.get_snowflake_config(secret_name)


def from_vault(secret_path: str, vault_url: str = None, vault_token: str = None) -> SnowflakeConfig:
    """
    Create SnowflakeConfig from HashiCorp Vault.
    
    Args:
        secret_path: Path to the secret in Vault
        vault_url: Vault server URL (defaults to VAULT_ADDR)
        vault_token: Vault token (defaults to VAULT_TOKEN)
    
    Returns:
        SnowflakeConfig with credentials from Vault
    """
    config = SecretManagerConfig(
        provider='vault',
        vault_url=vault_url,
        vault_token=vault_token
    )
    manager = SecretManager(config)
    return manager.get_snowflake_config(secret_path)


def from_environment() -> SnowflakeConfig:
    """
    Create SnowflakeConfig from environment variables (current default).
    
    Returns:
        SnowflakeConfig with credentials from environment variables
    """
    manager = SecretManager()
    return manager.get_snowflake_config()
