"""
Connection pooling implementation for Snowflake Connector.

This module provides thread-safe connection pooling with health checking,
automatic cleanup, and configurable pool behavior.
"""

import logging
import threading
import time
import queue
from typing import Optional, Dict, Any, List, ContextManager
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import snowflake.connector
    from snowflake.connector.errors import Error as SnowflakeError
except ImportError:
    raise ImportError(
        "snowflake-connector-python is required. Install it with: "
        "pip install snowflake-connector-python"
    )

from .config import SnowflakeConfig
from .exceptions import ConnectionError, ConfigurationError
from .utils import setup_logger, format_connection_info


@dataclass
class PooledConnection:
    """Wrapper for a pooled Snowflake connection with metadata."""
    
    connection: Any  # snowflake.connector.SnowflakeConnection
    created_at: datetime
    last_used: datetime
    use_count: int = 0
    is_healthy: bool = True
    
    def mark_used(self):
        """Mark connection as recently used."""
        self.last_used = datetime.now()
        self.use_count += 1
    
    def is_expired(self, max_age_seconds: int) -> bool:
        """Check if connection has exceeded maximum age."""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > max_age_seconds
    
    def is_idle_too_long(self, max_idle_seconds: int) -> bool:
        """Check if connection has been idle too long."""
        idle_time = (datetime.now() - self.last_used).total_seconds()
        return idle_time > max_idle_seconds
    
    def check_health(self) -> bool:
        """Check if connection is still healthy."""
        try:
            if self.connection.is_closed():
                self.is_healthy = False
                return False
            
            # Simple health check query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            self.is_healthy = True
            return True
            
        except Exception:
            self.is_healthy = False
            return False
    
    def close(self):
        """Close the underlying connection."""
        try:
            if not self.connection.is_closed():
                self.connection.close()
        except Exception:
            pass  # Connection might already be closed/invalid


class SnowflakeConnectionPool:
    """
    Thread-safe connection pool for Snowflake connections.
    
    Features:
    - Configurable pool size and connection limits
    - Automatic connection health checking
    - Connection expiration and cleanup
    - Thread-safe operations
    - Connection usage statistics
    - Graceful pool shutdown
    """
    
    def __init__(
        self,
        config: SnowflakeConfig,
        min_connections: int = 1,
        max_connections: int = 10,
        max_connection_age: int = 3600,  # 1 hour
        max_idle_time: int = 300,        # 5 minutes
        health_check_interval: int = 60,  # 1 minute
        connection_timeout: int = 30,     # 30 seconds to get connection
        enable_health_checks: bool = True,
        auto_cleanup: bool = True
    ):
        """
        Initialize the connection pool.
        
        Args:
            config: Snowflake configuration
            min_connections: Minimum connections to maintain
            max_connections: Maximum connections allowed
            max_connection_age: Maximum age of connection in seconds
            max_idle_time: Maximum idle time before connection cleanup
            health_check_interval: How often to check connection health
            connection_timeout: Timeout for getting connection from pool
            enable_health_checks: Whether to perform health checks
            auto_cleanup: Whether to automatically clean up old connections
        """
        self.config = config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_connection_age = max_connection_age
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval
        self.connection_timeout = connection_timeout
        self.enable_health_checks = enable_health_checks
        self.auto_cleanup = auto_cleanup
        
        # Thread-safe connection pool
        self._pool: queue.Queue[PooledConnection] = queue.Queue(maxsize=max_connections)
        self._all_connections: List[PooledConnection] = []
        self._pool_lock = threading.RLock()
        self._creation_lock = threading.Lock()
        
        # Pool state
        self._is_closed = False
        self._created_count = 0
        self._total_requests = 0
        self._pool_hits = 0
        
        # Background cleanup thread
        self._cleanup_thread: Optional[threading.Thread] = None
        self._cleanup_stop_event = threading.Event()
        
        # Logger
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
        # Validate configuration
        if min_connections > max_connections:
            raise ConfigurationError("min_connections cannot be greater than max_connections")
        
        if min_connections < 0 or max_connections <= 0:
            raise ConfigurationError("Connection counts must be positive")
        
        # Initialize pool with minimum connections
        self._initialize_pool()
        
        # Start cleanup thread if auto cleanup is enabled
        if auto_cleanup:
            self._start_cleanup_thread()
        
        self.logger.info(f"Connection pool initialized: min={min_connections}, max={max_connections}")
    
    def _initialize_pool(self):
        """Initialize the pool with minimum connections."""
        for _ in range(self.min_connections):
            try:
                conn = self._create_connection()
                if conn:
                    self._pool.put_nowait(conn)
            except Exception as e:
                self.logger.warning(f"Failed to create initial connection: {e}")
    
    def _create_connection(self) -> Optional[PooledConnection]:
        """Create a new pooled connection."""
        try:
            with self._creation_lock:
                if self._created_count >= self.max_connections:
                    return None
                
                connection_params = self.config.to_connection_params()
                self.logger.debug(f"Creating new connection: {format_connection_info(connection_params)}")
                
                snowflake_conn = snowflake.connector.connect(**connection_params)
                
                pooled_conn = PooledConnection(
                    connection=snowflake_conn,
                    created_at=datetime.now(),
                    last_used=datetime.now()
                )
                
                with self._pool_lock:
                    self._all_connections.append(pooled_conn)
                    self._created_count += 1
                
                self.logger.debug(f"Created connection {len(self._all_connections)}/{self.max_connections}")
                return pooled_conn
                
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
            raise ConnectionError(f"Failed to create pooled connection: {e}")
    
    def _start_cleanup_thread(self):
        """Start the background cleanup thread."""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._cleanup_stop_event.clear()
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                name="SnowflakePoolCleanup",
                daemon=True
            )
            self._cleanup_thread.start()
            self.logger.debug("Started cleanup thread")
    
    def _cleanup_worker(self):
        """Background worker for cleaning up expired/unhealthy connections."""
        while not self._cleanup_stop_event.wait(self.health_check_interval):
            if self._is_closed:
                break
            
            try:
                self._cleanup_connections()
            except Exception as e:
                self.logger.error(f"Error in cleanup worker: {e}")
    
    def _cleanup_connections(self):
        """Clean up expired and unhealthy connections."""
        with self._pool_lock:
            connections_to_remove = []
            
            for conn in self._all_connections:
                should_remove = False
                
                # Check if connection is expired
                if conn.is_expired(self.max_connection_age):
                    self.logger.debug(f"Connection expired (age: {(datetime.now() - conn.created_at).total_seconds()}s)")
                    should_remove = True
                
                # Check if connection has been idle too long
                elif conn.is_idle_too_long(self.max_idle_time):
                    self.logger.debug(f"Connection idle too long (idle: {(datetime.now() - conn.last_used).total_seconds()}s)")
                    should_remove = True
                
                # Check health if enabled
                elif self.enable_health_checks and not conn.check_health():
                    self.logger.debug("Connection failed health check")
                    should_remove = True
                
                if should_remove:
                    connections_to_remove.append(conn)
            
            # Remove unhealthy connections but maintain minimum
            for conn in connections_to_remove:
                if len(self._all_connections) > self.min_connections:
                    self._remove_connection(conn)
                elif not conn.is_healthy:
                    # Always remove unhealthy connections even if below minimum
                    self._remove_connection(conn)
            
            # Ensure we have minimum connections
            self._ensure_minimum_connections()
    
    def _remove_connection(self, conn: PooledConnection):
        """Remove a connection from the pool."""
        try:
            # Remove from pool queue (if it's there)
            temp_queue = queue.Queue()
            while not self._pool.empty():
                try:
                    queued_conn = self._pool.get_nowait()
                    if queued_conn != conn:
                        temp_queue.put_nowait(queued_conn)
                except queue.Empty:
                    break
            
            # Put back non-removed connections
            while not temp_queue.empty():
                self._pool.put_nowait(temp_queue.get_nowait())
            
            # Remove from all connections list
            if conn in self._all_connections:
                self._all_connections.remove(conn)
                self._created_count -= 1
            
            # Close the connection
            conn.close()
            
            self.logger.debug(f"Removed connection, pool size: {len(self._all_connections)}")
            
        except Exception as e:
            self.logger.error(f"Error removing connection: {e}")
    
    def _ensure_minimum_connections(self):
        """Ensure pool has minimum number of connections."""
        current_count = len(self._all_connections)
        if current_count < self.min_connections:
            needed = self.min_connections - current_count
            for _ in range(needed):
                try:
                    conn = self._create_connection()
                    if conn:
                        self._pool.put_nowait(conn)
                    else:
                        break  # Can't create more connections
                except Exception as e:
                    self.logger.warning(f"Failed to create connection for minimum pool: {e}")
                    break
    
    @contextmanager
    def get_connection(self) -> ContextManager[Any]:
        """
        Get a connection from the pool.
        
        Returns:
            Context manager that yields a Snowflake connection
            
        Raises:
            ConnectionError: If unable to get a connection
        """
        if self._is_closed:
            raise ConnectionError("Connection pool is closed")
        
        pooled_conn = None
        start_time = time.time()
        
        try:
            with self._pool_lock:
                self._total_requests += 1
            
            # Try to get connection from pool
            try:
                pooled_conn = self._pool.get(timeout=self.connection_timeout)
                with self._pool_lock:
                    self._pool_hits += 1
                
                # Validate connection health
                if not pooled_conn.check_health():
                    self.logger.debug("Got unhealthy connection from pool, creating new one")
                    self._remove_connection(pooled_conn)
                    pooled_conn = self._create_connection()
                    if not pooled_conn:
                        raise ConnectionError("Unable to create new connection")
                
            except queue.Empty:
                # Pool is empty, try to create new connection
                self.logger.debug("Pool empty, creating new connection")
                pooled_conn = self._create_connection()
                if not pooled_conn:
                    raise ConnectionError("Pool exhausted and cannot create new connection")
            
            # Mark connection as used
            pooled_conn.mark_used()
            
            acquisition_time = time.time() - start_time
            self.logger.debug(f"Connection acquired in {acquisition_time:.3f}s")
            
            yield pooled_conn.connection
            
        except Exception as e:
            self.logger.error(f"Error getting connection: {e}")
            if pooled_conn:
                self._remove_connection(pooled_conn)
                pooled_conn = None
            raise
        
        finally:
            # Return connection to pool
            if pooled_conn and not self._is_closed:
                try:
                    # Check if connection is still healthy before returning
                    if pooled_conn.check_health() and not pooled_conn.is_expired(self.max_connection_age):
                        self._pool.put_nowait(pooled_conn)
                    else:
                        self._remove_connection(pooled_conn)
                except Exception as e:
                    self.logger.error(f"Error returning connection to pool: {e}")
                    self._remove_connection(pooled_conn)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self._pool_lock:
            return {
                'pool_size': len(self._all_connections),
                'available_connections': self._pool.qsize(),
                'min_connections': self.min_connections,
                'max_connections': self.max_connections,
                'total_requests': self._total_requests,
                'pool_hits': self._pool_hits,
                'cache_hit_ratio': self._pool_hits / max(self._total_requests, 1),
                'created_connections': self._created_count,
                'is_closed': self._is_closed,
                'health_checks_enabled': self.enable_health_checks,
                'connections_info': [
                    {
                        'created_at': conn.created_at.isoformat(),
                        'last_used': conn.last_used.isoformat(),
                        'use_count': conn.use_count,
                        'is_healthy': conn.is_healthy,
                        'age_seconds': (datetime.now() - conn.created_at).total_seconds(),
                        'idle_seconds': (datetime.now() - conn.last_used).total_seconds()
                    }
                    for conn in self._all_connections
                ]
            }
    
    def close(self):
        """Close the connection pool and all connections."""
        if self._is_closed:
            return
        
        self.logger.info("Closing connection pool...")
        self._is_closed = True
        
        # Stop cleanup thread
        if self._cleanup_thread:
            self._cleanup_stop_event.set()
            self._cleanup_thread.join(timeout=5)
        
        # Close all connections
        with self._pool_lock:
            for conn in self._all_connections:
                conn.close()
            
            self._all_connections.clear()
            self._created_count = 0
            
            # Clear the queue
            while not self._pool.empty():
                try:
                    self._pool.get_nowait()
                except queue.Empty:
                    break
        
        self.logger.info("Connection pool closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure pool is closed."""
        if hasattr(self, '_is_closed') and not self._is_closed:
            self.close()
