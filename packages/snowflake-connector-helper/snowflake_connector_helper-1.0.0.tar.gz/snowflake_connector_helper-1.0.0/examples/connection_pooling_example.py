#!/usr/bin/env python3
"""
Connection pooling examples for Snowflake Connector.

This script demonstrates how to use connection pooling for improved
performance and resource management in production applications.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from snowflake_connector import SnowflakeConfig, SnowflakeConnector, SnowflakeConnectionPool


def example_basic_pooling():
    """Example: Basic connection pooling setup."""
    print("=== Basic Connection Pooling Example ===")
    
    # Configure with connection pooling enabled
    config = SnowflakeConfig(
        account="your_account",
        user="your_username", 
        password="your_password",
        warehouse="COMPUTE_WH",
        database="DEMO_DB",
        schema="PUBLIC",
        
        # Enable connection pooling
        use_connection_pool=True,
        pool_min_connections=2,
        pool_max_connections=10,
        pool_max_connection_age=3600,  # 1 hour
        pool_max_idle_time=300         # 5 minutes
    )
    
    print(f"Pool configuration:")
    print(f"  Min connections: {config.pool_min_connections}")
    print(f"  Max connections: {config.pool_max_connections}")
    print(f"  Connection pooling: {config.use_connection_pool}")
    
    try:
        with SnowflakeConnector(config) as conn:
            # Test connection
            test_result = conn.test_connection()
            print(f"Connection successful: {test_result['connected']}")
            
            # Execute queries - pooling is transparent
            for i in range(5):
                df = conn.execute_query_to_dataframe(f"""
                    SELECT 
                        {i} as query_number,
                        CURRENT_TIMESTAMP() as execution_time,
                        CONNECTION_ID() as connection_id
                """)
                print(f"Query {i}: Connection ID {df['CONNECTION_ID'].iloc[0]}")
            
            # Check pool statistics
            stats = conn.get_pool_stats()
            if stats:
                print(f"\nPool Statistics:")
                print(f"  Pool size: {stats['pool_size']}")
                print(f"  Available connections: {stats['available_connections']}")
                print(f"  Total requests: {stats['total_requests']}")
                print(f"  Cache hit ratio: {stats['cache_hit_ratio']:.2%}")
                
    except Exception as e:
        print(f"Error: {e}")


def example_concurrent_usage():
    """Example: Concurrent usage with connection pooling."""
    print("\n=== Concurrent Usage Example ===")
    
    config = SnowflakeConfig(
        account="your_account",
        user="your_username",
        password="your_password",
        use_connection_pool=True,
        pool_min_connections=3,
        pool_max_connections=15,
        pool_connection_timeout=30
    )
    
    def worker(worker_id, connector):
        """Worker function for concurrent execution."""
        results = []
        try:
            for i in range(3):
                df = connector.execute_query_to_dataframe(f"""
                    SELECT 
                        {worker_id} as worker_id,
                        {i} as iteration,
                        CONNECTION_ID() as connection_id,
                        CURRENT_TIMESTAMP() as timestamp
                """)
                results.append({
                    'worker_id': worker_id,
                    'iteration': i,
                    'connection_id': df['CONNECTION_ID'].iloc[0],
                    'timestamp': df['TIMESTAMP'].iloc[0]
                })
                time.sleep(0.1)  # Simulate work
                
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
            
        return results
    
    try:
        with SnowflakeConnector(config) as conn:
            print(f"Starting {5} concurrent workers...")
            
            # Use ThreadPoolExecutor for concurrent execution
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit workers
                futures = [
                    executor.submit(worker, worker_id, conn) 
                    for worker_id in range(5)
                ]
                
                # Collect results
                all_results = []
                for future in as_completed(futures):
                    results = future.result()
                    all_results.extend(results)
            
            print(f"Completed {len(all_results)} queries across {5} workers")
            
            # Analyze connection usage
            connection_ids = set(result['connection_id'] for result in all_results)
            print(f"Used {len(connection_ids)} unique connections")
            
            # Final pool statistics
            stats = conn.get_pool_stats()
            if stats:
                print(f"\nFinal Pool Statistics:")
                print(f"  Total requests: {stats['total_requests']}")
                print(f"  Pool hits: {stats['pool_hits']}")
                print(f"  Cache hit ratio: {stats['cache_hit_ratio']:.2%}")
                
    except Exception as e:
        print(f"Error: {e}")


def example_direct_pool_usage():
    """Example: Using connection pool directly."""
    print("\n=== Direct Pool Usage Example ===")
    
    config = SnowflakeConfig(
        account="your_account",
        user="your_username",
        password="your_password"
    )
    
    try:
        # Create pool directly
        with SnowflakeConnectionPool(
            config=config,
            min_connections=2,
            max_connections=8,
            max_connection_age=1800,  # 30 minutes
            enable_health_checks=True,
            auto_cleanup=True
        ) as pool:
            
            print("Pool created successfully")
            
            # Get initial statistics
            stats = pool.get_stats()
            print(f"Initial pool size: {stats['pool_size']}")
            
            # Use pool connections
            for i in range(3):
                with pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"""
                        SELECT 
                            {i} as query_number,
                            CONNECTION_ID() as connection_id,
                            CURRENT_TIMESTAMP() as timestamp
                    """)
                    result = cursor.fetchone()
                    print(f"Query {i}: Connection {result[1]}")
                    cursor.close()
            
            # Final statistics
            final_stats = pool.get_stats()
            print(f"\nFinal Statistics:")
            print(f"  Pool size: {final_stats['pool_size']}")
            print(f"  Total requests: {final_stats['total_requests']}")
            print(f"  Reused connections: {final_stats['pool_hits']}")
            
    except Exception as e:
        print(f"Error: {e}")


def example_pool_monitoring():
    """Example: Pool monitoring and health checks."""
    print("\n=== Pool Monitoring Example ===")
    
    config = SnowflakeConfig(
        account="your_account",
        user="your_username",
        password="your_password",
        use_connection_pool=True,
        pool_min_connections=2,
        pool_max_connections=6,
        pool_health_check_interval=5,  # Check every 5 seconds
        pool_enable_health_checks=True
    )
    
    try:
        connector = SnowflakeConnector(config)
        
        print("Monitoring pool for 15 seconds...")
        
        start_time = time.time()
        while time.time() - start_time < 15:
            # Execute some queries
            df = connector.execute_query_to_dataframe("""
                SELECT 
                    CONNECTION_ID() as connection_id,
                    CURRENT_TIMESTAMP() as timestamp
            """)
            
            # Get and display stats
            stats = connector.get_pool_stats()
            if stats:
                print(f"Time: {time.time() - start_time:.1f}s | "
                      f"Pool: {stats['pool_size']} | "
                      f"Available: {stats['available_connections']} | "
                      f"Requests: {stats['total_requests']} | "
                      f"Hit ratio: {stats['cache_hit_ratio']:.1%}")
            
            time.sleep(2)
        
        # Show detailed connection info
        final_stats = connector.get_pool_stats()
        if final_stats and 'connections_info' in final_stats:
            print(f"\nConnection Details:")
            for i, conn_info in enumerate(final_stats['connections_info']):
                print(f"  Connection {i+1}:")
                print(f"    Age: {conn_info['age_seconds']:.1f}s")
                print(f"    Idle: {conn_info['idle_seconds']:.1f}s")
                print(f"    Uses: {conn_info['use_count']}")
                print(f"    Healthy: {conn_info['is_healthy']}")
        
        connector.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all connection pooling examples."""
    print("🚀 Snowflake Connection Pooling Examples")
    print("=" * 60)
    
    print("\n⚠️  Note: These examples require valid Snowflake credentials.")
    print("   Update the configuration with your actual connection details.")
    print("   Set up your .env file or modify the config objects below.\n")
    
    # Run examples
    example_basic_pooling()
    example_concurrent_usage()
    example_direct_pool_usage()
    example_pool_monitoring()
    
    print("\n" + "=" * 60)
    print("🎉 Connection pooling examples completed!")
    print("\nKey Benefits Demonstrated:")
    print("• Connection reuse reduces overhead")
    print("• Thread-safe concurrent access")
    print("• Automatic health monitoring")
    print("• Resource management and cleanup")
    print("• Performance monitoring and metrics")


if __name__ == "__main__":
    main()
