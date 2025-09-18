#!/usr/bin/env python3
"""
Basic usage examples for Snowflake Connector.

This script demonstrates common usage patterns for the Snowflake Connector library.
Make sure to set up your .env file with Snowflake credentials before running.
"""

import pandas as pd
from snowflake_connector import SnowflakeConnector, SnowflakeConfig
from snowflake_connector.exceptions import ConnectionError, QueryError


def example_basic_connection():
    """Example: Basic connection and query execution."""
    print("=== Basic Connection Example ===")
    
    try:
        # Create connector (will use environment variables)
        with SnowflakeConnector() as conn:
            # Test the connection
            test_result = conn.test_connection()
            print(f"Connection successful: {test_result['connected']}")
            print(f"Current user: {test_result.get('current_user')}")
            print(f"Current database: {test_result.get('current_database')}")
            
            # Execute a simple query
            results = conn.execute_query("SELECT CURRENT_TIMESTAMP() as current_time")
            print(f"Current Snowflake time: {results[0]['CURRENT_TIME']}")
            
    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


def example_dataframe_operations():
    """Example: Working with pandas DataFrames."""
    print("\n=== DataFrame Operations Example ===")
    
    try:
        with SnowflakeConnector() as conn:
            # Query to DataFrame
            df = conn.execute_query_to_dataframe("""
                SELECT 
                    'Customer' || UNIFORM(1, 1000, RANDOM()) as customer_name,
                    UNIFORM(100, 5000, RANDOM()) as order_total,
                    DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE()) as order_date
                FROM TABLE(GENERATOR(ROWCOUNT => 10))
            """)
            
            print(f"Generated sample data with {len(df)} rows:")
            print(df.head())
            
            # Process the DataFrame
            df['order_date'] = pd.to_datetime(df['ORDER_DATE'])
            recent_orders = df[df['order_date'] > '2024-01-01']
            
            print(f"\nOrders from 2024: {len(recent_orders)}")
            print(f"Average order total: ${df['ORDER_TOTAL'].mean():.2f}")
            
    except QueryError as e:
        print(f"Query failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


def example_database_exploration():
    """Example: Exploring database structure."""
    print("\n=== Database Exploration Example ===")
    
    try:
        with SnowflakeConnector() as conn:
            # List databases
            databases = conn.get_databases()
            print(f"Available databases: {databases[:5]}")  # Show first 5
            
            # List schemas in current database
            schemas = conn.get_schemas()
            print(f"Available schemas: {schemas[:5]}")  # Show first 5
            
            # List tables in current schema
            tables = conn.get_tables()
            if tables:
                print(f"Available tables: {tables[:5]}")  # Show first 5
                
                # Get info about first table
                if tables:
                    table_info = conn.get_table_info(tables[0])
                    print(f"\nStructure of table '{tables[0]}':")
                    for col in table_info[:3]:  # Show first 3 columns
                        print(f"  {col['name']}: {col['type']}")
            else:
                print("No tables found in current schema")
                
    except Exception as e:
        print(f"Error exploring database: {e}")


def example_parameterized_queries():
    """Example: Using parameterized queries."""
    print("\n=== Parameterized Queries Example ===")
    
    try:
        with SnowflakeConnector() as conn:
            # Single parameterized query
            query = """
                SELECT 
                    %(param1)s as parameter_value,
                    CURRENT_DATE() as query_date,
                    %(param2)s as second_parameter
            """
            
            result = conn.execute_query(query, parameters={
                "param1": "Hello from Python!",
                "param2": 42
            })
            
            print("Parameterized query result:")
            print(result[0])
            
    except Exception as e:
        print(f"Error with parameterized query: {e}")


def example_custom_configuration():
    """Example: Using custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    try:
    # Create custom config (you would use real values)  
    config = SnowflakeConfig(
        account="your_account",
        user="your_user",
        private_key_path="/path/to/private_key.p8",
        private_key_passphrase="your_passphrase",
        warehouse="COMPUTE_WH",
        database="DEMO_DB",
        schema="PUBLIC",
        network_timeout=30
    )
        
        print("Custom configuration created successfully")
        print(f"Account: {config.account}")
        print(f"Warehouse: {config.warehouse}")
        
        # You would use this config with SnowflakeConnector(config)
        # For demo purposes, we'll just show the config structure
        params = config.to_connection_params()
        safe_params = {k: v for k, v in params.items() if k != 'password'}
        print(f"Connection parameters: {safe_params}")
        
    except Exception as e:
        print(f"Error with custom configuration: {e}")


def main():
    """Run all examples."""
    print("🚀 Snowflake Connector Examples")
    print("=" * 50)
    
    # Check if we can import the library
    try:
        from snowflake_connector import SnowflakeConnector
        print("✅ Snowflake Connector imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Snowflake Connector: {e}")
        print("Make sure to install the package: pip install -e .")
        return
    
    # Run examples
    example_basic_connection()
    example_dataframe_operations()
    example_database_exploration()
    example_parameterized_queries()
    example_custom_configuration()
    
    print("\n" + "=" * 50)
    print("🎉 Examples completed!")
    print("\nNext steps:")
    print("1. Set up your .env file with real Snowflake credentials")
    print("2. Modify these examples for your specific use case")
    print("3. Explore the full API documentation in README.md")


if __name__ == "__main__":
    main()
