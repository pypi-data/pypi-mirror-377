"""
Snowflake Connector Helper - SignifyHealth Internal

Internal Python library for connecting to Snowflake data warehouse with
PKCS#8 encrypted key authentication, connection pooling, and pandas integration.

INTERNAL USE ONLY - Team of Noah A from SignifyHealth

Features:
- PKCS#8 encrypted private key authentication (company standard)
- Connection pooling with health monitoring  
- Native pandas DataFrame support
- Team naming convention support
- Enterprise security features
"""

__version__ = "1.0.0"
__author__ = "Team of Noah A - SignifyHealth"

from .connector import SnowflakeConnector
from .config import SnowflakeConfig
from .pool import SnowflakeConnectionPool
from .secrets import SecretManager, from_aws_secrets_manager, from_vault, from_environment
from .exceptions import SnowflakeConnectorError, ConnectionError, QueryError

__all__ = [
    "SnowflakeConnector",
    "SnowflakeConfig", 
    "SnowflakeConnectionPool",
    "SecretManager",
    "from_aws_secrets_manager",
    "from_vault", 
    "from_environment",
    "SnowflakeConnectorError",
    "ConnectionError",
    "QueryError"
]