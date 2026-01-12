"""
Schema manager for LedgerLite.

Handles table schema registration, validation, and retrieval.
"""

from typing import Dict, Optional
from src.types import Table


class SchemaManager:
    """Manages table schemas."""
    
    def __init__(self):
        """Initialize schema manager."""
        self._tables: Dict[str, Table] = {}
    
    def add_table(self, table: Table) -> None:
        """
        Register a new table schema.
        
        Args:
            table: Table schema to register
            
        Raises:
            ValueError: If table already exists
        """
        if table.name in self._tables:
            raise ValueError(f"Table '{table.name}' already exists")
        self._tables[table.name] = table
    
    def get_table(self, table_name: str) -> Table:
        """
        Get table schema by name.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table schema
            
        Raises:
            ValueError: If table does not exist
        """
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        return self._tables[table_name]
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table
            
        Returns:
            True if table exists, False otherwise
        """
        return table_name in self._tables
    
    def list_tables(self) -> list[str]:
        """
        List all registered table names.
        
        Returns:
            List of table names
        """
        return list(self._tables.keys())
    
    def remove_table(self, table_name: str) -> None:
        """
        Remove a table schema.
        
        Args:
            table_name: Name of the table to remove
            
        Raises:
            ValueError: If table does not exist
        """
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        del self._tables[table_name]
    
    def get_all_tables(self) -> list[Table]:
        """
        Get all registered table schemas.
        
        Returns:
            List of all Table objects
        """
        return list(self._tables.values())

