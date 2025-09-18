"""
Custom exceptions for the Snowflake Connector.
"""


class SnowflakeConnectorError(Exception):
    """Base exception class for Snowflake Connector."""
    pass


class ConnectionError(SnowflakeConnectorError):
    """Raised when there's an error establishing connection to Snowflake."""
    pass


class QueryError(SnowflakeConnectorError):
    """Raised when there's an error executing a query."""
    pass


class ConfigurationError(SnowflakeConnectorError):
    """Raised when there's an error in configuration."""
    pass


class AuthenticationError(SnowflakeConnectorError):
    """Raised when authentication fails."""
    pass
