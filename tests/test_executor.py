"""
Tests for query executor.
"""

import pytest
import tempfile
import os
from src.main import DatabaseEngine
from src.executor.validators import ConstraintViolationError


def test_create_table():
    """Test CREATE TABLE execution."""
    db = DatabaseEngine()
    result = db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    assert "created successfully" in result
    assert db.schema_manager.table_exists("users")


def test_insert():
    """Test INSERT execution."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    result = db.execute("INSERT INTO users VALUES (1, 'Alice')")
    assert "inserted" in result
    
    # Verify data
    rows = db.execute("SELECT * FROM users")
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["name"] == "Alice"


def test_select_all():
    """Test SELECT * execution."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("INSERT INTO users VALUES (2, 'Bob')")
    
    rows = db.execute("SELECT * FROM users")
    assert len(rows) == 2


def test_select_with_where():
    """Test SELECT with WHERE clause."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("INSERT INTO users VALUES (2, 'Bob')")
    
    rows = db.execute("SELECT * FROM users WHERE id = 1")
    assert len(rows) == 1
    assert rows[0]["id"] == 1


def test_update():
    """Test UPDATE execution."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    
    result = db.execute("UPDATE users SET name = 'Bob' WHERE id = 1")
    assert "updated" in result
    
    rows = db.execute("SELECT * FROM users WHERE id = 1")
    assert rows[0]["name"] == "Bob"


def test_delete():
    """Test DELETE execution."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("INSERT INTO users VALUES (2, 'Bob')")
    
    result = db.execute("DELETE FROM users WHERE id = 1")
    assert "deleted" in result
    
    rows = db.execute("SELECT * FROM users")
    assert len(rows) == 1
    assert rows[0]["id"] == 2


def test_primary_key_constraint():
    """Test primary key constraint enforcement."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    
    with pytest.raises(Exception) as exc_info:
        db.execute("INSERT INTO users VALUES (1, 'Bob')")
    assert "Primary key" in str(exc_info.value) or "constraint" in str(exc_info.value).lower()


def test_unique_constraint():
    """Test unique constraint enforcement."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, email TEXT UNIQUE, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'alice@example.com', 'Alice')")
    
    with pytest.raises(Exception) as exc_info:
        db.execute("INSERT INTO users VALUES (2, 'alice@example.com', 'Bob')")
    assert "Unique" in str(exc_info.value) or "constraint" in str(exc_info.value).lower()


def test_join():
    """Test INNER JOIN execution."""
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    db.execute("CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount FLOAT)")
    
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("INSERT INTO orders VALUES (1, 1, 100.50)")
    
    rows = db.execute("""
        SELECT users.name, orders.amount 
        FROM users 
        INNER JOIN orders 
        ON users.id = orders.user_id
    """)
    
    assert len(rows) == 1
    assert "name" in rows[0] or "users.name" in str(rows[0])
    assert "amount" in rows[0] or "orders.amount" in str(rows[0])


def test_ledger_persistence():
    """Test that ledger entries are persisted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "ledger.jsonl")
        db = DatabaseEngine(ledger_file=ledger_file)
        
        db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        db.execute("INSERT INTO users VALUES (1, 'Alice')")
        
        # Create new instance to test persistence
        db2 = DatabaseEngine(ledger_file=ledger_file)
        rows = db2.execute("SELECT * FROM users")
        assert len(rows) == 1
        assert rows[0]["id"] == 1

