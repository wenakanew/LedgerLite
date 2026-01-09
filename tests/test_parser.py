"""
Tests for SQL parser.
"""

import pytest
from src.parser.parser import parse_sql, ParserError
from src.parser.ast import CreateTableStatement, InsertStatement, SelectStatement
from src.types import DataType, Column


def test_parse_create_table():
    """Test parsing CREATE TABLE statement."""
    sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"
    stmt = parse_sql(sql)
    
    assert isinstance(stmt, CreateTableStatement)
    assert stmt.table_name == "users"
    assert len(stmt.columns) == 2
    assert stmt.columns[0].name == "id"
    assert stmt.columns[0].data_type == DataType.INT
    assert stmt.columns[0].is_primary_key is True
    assert stmt.columns[1].name == "name"
    assert stmt.columns[1].data_type == DataType.TEXT


def test_parse_create_table_with_unique():
    """Test parsing CREATE TABLE with UNIQUE constraint."""
    sql = "CREATE TABLE users (id INT PRIMARY KEY, email TEXT UNIQUE)"
    stmt = parse_sql(sql)
    
    assert stmt.columns[1].is_unique is True


def test_parse_insert():
    """Test parsing INSERT statement."""
    sql = "INSERT INTO users VALUES (1, 'Alice')"
    stmt = parse_sql(sql)
    
    assert isinstance(stmt, InsertStatement)
    assert stmt.table_name == "users"
    assert stmt.values == [1, "Alice"]


def test_parse_insert_with_numbers():
    """Test parsing INSERT with different number types."""
    sql = "INSERT INTO products VALUES (1, 'Widget', 19.99)"
    stmt = parse_sql(sql)
    
    assert stmt.values[0] == 1
    assert stmt.values[1] == "Widget"
    assert stmt.values[2] == 19.99


def test_parse_select_all():
    """Test parsing SELECT * statement."""
    sql = "SELECT * FROM users"
    stmt = parse_sql(sql)
    
    assert isinstance(stmt, SelectStatement)
    assert stmt.columns == ["*"]
    assert stmt.table_name == "users"
    assert stmt.where_clause is None


def test_parse_select_columns():
    """Test parsing SELECT with specific columns."""
    sql = "SELECT id, name FROM users"
    stmt = parse_sql(sql)
    
    assert stmt.columns == ["id", "name"]
    assert stmt.table_name == "users"


def test_parse_select_with_where():
    """Test parsing SELECT with WHERE clause."""
    sql = "SELECT * FROM users WHERE id = 1"
    stmt = parse_sql(sql)
    
    assert stmt.where_clause is not None
    assert stmt.where_clause["column"] == "id"
    assert stmt.where_clause["operator"] == "="
    assert stmt.where_clause["value"] == 1


def test_parse_select_with_join():
    """Test parsing SELECT with JOIN."""
    sql = "SELECT users.name, orders.amount FROM users INNER JOIN orders ON users.id = orders.user_id"
    stmt = parse_sql(sql)
    
    assert len(stmt.joins) == 1
    assert stmt.joins[0].table_name == "orders"
    assert stmt.joins[0].join_type == "INNER"
    assert "id" in stmt.joins[0].condition
    assert stmt.joins[0].condition["id"] == "user_id"


def test_parse_update():
    """Test parsing UPDATE statement."""
    sql = "UPDATE users SET name = 'Bob' WHERE id = 1"
    stmt = parse_sql(sql)
    
    assert stmt.table_name == "users"
    assert stmt.set_clauses == {"name": "Bob"}
    assert stmt.where_clause["column"] == "id"
    assert stmt.where_clause["value"] == 1


def test_parse_delete():
    """Test parsing DELETE statement."""
    sql = "DELETE FROM users WHERE id = 1"
    stmt = parse_sql(sql)
    
    assert stmt.table_name == "users"
    assert stmt.where_clause["column"] == "id"
    assert stmt.where_clause["value"] == 1


def test_parse_delete_no_where():
    """Test parsing DELETE without WHERE clause."""
    sql = "DELETE FROM users"
    stmt = parse_sql(sql)
    
    assert stmt.table_name == "users"
    assert stmt.where_clause is None


def test_parse_with_semicolon():
    """Test parsing statements with semicolon."""
    sql = "CREATE TABLE users (id INT PRIMARY KEY);"
    stmt = parse_sql(sql)
    
    assert isinstance(stmt, CreateTableStatement)
    assert stmt.table_name == "users"


def test_parse_error_invalid_syntax():
    """Test that invalid syntax raises ParserError."""
    with pytest.raises(ParserError):
        parse_sql("CREATE TABLE")


def test_parse_error_missing_table_name():
    """Test that missing table name raises error."""
    with pytest.raises(ParserError):
        parse_sql("CREATE TABLE (id INT PRIMARY KEY)")
