"""
Tests for REPL functionality.
"""

import sys
import os
import tempfile
from io import StringIO
from unittest.mock import patch
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.repl import format_result, format_table, start_repl
from src.main import DatabaseEngine


def test_format_table():
    """Test table formatting."""
    rows = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25}
    ]
    
    result = format_table(rows)
    
    assert "id" in result
    assert "name" in result
    assert "age" in result
    assert "Alice" in result
    assert "Bob" in result
    assert "(2 row(s))" in result


def test_format_table_empty():
    """Test formatting empty table."""
    result = format_table([])
    assert result == "(0 rows)"


def test_format_result_string():
    """Test formatting string result."""
    result = format_result("Table created")
    assert result == "Table created"


def test_format_result_list():
    """Test formatting list result."""
    result = format_result([{"id": 1, "name": "Alice"}])
    assert "id" in result
    assert "name" in result
    assert "Alice" in result


def test_format_result_int():
    """Test formatting integer result (rows affected)."""
    result = format_result(1)
    assert "(1 row affected)" in result
    
    result = format_result(0)
    assert "(0 rows affected)" in result
    
    result = format_result(5)
    assert "(5 rows affected)" in result


def test_format_result_none():
    """Test formatting None result."""
    result = format_result(None)
    assert result == ""


def test_repl_execution():
    """Test REPL can execute queries."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Test CREATE TABLE
        result = db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        assert result == "Table 'users' created successfully"
        
        # Test INSERT
        result = db.execute("INSERT INTO users VALUES (1, 'Alice')")
        assert result == "(1 row affected)"
        
        # Test SELECT
        result = db.execute("SELECT * FROM users")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"
    
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)
