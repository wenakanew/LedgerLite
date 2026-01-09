"""
Index manager for LedgerLite.

Manages indexes for primary keys and unique constraints.
"""

from typing import Dict, Any, Optional, List
from src.types import Table


class IndexManager:
    """Manages indexes for fast lookups."""
    
    def __init__(self):
        """Initialize index manager."""
        # Primary key index: {table_name: {primary_key_value: row}}
        self._primary_key_indexes: Dict[str, Dict[Any, Dict[str, Any]]] = {}
        
        # Unique constraint indexes: {table_name: {column_name: {value: row}}}
        self._unique_indexes: Dict[str, Dict[str, Dict[Any, Dict[str, Any]]]] = {}
    
    def add_row(self, table: Table, row: Dict[str, Any]) -> None:
        """
        Add a row to indexes.
        
        Args:
            table: Table schema
            row: Row to index
        """
        table_name = table.name
        
        # Initialize indexes for table if needed
        if table_name not in self._primary_key_indexes:
            self._primary_key_indexes[table_name] = {}
        if table_name not in self._unique_indexes:
            self._unique_indexes[table_name] = {}
        
        # Add to primary key index
        primary_key_col = table.get_primary_key_column()
        primary_key_value = row.get(primary_key_col.name)
        if primary_key_value is not None:
            self._primary_key_indexes[table_name][primary_key_value] = row
        
        # Add to unique constraint indexes
        for column in table.columns:
            if column.is_unique and not column.is_primary_key:
                if column.name not in self._unique_indexes[table_name]:
                    self._unique_indexes[table_name][column.name] = {}
                
                value = row.get(column.name)
                if value is not None:
                    self._unique_indexes[table_name][column.name][value] = row
    
    def update_row(
        self,
        table: Table,
        old_row: Dict[str, Any],
        new_row: Dict[str, Any]
    ) -> None:
        """
        Update indexes when a row is modified.
        
        Args:
            table: Table schema
            old_row: Original row
            new_row: Updated row
        """
        table_name = table.name
        primary_key_col = table.get_primary_key_column()
        
        # Remove old primary key
        old_pk = old_row.get(primary_key_col.name)
        if old_pk is not None and old_pk in self._primary_key_indexes.get(table_name, {}):
            del self._primary_key_indexes[table_name][old_pk]
        
        # Add new primary key
        new_pk = new_row.get(primary_key_col.name)
        if new_pk is not None:
            if table_name not in self._primary_key_indexes:
                self._primary_key_indexes[table_name] = {}
            self._primary_key_indexes[table_name][new_pk] = new_row
        
        # Update unique constraint indexes
        for column in table.columns:
            if column.is_unique and not column.is_primary_key:
                old_value = old_row.get(column.name)
                new_value = new_row.get(column.name)
                
                if table_name not in self._unique_indexes:
                    self._unique_indexes[table_name] = {}
                if column.name not in self._unique_indexes[table_name]:
                    self._unique_indexes[table_name][column.name] = {}
                
                # Remove old value
                if old_value is not None and old_value in self._unique_indexes[table_name][column.name]:
                    del self._unique_indexes[table_name][column.name][old_value]
                
                # Add new value
                if new_value is not None:
                    self._unique_indexes[table_name][column.name][new_value] = new_row
    
    def remove_row(self, table: Table, row: Dict[str, Any]) -> None:
        """
        Remove a row from indexes.
        
        Args:
            table: Table schema
            row: Row to remove
        """
        table_name = table.name
        primary_key_col = table.get_primary_key_column()
        
        # Remove from primary key index
        primary_key_value = row.get(primary_key_col.name)
        if (primary_key_value is not None and 
            table_name in self._primary_key_indexes and
            primary_key_value in self._primary_key_indexes[table_name]):
            del self._primary_key_indexes[table_name][primary_key_value]
        
        # Remove from unique constraint indexes
        for column in table.columns:
            if column.is_unique and not column.is_primary_key:
                value = row.get(column.name)
                if (value is not None and
                    table_name in self._unique_indexes and
                    column.name in self._unique_indexes[table_name] and
                    value in self._unique_indexes[table_name][column.name]):
                    del self._unique_indexes[table_name][column.name][value]
    
    def primary_key_exists(self, table_name: str, primary_key_value: Any) -> bool:
        """
        Check if a primary key value exists.
        
        Args:
            table_name: Name of the table
            primary_key_value: Primary key value to check
            
        Returns:
            True if primary key exists, False otherwise
        """
        return (table_name in self._primary_key_indexes and
                primary_key_value in self._primary_key_indexes[table_name])
    
    def unique_value_exists(
        self,
        table_name: str,
        column_name: str,
        value: Any
    ) -> bool:
        """
        Check if a unique value exists.
        
        Args:
            table_name: Name of the table
            column_name: Name of the unique column
            value: Value to check
            
        Returns:
            True if value exists, False otherwise
        """
        return (table_name in self._unique_indexes and
                column_name in self._unique_indexes[table_name] and
                value in self._unique_indexes[table_name][column_name])
    
    def get_primary_key_index(self, table_name: str) -> Optional[Dict[Any, Dict[str, Any]]]:
        """Get primary key index for a table."""
        return self._primary_key_indexes.get(table_name)
    
    def get_unique_indexes(self, table_name: str) -> Optional[Dict[str, Dict[Any, Dict[str, Any]]]]:
        """Get unique constraint indexes for a table."""
        return self._unique_indexes.get(table_name)
    
    def rebuild_indexes(self, table: Table, rows: List[Dict[str, Any]]) -> None:
        """
        Rebuild indexes for a table from rows.
        
        Args:
            table: Table schema
            rows: List of rows to index
        """
        table_name = table.name
        
        # Clear existing indexes
        if table_name in self._primary_key_indexes:
            del self._primary_key_indexes[table_name]
        if table_name in self._unique_indexes:
            del self._unique_indexes[table_name]
        
        # Rebuild indexes
        for row in rows:
            self.add_row(table, row)
