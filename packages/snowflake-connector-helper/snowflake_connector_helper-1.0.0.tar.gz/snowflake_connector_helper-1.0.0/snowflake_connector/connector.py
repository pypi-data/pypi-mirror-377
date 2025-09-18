"""
Main Snowflake Connector class for connecting to and interacting with Snowflake.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from contextlib import contextmanager
import pandas as pd

try:
    import snowflake.connector
    from snowflake.connector import DictCursor
    from snowflake.connector.errors import Error as SnowflakeError
except ImportError:
    raise ImportError(
        "snowflake-connector-python is required. Install it with: "
        "pip install snowflake-connector-python"
    )

from .config import SnowflakeConfig
from .exceptions import (
    SnowflakeConnectorError, 
    ConnectionError, 
    QueryError, 
    AuthenticationError,
    ConfigurationError
)
from .utils import setup_logger, sanitize_query, format_connection_info, validate_query
from .pool import SnowflakeConnectionPool


class SnowflakeConnector:
    """
    A comprehensive Snowflake connector for Python applications.
    
    This class provides methods to connect to Snowflake, execute queries,
    and retrieve data in various formats including pandas DataFrames.
    """
    
    def __init__(self, config: Optional[SnowflakeConfig] = None):
        """
        Initialize the Snowflake connector.
        
        Args:
            config: SnowflakeConfig instance. If None, will attempt to load from environment.
        """
        self.config = config or SnowflakeConfig.from_env()
        self.connection = None
        self.connection_pool: Optional[SnowflakeConnectionPool] = None
        self.logger = setup_logger(self.__class__.__name__)
        
        # Validate configuration
        try:
            self.config.to_connection_params()
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration: {str(e)}")
        
        # Initialize connection pool if enabled
        if self.config.use_connection_pool:
            self._initialize_connection_pool()
    
    def connect(self) -> None:
        """
        Establish connection to Snowflake.
        
        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
        """
        try:
            if self.connection and not self.connection.is_closed():
                self.logger.info("Already connected to Snowflake")
                return
            
            connection_params = self.config.to_connection_params()
            self.logger.info(f"Connecting to Snowflake: {format_connection_info(connection_params)}")
            
            self.connection = snowflake.connector.connect(**connection_params)
            
            self.logger.info("Successfully connected to Snowflake")
            
        except snowflake.connector.errors.ProgrammingError as e:
            if "Authentication" in str(e) or "login" in str(e).lower():
                raise AuthenticationError(f"Authentication failed: {str(e)}")
            else:
                raise ConnectionError(f"Failed to connect to Snowflake: {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error connecting to Snowflake: {str(e)}")
    
    def _initialize_connection_pool(self):
        """Initialize the connection pool."""
        try:
            self.connection_pool = SnowflakeConnectionPool(
                config=self.config,
                min_connections=self.config.pool_min_connections,
                max_connections=self.config.pool_max_connections,
                max_connection_age=self.config.pool_max_connection_age,
                max_idle_time=self.config.pool_max_idle_time,
                health_check_interval=self.config.pool_health_check_interval,
                connection_timeout=self.config.pool_connection_timeout,
                enable_health_checks=self.config.pool_enable_health_checks,
                auto_cleanup=self.config.pool_auto_cleanup
            )
            self.logger.info("Connection pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise ConfigurationError(f"Failed to initialize connection pool: {e}")
    
    def disconnect(self) -> None:
        """Close the Snowflake connection or connection pool."""
        if self.connection_pool:
            try:
                self.connection_pool.close()
                self.connection_pool = None
                self.logger.info("Connection pool closed")
            except Exception as e:
                self.logger.error(f"Error closing connection pool: {str(e)}")
        
        if self.connection and not self.connection.is_closed():
            try:
                self.connection.close()
                self.logger.info("Disconnected from Snowflake")
            except Exception as e:
                self.logger.error(f"Error closing connection: {str(e)}")
        
        self.connection = None
    
    def is_connected(self) -> bool:
        """Check if connected to Snowflake."""
        if self.connection_pool:
            return not self.connection_pool._is_closed
        return self.connection is not None and not self.connection.is_closed()
    
    @contextmanager
    def get_cursor(self, cursor_class=DictCursor):
        """
        Context manager for getting a cursor.
        
        Args:
            cursor_class: Type of cursor to create (default: DictCursor)
        
        Yields:
            Snowflake cursor
        """
        if self.connection_pool:
            # Use connection pool
            with self.connection_pool.get_connection() as connection:
                cursor = connection.cursor(cursor_class)
                try:
                    yield cursor
                finally:
                    cursor.close()
        else:
            # Use direct connection
            if not self.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(cursor_class)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        fetch: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query to execute
            parameters: Query parameters for parameterized queries
            fetch: Whether to fetch results (default: True)
        
        Returns:
            Query results as list of dictionaries if fetch=True, None otherwise
        
        Raises:
            QueryError: If query execution fails
        """
        if not validate_query(query):
            raise QueryError("Invalid query provided")
        
        try:
            with self.get_cursor() as cursor:
                self.logger.info(f"Executing query: {sanitize_query(query)}")
                
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                
                if fetch:
                    results = cursor.fetchall()
                    self.logger.info(f"Query returned {len(results)} rows")
                    return results
                else:
                    self.logger.info("Query executed successfully (no fetch)")
                    return None
                    
        except SnowflakeError as e:
            raise QueryError(f"Snowflake query error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error executing query: {str(e)}")
    
    def execute_query_to_dataframe(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Execute a query and return results as pandas DataFrame.
        
        Args:
            query: SQL query to execute
            parameters: Query parameters for parameterized queries
            chunk_size: If specified, fetch results in chunks
        
        Returns:
            pandas DataFrame with query results
        
        Raises:
            QueryError: If query execution fails
        """
        try:
            with self.get_cursor() as cursor:
                self.logger.info(f"Executing query to DataFrame: {sanitize_query(query)}")
                
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                
                if chunk_size:
                    # Fetch in chunks for large datasets
                    dataframes = []
                    while True:
                        chunk = cursor.fetchmany(chunk_size)
                        if not chunk:
                            break
                        df_chunk = pd.DataFrame(chunk)
                        dataframes.append(df_chunk)
                    
                    if dataframes:
                        result_df = pd.concat(dataframes, ignore_index=True)
                    else:
                        result_df = pd.DataFrame()
                else:
                    # Fetch all at once
                    results = cursor.fetchall()
                    result_df = pd.DataFrame(results)
                
                self.logger.info(f"Query returned DataFrame with shape: {result_df.shape}")
                return result_df
                
        except SnowflakeError as e:
            raise QueryError(f"Snowflake query error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error executing query: {str(e)}")
    
    def execute_many(
        self, 
        query: str, 
        parameters_list: List[Dict[str, Any]]
    ) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query to execute
            parameters_list: List of parameter dictionaries
        
        Raises:
            QueryError: If query execution fails
        """
        if not validate_query(query):
            raise QueryError("Invalid query provided")
        
        try:
            with self.get_cursor() as cursor:
                self.logger.info(f"Executing query {len(parameters_list)} times: {sanitize_query(query)}")
                cursor.executemany(query, parameters_list)
                self.logger.info(f"Successfully executed {len(parameters_list)} queries")
                
        except SnowflakeError as e:
            raise QueryError(f"Snowflake query error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error executing queries: {str(e)}")
    
    def get_table_info(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get information about a table's columns.
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
        
        Returns:
            List of column information dictionaries
        """
        schema_part = f"'{schema}'." if schema else ""
        query = f"DESCRIBE TABLE {schema_part}'{table_name}'"
        
        return self.execute_query(query)
    
    def get_databases(self) -> List[str]:
        """Get list of available databases."""
        results = self.execute_query("SHOW DATABASES")
        return [row['name'] for row in results]
    
    def get_schemas(self, database: Optional[str] = None) -> List[str]:
        """Get list of available schemas."""
        query = "SHOW SCHEMAS"
        if database:
            query += f" IN DATABASE {database}"
        
        results = self.execute_query(query)
        return [row['name'] for row in results]
    
    def get_tables(self, schema: Optional[str] = None, database: Optional[str] = None) -> List[str]:
        """Get list of available tables."""
        query = "SHOW TABLES"
        
        if database and schema:
            query += f" IN SCHEMA {database}.{schema}"
        elif schema:
            query += f" IN SCHEMA {schema}"
        
        results = self.execute_query(query)
        return [row['name'] for row in results]
    
    def insert_dataframe(
        self, 
        dataframe: pd.DataFrame, 
        table_name: str,
        schema: Optional[str] = None,
        if_exists: str = 'append',
        chunk_size: int = 1000
    ) -> None:
        """
        Insert pandas DataFrame into Snowflake table.
        
        Args:
            dataframe: pandas DataFrame to insert
            table_name: Target table name
            schema: Schema name (optional)
            if_exists: What to do if table exists ('append', 'replace', 'fail')
            chunk_size: Number of rows to insert at once
        
        Raises:
            QueryError: If insertion fails
        """
        if dataframe.empty:
            self.logger.warning("DataFrame is empty, nothing to insert")
            return
        
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        
        try:
            # Convert DataFrame to list of dictionaries
            records = dataframe.to_dict('records')
            
            # Create parameterized insert query
            columns = list(dataframe.columns)
            placeholders = ', '.join([f'%({col})s' for col in columns])
            insert_query = f"INSERT INTO {full_table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert in chunks
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                self.execute_many(insert_query, chunk)
            
            self.logger.info(f"Successfully inserted {len(records)} rows into {full_table_name}")
            
        except Exception as e:
            raise QueryError(f"Error inserting DataFrame: {str(e)}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection and return connection information.
        
        Returns:
            Dictionary with connection test results
        """
        try:
            self.connect()
            
            # Get basic connection info
            result = self.execute_query("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            
            info = {
                'connected': True,
                'snowflake_version': result[0].get('CURRENT_VERSION()'),
                'current_user': result[0].get('CURRENT_USER()'),
                'current_role': result[0].get('CURRENT_ROLE()'),
                'current_database': result[0].get('CURRENT_DATABASE()'),
                'current_schema': result[0].get('CURRENT_SCHEMA()')
            }
            
            self.logger.info("Connection test successful")
            return info
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def get_pool_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get connection pool statistics.
        
        Returns:
            Dictionary with pool statistics if using connection pool, None otherwise
        """
        if self.connection_pool:
            return self.connection_pool.get_stats()
        return None
    
    def reset_pool(self) -> None:
        """
        Reset the connection pool by closing and reinitializing it.
        
        This can be useful for recovering from network issues or configuration changes.
        """
        if self.connection_pool:
            self.logger.info("Resetting connection pool...")
            self.connection_pool.close()
            self._initialize_connection_pool()
            self.logger.info("Connection pool reset successfully")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Destructor to ensure connection is closed."""
        if hasattr(self, 'connection'):
            self.disconnect()
