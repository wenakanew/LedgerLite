"""
Tests for core data types.
"""

import pytest
from src.types import DataType, OperationType, Column, Table, LedgerEntry


def test_column_creation():
    """Test creating a column."""
    col = Column(name="id", data_type=DataType.INT, is_primary_key=True)
    assert col.name == "id"
    assert col.data_type == DataType.INT
    assert col.is_primary_key is True
    assert col.is_unique is False


def test_column_empty_name():
    """Test that column name cannot be empty."""
    with pytest.raises(ValueError, match="Column name cannot be empty"):
        Column(name="", data_type=DataType.TEXT)


def test_table_creation():
    """Test creating a table."""
    columns = [
        Column(name="id", data_type=DataType.INT, is_primary_key=True),
        Column(name="name", data_type=DataType.TEXT)
    ]
    table = Table(name="users", columns=columns)
    assert table.name == "users"
    assert len(table.columns) == 2
    assert table.get_primary_key_column().name == "id"


def test_table_no_primary_key():
    """Test that table must have a primary key."""
    columns = [Column(name="id", data_type=DataType.INT)]
    with pytest.raises(ValueError, match="Table must have a primary key"):
        Table(name="users", columns=columns)


def test_table_multiple_primary_keys():
    """Test that table cannot have multiple primary keys."""
    columns = [
        Column(name="id1", data_type=DataType.INT, is_primary_key=True),
        Column(name="id2", data_type=DataType.INT, is_primary_key=True)
    ]
    with pytest.raises(ValueError, match="at most one primary key"):
        Table(name="users", columns=columns)


def test_table_duplicate_columns():
    """Test that table cannot have duplicate column names."""
    columns = [
        Column(name="id", data_type=DataType.INT, is_primary_key=True),
        Column(name="id", data_type=DataType.TEXT)
    ]
    with pytest.raises(ValueError, match="Duplicate column names"):
        Table(name="users", columns=columns)


def test_ledger_entry_serialization():
    """Test ledger entry to/from dictionary conversion."""
    entry = LedgerEntry(
        transaction_id=1,
        table_name="users",
        operation=OperationType.INSERT,
        timestamp="2026-01-15T10:30:00Z",
        old_value=None,
        new_value={"id": 1, "name": "Alice"}
    )
    
    entry_dict = entry.to_dict()
    assert entry_dict["transaction_id"] == 1
    assert entry_dict["operation"] == "INSERT"
    
    restored = LedgerEntry.from_dict(entry_dict)
    assert restored.transaction_id == entry.transaction_id
    assert restored.operation == entry.operation
