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
    # Join condition keys are in table.column format
    assert "users.id" in stmt.joins[0].condition
    assert stmt.joins[0].condition["users.id"] == "orders.user_id"


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


def test_parse_select_with_where_and():
    """Test parsing SELECT with AND operator in WHERE clause."""
    sql = "SELECT * FROM users WHERE id = 1 AND name = 'Alice'"
    stmt = parse_sql(sql)
    
    assert stmt.where_clause is not None
    assert stmt.where_clause["type"] == "AND"
    assert stmt.where_clause["left"]["type"] == "CONDITION"
    assert stmt.where_clause["left"]["column"] == "id"
    assert stmt.where_clause["left"]["value"] == 1
    assert stmt.where_clause["right"]["type"] == "CONDITION"
    assert stmt.where_clause["right"]["column"] == "name"
    assert stmt.where_clause["right"]["value"] == "Alice"


def test_parse_select_with_where_or():
    """Test parsing SELECT with OR operator in WHERE clause."""
    sql = "SELECT * FROM users WHERE id = 1 OR id = 2"
    stmt = parse_sql(sql)
    
    assert stmt.where_clause is not None
    assert stmt.where_clause["type"] == "OR"
    assert stmt.where_clause["left"]["column"] == "id"
    assert stmt.where_clause["left"]["value"] == 1
    assert stmt.where_clause["right"]["column"] == "id"
    assert stmt.where_clause["right"]["value"] == 2


def test_parse_select_with_where_and_or():
    """Test parsing SELECT with mixed AND/OR (AND has higher precedence)."""
    sql = "SELECT * FROM users WHERE id = 1 AND name = 'Alice' OR id = 2"
    stmt = parse_sql(sql)
    
    assert stmt.where_clause is not None
    assert stmt.where_clause["type"] == "OR"
    # Left side should be the AND
    assert stmt.where_clause["left"]["type"] == "AND"
    # Right side should be the simple condition
    assert stmt.where_clause["right"]["type"] == "CONDITION"


def test_parse_select_with_where_chained_and():
    """Test parsing SELECT with chained AND operators."""
    sql = "SELECT * FROM users WHERE id = 1 AND name = 'Alice' AND age > 25"
    stmt = parse_sql(sql)
    
    assert stmt.where_clause is not None
    assert stmt.where_clause["type"] == "AND"
    # Left side should be another AND
    assert stmt.where_clause["left"]["type"] == "AND"
    # Right side should be a condition
    assert stmt.where_clause["right"]["type"] == "CONDITION"
    assert stmt.where_clause["right"]["operator"] == ">"


def test_parse_update_with_where_and():
    """Test parsing UPDATE with AND in WHERE clause."""
    sql = "UPDATE users SET name = 'Bob' WHERE id = 1 AND status = 'active'"
    stmt = parse_sql(sql)
    
    assert stmt.where_clause is not None
    assert stmt.where_clause["type"] == "AND"


def test_parse_delete_with_where_or():
    """Test parsing DELETE with OR in WHERE clause."""
    sql = "DELETE FROM users WHERE id = 1 OR id = 2"
    stmt = parse_sql(sql)
    
    assert stmt.where_clause is not None
    assert stmt.where_clause["type"] == "OR"

