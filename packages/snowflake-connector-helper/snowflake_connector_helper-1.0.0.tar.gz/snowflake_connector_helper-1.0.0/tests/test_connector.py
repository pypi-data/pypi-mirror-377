"""
Unit tests for SnowflakeConnector class.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from snowflake_connector import (
    SnowflakeConnector, 
    SnowflakeConfig,
    ConnectionError,
    QueryError,
    AuthenticationError,
    ConfigurationError
)


class TestSnowflakeConnector:
    """Test cases for SnowflakeConnector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = SnowflakeConfig(
            account="test_account",
            user="test_user", 
            password="test_password",
            warehouse="TEST_WH",
            database="TEST_DB",
            schema="TEST_SCHEMA"
        )
    
    def test_connector_initialization(self):
        """Test connector initialization."""
        connector = SnowflakeConnector(self.config)
        assert connector.config == self.config
        assert connector.connection is None
        assert connector.logger is not None
    
    def test_connector_initialization_without_config(self):
        """Test connector initialization without config."""
        with patch.object(SnowflakeConfig, 'from_env') as mock_from_env:
            mock_from_env.return_value = self.config
            connector = SnowflakeConnector()
            assert connector.config == self.config
            mock_from_env.assert_called_once()
    
    def test_connector_initialization_invalid_config(self):
        """Test connector initialization with invalid config."""
        with pytest.raises(ConfigurationError):
            invalid_config = SnowflakeConfig(
                account="",
                user="test_user",
                password=""  # This should trigger validation error
            )
            SnowflakeConnector(invalid_config)
    
    @patch('snowflake_connector.connector.snowflake.connector.connect')
    def test_connect_success(self, mock_connect):
        """Test successful connection."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_connect.return_value = mock_connection
        
        connector = SnowflakeConnector(self.config)
        connector.connect()
        
        assert connector.connection == mock_connection
        mock_connect.assert_called_once()
    
    @patch('snowflake_connector.connector.snowflake.connector.connect')
    def test_connect_already_connected(self, mock_connect):
        """Test connect when already connected."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        connector.connect()
        
        # Should not call connect again
        mock_connect.assert_not_called()
    
    @patch('snowflake_connector.connector.snowflake.connector.connect')
    def test_connect_authentication_error(self, mock_connect):
        """Test connection with authentication error."""
        from snowflake.connector.errors import ProgrammingError
        mock_connect.side_effect = ProgrammingError("Authentication failed")
        
        connector = SnowflakeConnector(self.config)
        with pytest.raises(AuthenticationError):
            connector.connect()
    
    @patch('snowflake_connector.connector.snowflake.connector.connect')
    def test_connect_connection_error(self, mock_connect):
        """Test connection with connection error."""
        from snowflake.connector.errors import ProgrammingError
        mock_connect.side_effect = ProgrammingError("Network error")
        
        connector = SnowflakeConnector(self.config)
        with pytest.raises(ConnectionError):
            connector.connect()
    
    def test_disconnect(self):
        """Test disconnection."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        connector.disconnect()
        
        mock_connection.close.assert_called_once()
        assert connector.connection is None
    
    def test_disconnect_no_connection(self):
        """Test disconnect when no connection exists."""
        connector = SnowflakeConnector(self.config)
        # Should not raise error
        connector.disconnect()
    
    def test_is_connected_true(self):
        """Test is_connected when connected."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        assert connector.is_connected() is True
    
    def test_is_connected_false(self):
        """Test is_connected when not connected."""
        connector = SnowflakeConnector(self.config)
        assert connector.is_connected() is False
    
    def test_execute_query_success(self):
        """Test successful query execution."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'test'}]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        result = connector.execute_query("SELECT * FROM test")
        
        assert result == [{'id': 1, 'name': 'test'}]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
        mock_cursor.fetchall.assert_called_once()
    
    def test_execute_query_with_parameters(self):
        """Test query execution with parameters."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        parameters = {'id': 1}
        connector.execute_query("SELECT * FROM test WHERE id = %(id)s", parameters)
        
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test WHERE id = %(id)s", 
            parameters
        )
    
    def test_execute_query_no_fetch(self):
        """Test query execution without fetching results."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        result = connector.execute_query("INSERT INTO test VALUES (1)", fetch=False)
        
        assert result is None
        mock_cursor.fetchall.assert_not_called()
    
    def test_execute_query_invalid_query(self):
        """Test execution of invalid query."""
        connector = SnowflakeConnector(self.config)
        
        with pytest.raises(QueryError):
            connector.execute_query("")
    
    def test_execute_query_to_dataframe(self):
        """Test query execution returning DataFrame."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        df = connector.execute_query_to_dataframe("SELECT * FROM test")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ['id', 'name']
    
    def test_execute_query_to_dataframe_with_chunks(self):
        """Test query execution with chunking."""
        mock_connection = Mock()
        mock_cursor = Mock()
        # Simulate chunked fetching
        mock_cursor.fetchmany.side_effect = [
            [{'id': 1, 'name': 'Alice'}],
            [{'id': 2, 'name': 'Bob'}],
            []  # End of data
        ]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        df = connector.execute_query_to_dataframe("SELECT * FROM test", chunk_size=1)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
    
    def test_execute_many(self):
        """Test executing multiple queries."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        parameters_list = [{'id': 1}, {'id': 2}]
        connector.execute_many("INSERT INTO test VALUES (%(id)s)", parameters_list)
        
        mock_cursor.executemany.assert_called_once_with(
            "INSERT INTO test VALUES (%(id)s)",
            parameters_list
        )
    
    def test_get_table_info(self):
        """Test getting table information."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'name': 'id', 'type': 'NUMBER'},
            {'name': 'name', 'type': 'VARCHAR'}
        ]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        result = connector.get_table_info("test_table")
        
        assert len(result) == 2
        assert result[0]['name'] == 'id'
        mock_cursor.execute.assert_called_once_with("DESCRIBE TABLE 'test_table'")
    
    def test_get_databases(self):
        """Test getting database list."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'name': 'DB1'}, {'name': 'DB2'}
        ]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        result = connector.get_databases()
        
        assert result == ['DB1', 'DB2']
        mock_cursor.execute.assert_called_once_with("SHOW DATABASES")
    
    def test_insert_dataframe(self):
        """Test inserting DataFrame."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        df = pd.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob']
        })
        
        connector.insert_dataframe(df, "test_table")
        
        # Should call executemany for the insert
        mock_cursor.executemany.assert_called_once()
    
    def test_insert_empty_dataframe(self):
        """Test inserting empty DataFrame."""
        connector = SnowflakeConnector(self.config)
        
        df = pd.DataFrame()
        # Should not raise error, just log warning
        connector.insert_dataframe(df, "test_table")
    
    def test_test_connection(self):
        """Test connection testing."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{
            'CURRENT_VERSION()': '1.0.0',
            'CURRENT_USER()': 'test_user',
            'CURRENT_ROLE()': 'test_role',
            'CURRENT_DATABASE()': 'test_db',
            'CURRENT_SCHEMA()': 'test_schema'
        }]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        connector = SnowflakeConnector(self.config)
        connector.connection = mock_connection
        
        result = connector.test_connection()
        
        assert result['connected'] is True
        assert result['current_user'] == 'test_user'
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with patch.object(SnowflakeConnector, 'connect') as mock_connect:
            with patch.object(SnowflakeConnector, 'disconnect') as mock_disconnect:
                
                with SnowflakeConnector(self.config) as connector:
                    assert isinstance(connector, SnowflakeConnector)
                
                mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()


class TestSnowflakeConfig:
    """Test cases for SnowflakeConfig class."""
    
    def test_config_creation_with_password(self):
        """Test creating config with password authentication."""
        config = SnowflakeConfig(
            account="test_account",
            user="test_user",
            password="test_password"
        )
        assert config.account == "test_account"
        assert config.user == "test_user"
        assert config.password == "test_password"
    
    def test_config_creation_with_private_key(self):
        """Test creating config with private key authentication."""
        config = SnowflakeConfig(
            account="test_account",
            user="test_user",
            private_key_path="/path/to/key.p8"
        )
        assert config.private_key_path == "/path/to/key.p8"
    
    def test_config_validation_no_auth(self):
        """Test config validation when no authentication method provided."""
        with pytest.raises(ValueError):
            SnowflakeConfig(
                account="test_account",
                user="test_user"
                # No password or private_key_path
            )
    
    @patch.dict('os.environ', {
        'SNOWFLAKE_ACCOUNT': 'env_account',
        'SNOWFLAKE_USER': 'env_user',
        'SNOWFLAKE_PASSWORD': 'env_password'
    })
    def test_config_from_env(self):
        """Test creating config from environment variables."""
        config = SnowflakeConfig.from_env()
        assert config.account == "env_account"
        assert config.user == "env_user"
        assert config.password == "env_password"
    
    def test_to_connection_params(self):
        """Test converting config to connection parameters."""
        config = SnowflakeConfig(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="TEST_WH"
        )
        
        params = config.to_connection_params()
        
        assert params['account'] == "test_account"
        assert params['user'] == "test_user"
        assert params['password'] == "test_password"
        assert params['warehouse'] == "TEST_WH"
        assert 'private_key_path' not in params
