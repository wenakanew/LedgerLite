"""
Abstract Syntax Tree (AST) node definitions for SQL statements.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from src.types import Column, DataType


@dataclass
class CreateTableStatement:
    """AST node for CREATE TABLE statement."""
    table_name: str
    columns: List[Column]


@dataclass
class InsertStatement:
    """AST node for INSERT INTO statement."""
    table_name: str
    values: List[Any]


@dataclass
class SelectStatement:
    """AST node for SELECT statement."""
    columns: List[str]  # ["*"] or specific column names
    table_name: str
    where_clause: Optional[Dict[str, Any]] = None
    joins: Optional[List['JoinClause']] = None


@dataclass
class UpdateStatement:
    """AST node for UPDATE statement."""
    table_name: str
    set_clauses: Dict[str, Any]  # {column_name: value}
    where_clause: Optional[Dict[str, Any]] = None


@dataclass
class DeleteStatement:
    """AST node for DELETE FROM statement."""
    table_name: str
    where_clause: Optional[Dict[str, Any]] = None


@dataclass
class JoinClause:
    """AST node for JOIN clause."""
    table_name: str
    join_type: str  # "INNER"
    condition: Dict[str, str]  # {"left_col": "right_col"}

