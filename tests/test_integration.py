"""
Integration tests for end-to-end scenarios.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import DatabaseEngine
from src.executor.validators import ConstraintViolationError


def test_full_crud_workflow():
    """Test complete CRUD workflow."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # CREATE TABLE
        result = db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT, email TEXT UNIQUE)")
        assert "created successfully" in result
        
        # INSERT
        result = db.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
        assert "inserted" in result.lower() or "row" in result.lower()
        
        result = db.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
        assert "inserted" in result.lower() or "row" in result.lower()
        
        # SELECT all
        result = db.execute("SELECT * FROM users")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"
        assert result[1]["id"] == 2
        assert result[1]["name"] == "Bob"
        
        # SELECT with WHERE
        result = db.execute("SELECT * FROM users WHERE id = 1")
        assert len(result) == 1
        assert result[0]["name"] == "Alice"
        
        # UPDATE
        result = db.execute("UPDATE users SET name = 'Alice Smith' WHERE id = 1")
        assert "updated" in result.lower() or "row" in result.lower()
        
        result = db.execute("SELECT * FROM users WHERE id = 1")
        assert result[0]["name"] == "Alice Smith"
        
        # DELETE
        result = db.execute("DELETE FROM users WHERE id = 2")
        assert "deleted" in result.lower() or "row" in result.lower()
        
        result = db.execute("SELECT * FROM users")
        assert len(result) == 1
        assert result[0]["id"] == 1
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_constraint_enforcement():
    """Test that constraints are properly enforced."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create table with constraints
        db.execute("CREATE TABLE users (id INT PRIMARY KEY, email TEXT UNIQUE)")
        
        # Insert valid data
        db.execute("INSERT INTO users VALUES (1, 'alice@example.com')")
        
        # Try duplicate primary key
        try:
            db.execute("INSERT INTO users VALUES (1, 'bob@example.com')")
            assert False, "Should have raised ConstraintViolationError"
        except (ValueError, ConstraintViolationError) as e:
            assert "primary key" in str(e).lower() or "constraint" in str(e).lower()
        
        # Try duplicate unique value
        try:
            db.execute("INSERT INTO users VALUES (2, 'alice@example.com')")
            assert False, "Should have raised ConstraintViolationError"
        except (ValueError, ConstraintViolationError) as e:
            assert "unique" in str(e).lower() or "constraint" in str(e).lower()
        
        # Valid insert
        db.execute("INSERT INTO users VALUES (2, 'bob@example.com')")
        result = db.execute("SELECT * FROM users")
        assert len(result) == 2
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_join_operations():
    """Test JOIN operations."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create tables
        db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        db.execute("CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount FLOAT)")
        
        # Insert data
        db.execute("INSERT INTO users VALUES (1, 'Alice')")
        db.execute("INSERT INTO users VALUES (2, 'Bob')")
        db.execute("INSERT INTO orders VALUES (1, 1, 100.50)")
        db.execute("INSERT INTO orders VALUES (2, 1, 50.25)")
        db.execute("INSERT INTO orders VALUES (3, 2, 75.00)")
        
        # Join
        result = db.execute("""
            SELECT users.name, orders.amount 
            FROM users 
            INNER JOIN orders 
            ON users.id = orders.user_id
        """)
        
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Verify join results
        # Columns are in table.column format from SELECT
        names = [row.get("users.name") or row.get("name") for row in result]
        assert "Alice" in names
        assert "Bob" in names
        assert len(result) == 3  # Should have 3 orders matched to users
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_ledger_persistence():
    """Test that data persists across database sessions."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        from src.types import OperationType
        
        # First session
        db1 = DatabaseEngine(ledger_file=ledger_file)
        db1.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        db1.execute("INSERT INTO users VALUES (1, 'Alice')")
        db1.execute("INSERT INTO users VALUES (2, 'Bob')")
        
        # Second session - schemas don't persist (limitation), but data does
        db2 = DatabaseEngine(ledger_file=ledger_file)
        
        # Recreate schema (since CREATE TABLE doesn't persist to ledger)
        db2.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        
        # Rebuild indexes from ledger data
        table = db2.schema_manager.get_table("users")
        rows = db2.ledger_store.reconstruct_state_with_primary_key(
            "users",
            table.get_primary_key_column().name
        )
        db2.index_manager.rebuild_indexes_for_table(table, rows)
        
        # Verify data is still there by querying
        result = db2.execute("SELECT * FROM users")
        assert len(result) == 2
        
        # Add more data in second session
        db2.execute("INSERT INTO users VALUES (3, 'Charlie')")
        
        # Verify in third session
        db3 = DatabaseEngine(ledger_file=ledger_file)
        db3.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        
        # Rebuild indexes
        table3 = db3.schema_manager.get_table("users")
        rows3 = db3.ledger_store.reconstruct_state_with_primary_key(
            "users",
            table3.get_primary_key_column().name
        )
        db3.index_manager.rebuild_indexes_for_table(table3, rows3)
        
        result = db3.execute("SELECT * FROM users")
        assert len(result) == 3
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_complex_queries():
    """Test complex query scenarios."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create tables
        db.execute("CREATE TABLE products (id INT PRIMARY KEY, name TEXT, price FLOAT)")
        db.execute("CREATE TABLE purchases (id INT PRIMARY KEY, product_id INT, quantity INT)")
        
        # Insert data
        db.execute("INSERT INTO products VALUES (1, 'Widget', 10.50)")
        db.execute("INSERT INTO products VALUES (2, 'Gadget', 25.00)")
        db.execute("INSERT INTO purchases VALUES (1, 1, 5)")
        db.execute("INSERT INTO purchases VALUES (2, 1, 3)")
        db.execute("INSERT INTO purchases VALUES (3, 2, 2)")
        
        # Complex join with WHERE
        result = db.execute("""
            SELECT products.name, purchases.quantity 
            FROM products 
            INNER JOIN purchases 
            ON products.id = purchases.product_id 
            WHERE products.price > 15
        """)
        
        assert len(result) == 1
        # Check for table.column format or just column name
        name = result[0].get("products.name") or result[0].get("name")
        assert name == "Gadget"
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_where_with_and():
    """Test SELECT with AND operator in WHERE clause."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create and populate table
        db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT)")
        db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")
        db.execute("INSERT INTO users VALUES (3, 'Charlie', 35)")
        
        # Query with AND
        result = db.execute("SELECT * FROM users WHERE age > 25 AND name = 'Alice'")
        assert len(result) == 1
        assert result[0]["name"] == "Alice"
        assert result[0]["age"] == 30
        
        # Query with AND that matches multiple
        result = db.execute("SELECT * FROM users WHERE age >= 25 AND age <= 35")
        assert len(result) == 3  # All three users match
        
        # Query with AND that matches none
        result = db.execute("SELECT * FROM users WHERE age > 30 AND name = 'Alice'")
        assert len(result) == 0
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_where_with_or():
    """Test SELECT with OR operator in WHERE clause."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create and populate table
        db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT, status TEXT)")
        db.execute("INSERT INTO users VALUES (1, 'Alice', 'active')")
        db.execute("INSERT INTO users VALUES (2, 'Bob', 'inactive')")
        db.execute("INSERT INTO users VALUES (3, 'Charlie', 'active')")
        
        # Query with OR - match by id
        result = db.execute("SELECT * FROM users WHERE id = 1 OR id = 3")
        assert len(result) == 2
        names = [row["name"] for row in result]
        assert "Alice" in names
        assert "Charlie" in names
        
        # Query with OR - match by status
        result = db.execute("SELECT * FROM users WHERE status = 'active' OR status = 'inactive'")
        assert len(result) == 3  # All users match
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_where_with_and_or_mixed():
    """Test SELECT with mixed AND/OR operators."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create and populate table
        db.execute("CREATE TABLE products (id INT PRIMARY KEY, name TEXT, price FLOAT)")
        db.execute("INSERT INTO products VALUES (1, 'Widget', 10.00)")
        db.execute("INSERT INTO products VALUES (2, 'Gadget', 25.00)")
        db.execute("INSERT INTO products VALUES (3, 'Gizmo', 15.00)")
        
        # Query with mixed AND/OR
        # (price > 12 AND price < 20) OR (price < 10)
        # Widget: (10 > 12 AND 10 < 20) OR (10 < 10) = F OR F = F
        # Gadget: (25 > 12 AND 25 < 20) OR (25 < 10) = F OR F = F
        # Gizmo: (15 > 12 AND 15 < 20) OR (15 < 10) = T OR F = T
        result = db.execute("SELECT * FROM products WHERE price > 12 AND price < 20 OR price < 10")
        assert len(result) == 1  # Only Gizmo (15)
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_update_with_and_where():
    """Test UPDATE with AND operator in WHERE clause."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create and populate table
        db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT)")
        db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")
        db.execute("INSERT INTO users VALUES (3, 'Charlie', 35)")
        
        # Update with AND
        db.execute("UPDATE users SET age = 31 WHERE age > 25 AND age < 35")
        
        # Verify only Alice was updated
        result = db.execute("SELECT * FROM users WHERE name = 'Alice'")
        assert result[0]["age"] == 31
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_delete_with_or_where():
    """Test DELETE with OR operator in WHERE clause."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Create and populate table
        db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        db.execute("INSERT INTO users VALUES (1, 'Alice')")
        db.execute("INSERT INTO users VALUES (2, 'Bob')")
        db.execute("INSERT INTO users VALUES (3, 'Charlie')")
        
        # Delete with OR
        db.execute("DELETE FROM users WHERE id = 1 OR id = 3")
        
        # Verify deletions
        result = db.execute("SELECT * FROM users")
        assert len(result) == 1
        assert result[0]["name"] == "Bob"
        
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


if __name__ == "__main__":
    print("Running integration tests...")
    
    tests = [
        test_full_crud_workflow,
        test_constraint_enforcement,
        test_join_operations,
        test_ledger_persistence,
        test_complex_queries,
        test_where_with_and,
        test_where_with_or,
        test_where_with_and_or_mixed,
        test_update_with_and_where,
        test_delete_with_or_where
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\nRunning {test.__name__}...", end=" ")
            test()
            print("PASSED")
            passed += 1
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
