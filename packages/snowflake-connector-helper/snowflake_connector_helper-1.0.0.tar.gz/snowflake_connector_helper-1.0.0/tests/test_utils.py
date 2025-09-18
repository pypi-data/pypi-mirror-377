"""
Unit tests for utility functions.
"""

import pytest
from datetime import datetime
from snowflake_connector.utils import (
    setup_logger,
    sanitize_query,
    format_connection_info,
    validate_query,
    parse_snowflake_identifier,
    convert_snowflake_timestamp
)


class TestUtils:
    """Test cases for utility functions."""
    
    def test_setup_logger(self):
        """Test logger setup."""
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"
        assert len(logger.handlers) > 0
    
    def test_sanitize_query(self):
        """Test query sanitization."""
        query = "SELECT * FROM users WHERE password = 'secret123'"
        sanitized = sanitize_query(query)
        assert "secret123" not in sanitized
        assert "'***'" in sanitized
    
    def test_sanitize_query_with_double_quotes(self):
        """Test query sanitization with double quotes."""
        query = 'SELECT * FROM users WHERE token = "abc123def"'
        sanitized = sanitize_query(query)
        assert "abc123def" not in sanitized
        assert '"***"' in sanitized
    
    def test_format_connection_info(self):
        """Test connection info formatting."""
        config = {
            'account': 'test_account',
            'user': 'test_user',
            'password': 'secret',
            'warehouse': 'TEST_WH'
        }
        
        formatted = format_connection_info(config)
        assert 'test_account' in formatted
        assert 'secret' not in formatted
        assert '***' in formatted
    
    def test_validate_query_valid(self):
        """Test query validation with valid query."""
        assert validate_query("SELECT * FROM users") is True
        assert validate_query("INSERT INTO users VALUES (1, 'John')") is True
    
    def test_validate_query_empty(self):
        """Test query validation with empty query."""
        assert validate_query("") is False
        assert validate_query("   ") is False
        assert validate_query(None) is False
    
    def test_validate_query_dangerous(self):
        """Test query validation with dangerous operations."""
        # Should still return True but log warning
        assert validate_query("DROP TABLE users") is True
        assert validate_query("DELETE FROM users") is True
        assert validate_query("TRUNCATE TABLE users") is True
    
    def test_parse_snowflake_identifier_single_part(self):
        """Test parsing single-part identifier."""
        result = parse_snowflake_identifier("table_name")
        assert result == {
            'database': None,
            'schema': None,
            'object': 'table_name'
        }
    
    def test_parse_snowflake_identifier_two_parts(self):
        """Test parsing two-part identifier."""
        result = parse_snowflake_identifier("schema.table_name")
        assert result == {
            'database': None,
            'schema': 'schema',
            'object': 'table_name'
        }
    
    def test_parse_snowflake_identifier_three_parts(self):
        """Test parsing three-part identifier."""
        result = parse_snowflake_identifier("database.schema.table_name")
        assert result == {
            'database': 'database',
            'schema': 'schema',
            'object': 'table_name'
        }
    
    def test_parse_snowflake_identifier_invalid(self):
        """Test parsing invalid identifier."""
        with pytest.raises(ValueError):
            parse_snowflake_identifier("too.many.parts.here")
    
    def test_convert_snowflake_timestamp_with_microseconds(self):
        """Test timestamp conversion with microseconds."""
        timestamp_str = "2023-12-25 15:30:45.123456"
        result = convert_snowflake_timestamp(timestamp_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 25
        assert result.hour == 15
        assert result.minute == 30
        assert result.second == 45
        assert result.microsecond == 123456
    
    def test_convert_snowflake_timestamp_without_microseconds(self):
        """Test timestamp conversion without microseconds."""
        timestamp_str = "2023-12-25 15:30:45"
        result = convert_snowflake_timestamp(timestamp_str)
        
        assert isinstance(result, datetime)
        assert result.microsecond == 0
    
    def test_convert_snowflake_timestamp_iso_format(self):
        """Test timestamp conversion with ISO format."""
        timestamp_str = "2023-12-25T15:30:45.123456"
        result = convert_snowflake_timestamp(timestamp_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2023
    
    def test_convert_snowflake_timestamp_invalid(self):
        """Test timestamp conversion with invalid format."""
        with pytest.raises(ValueError):
            convert_snowflake_timestamp("invalid-timestamp")
