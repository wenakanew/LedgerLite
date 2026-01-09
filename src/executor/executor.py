"""
Query executor for LedgerLite.

Executes parsed SQL statements and manages database operations.
"""

from typing import Any, List, Dict, Optional
from src.storage.schema import SchemaManager
from src.storage.ledger import LedgerStore
from src.index.index_manager import IndexManager
from src.executor.validators import (
    validate_row_types,
    validate_primary_key,
    validate_unique_constraints,
    validate_constraints_for_update,
    ConstraintViolationError,
    TypeValidationError
)
from src.utils import build_row_dict, validate_row
from src.parser.ast import (
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
    UpdateStatement,
    DeleteStatement
)
from src.types import OperationType, Table


class QueryExecutor:
    """Executes SQL statements."""
    
    def __init__(
        self,
        schema_manager: SchemaManager,
        ledger_store: LedgerStore,
        index_manager: IndexManager
    ):
        """Initialize query executor."""
        self.schema_manager = schema_manager
        self.ledger_store = ledger_store
        self.index_manager = index_manager
    
    def execute(self, ast: Any) -> Any:
        """
        Execute an AST node.
        
        Args:
            ast: AST node representing a SQL statement
            
        Returns:
            Execution result
        """
        if isinstance(ast, CreateTableStatement):
            return self.execute_create_table(ast)
        elif isinstance(ast, InsertStatement):
            return self.execute_insert(ast)
        elif isinstance(ast, SelectStatement):
            return self.execute_select(ast)
        elif isinstance(ast, UpdateStatement):
            return self.execute_update(ast)
        elif isinstance(ast, DeleteStatement):
            return self.execute_delete(ast)
        else:
            raise ValueError(f"Unknown AST node type: {type(ast)}")
    
    def execute_create_table(self, stmt: CreateTableStatement) -> str:
        """
        Execute CREATE TABLE statement.
        
        Args:
            stmt: CREATE TABLE AST node
            
        Returns:
            Success message
        """
        # Check if table already exists
        if self.schema_manager.table_exists(stmt.table_name):
            raise ValueError(f"Table '{stmt.table_name}' already exists")
        
        # Create table object
        table = Table(name=stmt.table_name, columns=stmt.columns)
        
        # Register table schema
        self.schema_manager.add_table(table)
        
        return f"Table '{stmt.table_name}' created successfully"
    
    def execute_insert(self, stmt: InsertStatement) -> str:
        """
        Execute INSERT statement.
        
        Args:
            stmt: INSERT AST node
            
        Returns:
            Success message
        """
        # Get table schema
        table = self.schema_manager.get_table(stmt.table_name)
        
        # Validate value types
        validate_row_types(stmt.values, table)
        
        # Build row dictionary
        row = build_row_dict(stmt.values, table)
        
        # Validate row structure
        validate_row(row, table)
        
        # Get current state for constraint validation
        primary_key_col = table.get_primary_key_column()
        existing_rows = self.ledger_store.reconstruct_state_with_primary_key(
            stmt.table_name,
            primary_key_col.name
        )
        
        # Get indexes for faster validation
        primary_key_index = self.index_manager.get_primary_key_index(stmt.table_name)
        unique_indexes = self.index_manager.get_unique_indexes(stmt.table_name)
        
        # Validate primary key uniqueness
        validate_primary_key(table, row, existing_rows, primary_key_index)
        
        # Validate unique constraints
        validate_unique_constraints(table, row, existing_rows, unique_indexes)
        
        # Create ledger entry
        entry = self.ledger_store.create_entry(
            table_name=stmt.table_name,
            operation=OperationType.INSERT,
            new_value=row
        )
        
        # Persist ledger entry
        self.ledger_store.append(entry)
        
        # Update indexes
        self.index_manager.add_row(table, row)
        
        return f"1 row inserted into '{stmt.table_name}'"
    
    def execute_select(self, stmt: SelectStatement) -> List[Dict[str, Any]]:
        """
        Execute SELECT statement.
        
        Args:
            stmt: SELECT AST node
            
        Returns:
            List of result rows
        """
        # Get table schema
        table = self.schema_manager.get_table(stmt.table_name)
        
        # Reconstruct current state
        primary_key_col = table.get_primary_key_column()
        rows = self.ledger_store.reconstruct_state_with_primary_key(
            stmt.table_name,
            primary_key_col.name
        )
        
        # Apply WHERE clause filtering
        if stmt.where_clause:
            rows = self._apply_where_clause(rows, stmt.where_clause)
        
        # Handle JOINs
        if stmt.joins:
            for join in stmt.joins:
                # Get joined table
                join_table = self.schema_manager.get_table(join.table_name)
                join_pk_col = join_table.get_primary_key_column()
                join_rows = self.ledger_store.reconstruct_state_with_primary_key(
                    join.table_name,
                    join_pk_col.name
                )
                
                # Perform join
                rows = self._execute_join(rows, join_rows, join.condition)
        
        # Project columns
        if stmt.columns == ["*"]:
            return rows
        else:
            # Handle table.column format
            result = []
            for row in rows:
                projected_row = {}
                for col_spec in stmt.columns:
                    if '.' in col_spec:
                        # table.column format
                        table_name, col_name = col_spec.split('.', 1)
                        if table_name in row or col_name in row:
                            # Use column name directly if present
                            if col_name in row:
                                projected_row[col_spec] = row[col_name]
                            else:
                                projected_row[col_spec] = row.get(col_spec, None)
                    else:
                        # Simple column name
                        projected_row[col_spec] = row.get(col_spec, None)
                result.append(projected_row)
            return result
    
    def execute_update(self, stmt: UpdateStatement) -> str:
        """
        Execute UPDATE statement.
        
        Args:
            stmt: UPDATE AST node
            
        Returns:
            Success message with count
        """
        # Get table schema
        table = self.schema_manager.get_table(stmt.table_name)
        
        # Reconstruct current state
        primary_key_col = table.get_primary_key_column()
        rows = self.ledger_store.reconstruct_state_with_primary_key(
            stmt.table_name,
            primary_key_col.name
        )
        
        # Apply WHERE clause to find matching rows
        if stmt.where_clause:
            matching_rows = self._apply_where_clause(rows, stmt.where_clause)
        else:
            matching_rows = rows
        
        updated_count = 0
        for old_row in matching_rows:
            # Create updated row
            new_row = old_row.copy()
            new_row.update(stmt.set_clauses)
            
            # Convert values to appropriate types
            for col_name, value in stmt.set_clauses.items():
                column = table.get_column(col_name)
                if column:
                    from src.utils import convert_value
                    try:
                        new_row[col_name] = convert_value(value, column.data_type)
                    except ValueError:
                        pass  # Keep original value if conversion fails
            
            # Validate constraints
            other_rows = [r for r in rows if r != old_row]
            primary_key_index = self.index_manager.get_primary_key_index(stmt.table_name)
            unique_indexes = self.index_manager.get_unique_indexes(stmt.table_name)
            
            try:
                validate_constraints_for_update(
                    table,
                    old_row,
                    new_row,
                    other_rows,
                    primary_key_index,
                    unique_indexes
                )
            except ConstraintViolationError as e:
                raise ConstraintViolationError(
                    f"Update failed: {e}"
                )
            
            # Create ledger entry
            entry = self.ledger_store.create_entry(
                table_name=stmt.table_name,
                operation=OperationType.UPDATE,
                old_value=old_row,
                new_value=new_row
            )
            
            # Persist ledger entry
            self.ledger_store.append(entry)
            
            # Update indexes
            self.index_manager.update_row(table, old_row, new_row)
            
            updated_count += 1
        
        return f"{updated_count} row(s) updated in '{stmt.table_name}'"
    
    def execute_delete(self, stmt: DeleteStatement) -> str:
        """
        Execute DELETE statement.
        
        Args:
            stmt: DELETE AST node
            
        Returns:
            Success message with count
        """
        # Get table schema
        table = self.schema_manager.get_table(stmt.table_name)
        
        # Reconstruct current state
        primary_key_col = table.get_primary_key_column()
        rows = self.ledger_store.reconstruct_state_with_primary_key(
            stmt.table_name,
            primary_key_col.name
        )
        
        # Apply WHERE clause to find matching rows
        if stmt.where_clause:
            matching_rows = self._apply_where_clause(rows, stmt.where_clause)
        else:
            matching_rows = rows
        
        deleted_count = 0
        for row in matching_rows:
            # Create ledger entry
            entry = self.ledger_store.create_entry(
                table_name=stmt.table_name,
                operation=OperationType.DELETE,
                old_value=row,
                new_value=None
            )
            
            # Persist ledger entry
            self.ledger_store.append(entry)
            
            # Update indexes
            self.index_manager.remove_row(table, row)
            
            deleted_count += 1
        
        return f"{deleted_count} row(s) deleted from '{stmt.table_name}'"
    
    def _apply_where_clause(
        self,
        rows: List[Dict[str, Any]],
        where_clause: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply WHERE clause filtering to rows.
        
        Args:
            rows: List of rows to filter
            where_clause: WHERE clause specification
            
        Returns:
            Filtered rows
        """
        column = where_clause["column"]
        operator = where_clause["operator"]
        value = where_clause["value"]
        
        result = []
        for row in rows:
            row_value = row.get(column)
            
            if operator == "=":
                if row_value == value:
                    result.append(row)
            elif operator == "!=":
                if row_value != value:
                    result.append(row)
            elif operator == ">":
                if row_value is not None and value is not None and row_value > value:
                    result.append(row)
            elif operator == "<":
                if row_value is not None and value is not None and row_value < value:
                    result.append(row)
            elif operator == ">=":
                if row_value is not None and value is not None and row_value >= value:
                    result.append(row)
            elif operator == "<=":
                if row_value is not None and value is not None and row_value <= value:
                    result.append(row)
        
        return result
    
    def _execute_join(
        self,
        left_rows: List[Dict[str, Any]],
        right_rows: List[Dict[str, Any]],
        condition: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Execute INNER JOIN operation.
        
        Args:
            left_rows: Rows from left table
            right_rows: Rows from right table
            condition: Join condition mapping
            
        Returns:
            Joined rows
        """
        results = []
        
        for left_row in left_rows:
            for right_row in right_rows:
                # Check join condition
                match = True
                for left_col, right_col in condition.items():
                    if left_row.get(left_col) != right_row.get(right_col):
                        match = False
                        break
                
                if match:
                    # Merge rows (right table columns override left if same name)
                    merged_row = {**left_row, **right_row}
                    results.append(merged_row)
        
        return results
