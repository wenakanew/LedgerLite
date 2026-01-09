"""
Utility functions for LedgerLite.
"""

from typing import Any, Dict
from src.types import DataType, Column, Table


def validate_type(value: Any, data_type: DataType) -> bool:
    """
    Validate that a value matches the expected data type.
    
    Args:
        value: Value to validate
        data_type: Expected data type
        
    Returns:
        True if value matches type, False otherwise
    """
    if value is None:
        return True  # NULL values are allowed for now
    
    type_map = {
        DataType.INT: int,
        DataType.TEXT: str,
        DataType.FLOAT: (int, float),  # Accept both int and float
        DataType.BOOLEAN: bool,
        DataType.TIMESTAMP: str,  # Timestamps stored as strings
    }
    
    expected_type = type_map.get(data_type)
    if expected_type is None:
        return False
    
    if isinstance(expected_type, tuple):
        return isinstance(value, expected_type)
    return isinstance(value, expected_type)


def convert_value(value: Any, data_type: DataType) -> Any:
    """
    Convert a value to the appropriate type.
    
    Args:
        value: Value to convert
        data_type: Target data type
        
    Returns:
        Converted value
        
    Raises:
        ValueError: If conversion is not possible
    """
    if value is None:
        return None
    
    try:
        if data_type == DataType.INT:
            return int(value)
        elif data_type == DataType.TEXT:
            return str(value)
        elif data_type == DataType.FLOAT:
            return float(value)
        elif data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif data_type == DataType.TIMESTAMP:
            return str(value)
        else:
            return value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot convert {value} to {data_type.value}: {e}")


def build_row_dict(values: list, table: Table) -> Dict[str, Any]:
    """
    Build a row dictionary from values and table schema.
    
    Args:
        values: List of values in column order
        table: Table schema
        
    Returns:
        Dictionary mapping column names to values
        
    Raises:
        ValueError: If number of values doesn't match columns
    """
    if len(values) != len(table.columns):
        raise ValueError(
            f"Expected {len(table.columns)} values, got {len(values)}"
        )
    
    row = {}
    for column, value in zip(table.columns, values):
        # Convert value to appropriate type
        converted_value = convert_value(value, column.data_type)
        row[column.name] = converted_value
    
    return row


def validate_row(row: Dict[str, Any], table: Table) -> None:
    """
    Validate a row against table schema.
    
    Args:
        row: Row dictionary
        table: Table schema
        
    Raises:
        ValueError: If validation fails
    """
    # Check all required columns are present
    for column in table.columns:
        if column.name not in row:
            raise ValueError(f"Missing column: {column.name}")
        
        # Validate type
        if not validate_type(row[column.name], column.data_type):
            raise ValueError(
                f"Invalid type for column {column.name}: "
                f"expected {column.data_type.value}"
            )
        
        # Check primary key is not None
        if column.is_primary_key and row[column.name] is None:
            raise ValueError(f"Primary key column {column.name} cannot be NULL")
