"""
Core data type definitions for LedgerLite.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, List, Dict


class DataType(Enum):
    """Supported column data types."""
    INT = "INT"
    TEXT = "TEXT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"


class OperationType(Enum):
    """Types of operations that can be recorded in the ledger."""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass
class Column:
    """Represents a table column definition."""
    name: str
    data_type: DataType
    is_primary_key: bool = False
    is_unique: bool = False
    
    def __post_init__(self):
        """Validate column definition."""
        if not self.name:
            raise ValueError("Column name cannot be empty")
        if self.is_primary_key and self.is_unique:
            # Primary key is implicitly unique, so we can simplify
            pass


@dataclass
class Table:
    """Represents a table schema."""
    name: str
    columns: List[Column]
    
    def __post_init__(self):
        """Validate table definition."""
        if not self.name:
            raise ValueError("Table name cannot be empty")
        if not self.columns:
            raise ValueError("Table must have at least one column")
        
        # Validate primary key exists and is unique
        primary_keys = [col for col in self.columns if col.is_primary_key]
        if len(primary_keys) > 1:
            raise ValueError("Table can have at most one primary key")
        if len(primary_keys) == 0:
            raise ValueError("Table must have a primary key")
        
        # Check for duplicate column names
        column_names = [col.name for col in self.columns]
        if len(column_names) != len(set(column_names)):
            raise ValueError("Duplicate column names are not allowed")
    
    def get_primary_key_column(self) -> Column:
        """Get the primary key column."""
        for col in self.columns:
            if col.is_primary_key:
                return col
        raise ValueError("No primary key column found")
    
    def get_column(self, name: str) -> Optional[Column]:
        """Get a column by name."""
        for col in self.columns:
            if col.name == name:
                return col
        return None


@dataclass
class LedgerEntry:
    """Represents a single ledger entry recording a data modification."""
    transaction_id: int
    table_name: str
    operation: OperationType
    timestamp: str
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ledger entry to dictionary for JSON serialization."""
        return {
            "transaction_id": self.transaction_id,
            "table_name": self.table_name,
            "operation": self.operation.value,
            "timestamp": self.timestamp,
            "old_value": self.old_value,
            "new_value": self.new_value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LedgerEntry":
        """Create ledger entry from dictionary."""
        return cls(
            transaction_id=data["transaction_id"],
            table_name=data["table_name"],
            operation=OperationType(data["operation"]),
            timestamp=data["timestamp"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value")
        )

