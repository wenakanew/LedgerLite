"""
Tests for schema manager.
"""

import pytest
from src.storage.schema import SchemaManager
from src.types import Table, Column, DataType


def test_add_table():
    """Test adding a table to schema manager."""
    manager = SchemaManager()
    columns = [
        Column(name="id", data_type=DataType.INT, is_primary_key=True),
        Column(name="name", data_type=DataType.TEXT)
    ]
    table = Table(name="users", columns=columns)
    
    manager.add_table(table)
    assert manager.table_exists("users")
    assert manager.get_table("users") == table


def test_add_duplicate_table():
    """Test that adding duplicate table raises error."""
    manager = SchemaManager()
    columns = [
        Column(name="id", data_type=DataType.INT, is_primary_key=True)
    ]
    table = Table(name="users", columns=columns)
    
    manager.add_table(table)
    
    with pytest.raises(ValueError, match="already exists"):
        manager.add_table(table)


def test_get_nonexistent_table():
    """Test that getting nonexistent table raises error."""
    manager = SchemaManager()
    
    with pytest.raises(ValueError, match="does not exist"):
        manager.get_table("users")


def test_list_tables():
    """Test listing all tables."""
    manager = SchemaManager()
    assert manager.list_tables() == []
    
    columns = [Column(name="id", data_type=DataType.INT, is_primary_key=True)]
    table1 = Table(name="users", columns=columns)
    table2 = Table(name="products", columns=columns)
    
    manager.add_table(table1)
    manager.add_table(table2)
    
    tables = manager.list_tables()
    assert len(tables) == 2
    assert "users" in tables
    assert "products" in tables

