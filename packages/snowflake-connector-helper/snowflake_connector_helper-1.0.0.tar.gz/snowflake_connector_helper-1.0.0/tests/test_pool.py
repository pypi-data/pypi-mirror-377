"""
Unit tests for SnowflakeConnectionPool class.
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from snowflake_connector import SnowflakeConfig
from snowflake_connector.pool import SnowflakeConnectionPool, PooledConnection
from snowflake_connector.exceptions import ConnectionError, ConfigurationError


class TestPooledConnection:
    """Test cases for PooledConnection class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_connection.is_closed.return_value = False
        
        self.pooled_conn = PooledConnection(
            connection=self.mock_connection,
            created_at=datetime.now(),
            last_used=datetime.now()
        )
    
    def test_mark_used(self):
        """Test marking connection as used."""
        original_time = self.pooled_conn.last_used
        original_count = self.pooled_conn.use_count
        
        time.sleep(0.01)  # Small delay to ensure time difference
        self.pooled_conn.mark_used()
        
        assert self.pooled_conn.last_used > original_time
        assert self.pooled_conn.use_count == original_count + 1
    
    def test_is_expired(self):
        """Test connection expiration check."""
        # Create connection that's old
        old_conn = PooledConnection(
            connection=self.mock_connection,
            created_at=datetime.now() - timedelta(seconds=3700),  # > 1 hour
            last_used=datetime.now()
        )
        
        assert old_conn.is_expired(3600) is True  # 1 hour max age
        assert self.pooled_conn.is_expired(3600) is False
    
    def test_is_idle_too_long(self):
        """Test idle time check."""
        # Create connection that's been idle
        idle_conn = PooledConnection(
            connection=self.mock_connection,
            created_at=datetime.now(),
            last_used=datetime.now() - timedelta(seconds=400)  # > 5 minutes
        )
        
        assert idle_conn.is_idle_too_long(300) is True  # 5 minute max idle
        assert self.pooled_conn.is_idle_too_long(300) is False
    
    def test_check_health_healthy(self):
        """Test health check for healthy connection."""
        mock_cursor = Mock()
        self.mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        
        assert self.pooled_conn.check_health() is True
        assert self.pooled_conn.is_healthy is True
    
    def test_check_health_unhealthy(self):
        """Test health check for unhealthy connection."""
        self.mock_connection.cursor.side_effect = Exception("Connection failed")
        
        assert self.pooled_conn.check_health() is False
        assert self.pooled_conn.is_healthy is False
    
    def test_close(self):
        """Test closing connection."""
        self.pooled_conn.close()
        self.mock_connection.close.assert_called_once()


class TestSnowflakeConnectionPool:
    """Test cases for SnowflakeConnectionPool class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = SnowflakeConfig(
            account="test_account",
            user="test_user",
            password="test_password"
        )
    
    def test_pool_initialization_invalid_config(self):
        """Test pool initialization with invalid configuration."""
        with pytest.raises(ConfigurationError):
            SnowflakeConnectionPool(
                self.config,
                min_connections=5,
                max_connections=3  # min > max
            )
        
        with pytest.raises(ConfigurationError):
            SnowflakeConnectionPool(
                self.config,
                min_connections=-1  # negative
            )
    
    @patch('snowflake_connector.pool.snowflake.connector.connect')
    def test_pool_initialization_success(self, mock_connect):
        """Test successful pool initialization."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_connect.return_value = mock_connection
        
        pool = SnowflakeConnectionPool(
            self.config,
            min_connections=2,
            max_connections=5,
            auto_cleanup=False  # Disable for testing
        )
        
        try:
            assert pool.min_connections == 2
            assert pool.max_connections == 5
            assert len(pool._all_connections) >= 2  # Should create min connections
            
            # Check that connections were created
            assert mock_connect.call_count >= 2
        finally:
            pool.close()
    
    @patch('snowflake_connector.pool.snowflake.connector.connect')
    def test_get_connection_from_pool(self, mock_connect):
        """Test getting connection from pool."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        mock_connect.return_value = mock_connection
        
        pool = SnowflakeConnectionPool(
            self.config,
            min_connections=1,
            max_connections=3,
            auto_cleanup=False
        )
        
        try:
            with pool.get_connection() as conn:
                assert conn is not None
                assert conn == mock_connection
            
            # Check that connection was returned to pool
            assert pool._pool.qsize() >= 1
        finally:
            pool.close()
    
    @patch('snowflake_connector.pool.snowflake.connector.connect')
    def test_pool_exhaustion(self, mock_connect):
        """Test behavior when pool is exhausted."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        mock_connect.return_value = mock_connection
        
        pool = SnowflakeConnectionPool(
            self.config,
            min_connections=1,
            max_connections=2,
            connection_timeout=0.1,  # Short timeout for testing
            auto_cleanup=False
        )
        
        try:
            # Get all connections and hold them
            connections = []
            for i in range(2):
                conn_context = pool.get_connection()
                conn = conn_context.__enter__()
                connections.append((conn_context, conn))
            
            # Try to get another connection - should timeout
            with pytest.raises(ConnectionError):
                with pool.get_connection() as conn:
                    pass
            
            # Release connections
            for conn_context, conn in connections:
                conn_context.__exit__(None, None, None)
                
        finally:
            pool.close()
    
    @patch('snowflake_connector.pool.snowflake.connector.connect')
    def test_pool_stats(self, mock_connect):
        """Test pool statistics."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        mock_connect.return_value = mock_connection
        
        pool = SnowflakeConnectionPool(
            self.config,
            min_connections=2,
            max_connections=5,
            auto_cleanup=False
        )
        
        try:
            stats = pool.get_stats()
            
            assert 'pool_size' in stats
            assert 'available_connections' in stats
            assert 'min_connections' in stats
            assert 'max_connections' in stats
            assert 'total_requests' in stats
            assert 'pool_hits' in stats
            assert 'cache_hit_ratio' in stats
            assert 'connections_info' in stats
            
            assert stats['min_connections'] == 2
            assert stats['max_connections'] == 5
            assert stats['pool_size'] >= 2
            
        finally:
            pool.close()
    
    @patch('snowflake_connector.pool.snowflake.connector.connect')
    def test_pool_cleanup(self, mock_connect):
        """Test pool cleanup functionality."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        mock_connect.return_value = mock_connection
        
        pool = SnowflakeConnectionPool(
            self.config,
            min_connections=1,
            max_connections=3,
            max_connection_age=1,  # 1 second max age
            max_idle_time=1,       # 1 second max idle
            health_check_interval=0.5,  # Check every 0.5 seconds
            auto_cleanup=True
        )
        
        try:
            # Wait for cleanup to potentially happen
            time.sleep(1.5)
            
            # Pool should still maintain minimum connections
            stats = pool.get_stats()
            assert stats['pool_size'] >= 1
            
        finally:
            pool.close()
    
    @patch('snowflake_connector.pool.snowflake.connector.connect')
    def test_thread_safety(self, mock_connect):
        """Test thread safety of connection pool."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        mock_connect.return_value = mock_connection
        
        pool = SnowflakeConnectionPool(
            self.config,
            min_connections=2,
            max_connections=5,
            auto_cleanup=False
        )
        
        results = []
        errors = []
        
        def worker():
            try:
                with pool.get_connection() as conn:
                    # Simulate some work
                    time.sleep(0.01)
                    results.append(conn)
            except Exception as e:
                errors.append(e)
        
        try:
            # Create multiple threads
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == 10
            
        finally:
            pool.close()
    
    @patch('snowflake_connector.pool.snowflake.connector.connect')
    def test_context_manager(self, mock_connect):
        """Test pool context manager."""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        mock_connect.return_value = mock_connection
        
        with SnowflakeConnectionPool(
            self.config,
            min_connections=1,
            max_connections=3,
            auto_cleanup=False
        ) as pool:
            assert not pool._is_closed
            stats = pool.get_stats()
            assert stats['pool_size'] >= 1
        
        # Pool should be closed after context
        assert pool._is_closed
    
    def test_pool_close(self):
        """Test pool closing."""
        with patch('snowflake_connector.pool.snowflake.connector.connect') as mock_connect:
            mock_connection = Mock()
            mock_connection.is_closed.return_value = False
            mock_connect.return_value = mock_connection
            
            pool = SnowflakeConnectionPool(
                self.config,
                min_connections=1,
                max_connections=3,
                auto_cleanup=False
            )
            
            assert not pool._is_closed
            
            pool.close()
            
            assert pool._is_closed
            assert len(pool._all_connections) == 0
            
            # Calling close again should not raise error
            pool.close()
