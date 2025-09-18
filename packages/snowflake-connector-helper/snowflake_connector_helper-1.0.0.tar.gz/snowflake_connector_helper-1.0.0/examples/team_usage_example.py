#!/usr/bin/env python3
"""
SignifyHealth Team - Snowflake Connector Usage Example

This example demonstrates the standard usage patterns for the team's
Snowflake connector with PKCS#8 authentication.

INTERNAL USE ONLY - Team of Noah A from SignifyHealth
"""

import pandas as pd
from snowflake_connector import SnowflakeConnector, SnowflakeConfig


def basic_data_extraction():
    """Basic data extraction pattern for team projects."""
    print("🔍 Basic Data Extraction Example")
    
    # Simple connection using environment variables
    with SnowflakeConnector() as conn:
        # Extract customer data
        customers = conn.execute_query_to_dataframe("""
            SELECT 
                customer_id,
                customer_name,
                segment,
                acquisition_date,
                lifetime_value
            FROM customer_analytics 
            WHERE acquisition_date >= '2024-01-01'
            ORDER BY lifetime_value DESC
            LIMIT 1000
        """)
        
        print(f"📊 Retrieved {len(customers)} customer records")
        print(f"📈 Total LTV: ${customers['LIFETIME_VALUE'].sum():,.2f}")
        
        return customers


def analysis_with_pooling():
    """Analysis pattern with connection pooling for better performance."""
    print("\n🏊‍♂️ Analysis with Connection Pooling")
    
    # Configure connection pooling
    config = SnowflakeConfig.from_env()
    config.use_connection_pool = True
    config.pool_max_connections = 10
    
    with SnowflakeConnector(config) as conn:
        # Multiple related queries using pooled connections
        
        # Customer segments
        segments = conn.execute_query_to_dataframe("""
            SELECT segment, COUNT(*) as customer_count, AVG(lifetime_value) as avg_ltv
            FROM customer_analytics 
            GROUP BY segment
            ORDER BY avg_ltv DESC
        """)
        
        # Monthly trends
        trends = conn.execute_query_to_dataframe("""
            SELECT 
                DATE_TRUNC('month', order_date) as month,
                COUNT(*) as order_count,
                SUM(order_amount) as total_revenue
            FROM order_history 
            WHERE order_date >= '2024-01-01'
            GROUP BY month
            ORDER BY month
        """)
        
        # Product performance
        products = conn.execute_query_to_dataframe("""
            SELECT 
                product_category,
                SUM(quantity_sold) as total_quantity,
                SUM(revenue) as total_revenue
            FROM product_sales 
            WHERE sale_date >= '2024-01-01'
            GROUP BY product_category
            ORDER BY total_revenue DESC
        """)
        
        print(f"📊 Analysis Results:")
        print(f"   • {len(segments)} customer segments")
        print(f"   • {len(trends)} months of trend data")
        print(f"   • {len(products)} product categories")
        
        return segments, trends, products


def data_pipeline_example():
    """Example data pipeline for team workflows."""
    print("\n🔄 Data Pipeline Example")
    
    config = SnowflakeConfig.from_env()
    config.use_connection_pool = True
    
    with SnowflakeConnector(config) as conn:
        # Step 1: Create staging table
        conn.execute_query("""
            CREATE OR REPLACE TABLE temp_customer_analysis AS
            SELECT 
                customer_id,
                segment,
                lifetime_value,
                acquisition_date,
                DATEDIFF('day', acquisition_date, CURRENT_DATE()) as days_since_acquisition
            FROM customer_analytics
            WHERE acquisition_date >= '2024-01-01'
        """)
        print("✅ Created staging table")
        
        # Step 2: Extract for analysis
        analysis_data = conn.execute_query_to_dataframe("""
            SELECT * FROM temp_customer_analysis
            ORDER BY lifetime_value DESC
        """)
        print(f"📊 Extracted {len(analysis_data)} records for analysis")
        
        # Step 3: Perform analysis (example)
        segment_summary = analysis_data.groupby('SEGMENT').agg({
            'LIFETIME_VALUE': ['mean', 'sum', 'count'],
            'DAYS_SINCE_ACQUISITION': 'mean'
        }).round(2)
        
        print("\n📈 Segment Analysis:")
        print(segment_summary)
        
        # Step 4: Clean up
        conn.execute_query("DROP TABLE IF EXISTS temp_customer_analysis")
        print("🧹 Cleaned up staging table")
        
        return segment_summary


def team_configuration_example():
    """Example of team-specific configuration patterns."""
    print("\n⚙️ Team Configuration Patterns")
    
    # Method 1: Environment variables (recommended)
    print("📋 Using environment variables (.env file):")
    connector1 = SnowflakeConnector()
    
    # Method 2: Direct configuration
    print("📋 Using direct configuration:")
    config = SnowflakeConfig(
        account="SIGNIFYHEALTH-DW_PROD_TEST",
        user="your_username",
        private_key_path="/path/to/your/private_key.cert",
        private_key_passphrase="your_passphrase",
        warehouse="COMPUTE_XSMALL",
        database="AI_TEST",
        schema="member_refusal_analysis",
        role="your_role",
        use_connection_pool=True
    )
    connector2 = SnowflakeConnector(config)
    
    # Test both configurations
    with connector1 as conn:
        result1 = conn.test_connection()
        print(f"✅ Environment config: {result1['connected']}")
    
    print("💡 Tip: Use .env files for consistent team configuration")


def main():
    """Run team usage examples."""
    print("🏢 SIGNIFYHEALTH TEAM - SNOWFLAKE CONNECTOR EXAMPLES")
    print("=" * 60)
    print("Internal package for Team of Noah A from SignifyHealth")
    print("PKCS#8 encrypted key authentication required")
    
    try:
        # Run examples
        customers = basic_data_extraction()
        segments, trends, products = analysis_with_pooling()
        summary = data_pipeline_example()
        team_configuration_example()
        
        print(f"\n🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print(f"📊 Ready for team data analysis workflows")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print(f"💡 Check your .env configuration and PKCS#8 key setup")


if __name__ == "__main__":
    main()
