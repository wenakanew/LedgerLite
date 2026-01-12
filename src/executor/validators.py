"""
Constraint validators for LedgerLite.
"""

from typing import Dict, Any, List, Optional
from src.types import Table, Column, DataType
from src.utils import validate_type, convert_value, validate_row, build_row_dict


class ConstraintViolationError(Exception):
    """Raised when a constraint is violated."""
    pass


class TypeValidationError(Exception):
    """Raised when a type validation fails."""
    pass


def validate_row_types(values: List[Any], table: Table) -> None:
    """
    Validate that values match column types.
    
    Args:
        values: List of values to validate
        table: Table schema
        
    Raises:
        TypeValidationError: If type validation fails
    """
    if len(values) != len(table.columns):
        raise TypeValidationError(
            f"Expected {len(table.columns)} values, got {len(values)}"
        )
    
    for column, value in zip(table.columns, values):
        if value is None and column.is_primary_key:
            raise ConstraintViolationError(
                f"Primary key column '{column.name}' cannot be NULL"
            )
        
        if value is not None and not validate_type(value, column.data_type):
            raise TypeValidationError(
                f"Invalid type for column '{column.name}': "
                f"expected {column.data_type.value}, got {type(value).__name__}"
            )


def validate_primary_key(
    table: Table,
    row: Dict[str, Any],
    existing_rows: List[Dict[str, Any]],
    primary_key_index: Optional[Dict[Any, Dict[str, Any]]] = None
) -> None:
    """
    Validate primary key uniqueness.
    
    Args:
        table: Table schema
        row: Row to validate
        existing_rows: List of existing rows
        primary_key_index: Optional index for faster lookup
        
    Raises:
        ConstraintViolationError: If primary key is not unique
    """
    primary_key_col = table.get_primary_key_column()
    primary_key_value = row.get(primary_key_col.name)
    
    if primary_key_value is None:
        raise ConstraintViolationError(
            f"Primary key column '{primary_key_col.name}' cannot be NULL"
        )
    
    # Use index if available
    if primary_key_index is not None:
        if primary_key_value in primary_key_index:
            raise ConstraintViolationError(
                f"Primary key violation: value {primary_key_value} already exists"
            )
    else:
        # Check against existing rows
        for existing_row in existing_rows:
            if existing_row.get(primary_key_col.name) == primary_key_value:
                raise ConstraintViolationError(
                    f"Primary key violation: value {primary_key_value} already exists"
                )


def validate_unique_constraints(
    table: Table,
    row: Dict[str, Any],
    existing_rows: List[Dict[str, Any]],
    unique_indexes: Optional[Dict[str, Dict[Any, Dict[str, Any]]]] = None
) -> None:
    """
    Validate unique constraints.
    
    Args:
        table: Table schema
        row: Row to validate
        existing_rows: List of existing rows
        unique_indexes: Optional indexes for faster lookup
        
    Raises:
        ConstraintViolationError: If unique constraint is violated
    """
    for column in table.columns:
        if not column.is_unique or column.is_primary_key:
            continue  # Primary key is handled separately
        
        value = row.get(column.name)
        if value is None:
            continue  # NULL values are allowed in unique columns
        
        # Use index if available
        if unique_indexes is not None and column.name in unique_indexes:
            if value in unique_indexes[column.name]:
                raise ConstraintViolationError(
                    f"Unique constraint violation on column '{column.name}': "
                    f"value {value} already exists"
                )
        else:
            # Check against existing rows
            for existing_row in existing_rows:
                if existing_row.get(column.name) == value:
                    raise ConstraintViolationError(
                        f"Unique constraint violation on column '{column.name}': "
                        f"value {value} already exists"
                    )


def validate_constraints_for_update(
    table: Table,
    old_row: Dict[str, Any],
    new_row: Dict[str, Any],
    existing_rows: List[Dict[str, Any]],
    primary_key_index: Optional[Dict[Any, Dict[str, Any]]] = None,
    unique_indexes: Optional[Dict[str, Dict[Any, Dict[str, Any]]]] = None
) -> None:
    """
    Validate constraints for an UPDATE operation.
    
    Args:
        table: Table schema
        old_row: Original row
        new_row: Updated row
        existing_rows: List of existing rows (excluding old_row)
        primary_key_index: Optional primary key index
        unique_indexes: Optional unique constraint indexes
        
    Raises:
        ConstraintViolationError: If constraints are violated
    """
    primary_key_col = table.get_primary_key_column()
    old_pk = old_row.get(primary_key_col.name)
    new_pk = new_row.get(primary_key_col.name)
    
    # Check if primary key changed
    if old_pk != new_pk:
        # Validate new primary key is unique
        validate_primary_key(table, new_row, existing_rows, primary_key_index)
    
    # Check unique constraints for changed columns
    for column in table.columns:
        if not column.is_unique or column.is_primary_key:
            continue
        
        old_value = old_row.get(column.name)
        new_value = new_row.get(column.name)
        
        if old_value != new_value and new_value is not None:
            # Check if new value is unique
            validate_unique_constraints(
                table,
                new_row,
                existing_rows,
                unique_indexes
            )

