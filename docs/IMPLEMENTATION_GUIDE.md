# LedgerLite Implementation Guide

This guide provides a structured approach to implementing LedgerLite, a transaction-first relational database management system. The implementation prioritizes clarity, correctness, and intentional design over performance optimization.

---

## Technology Stack

### Language Selection

**Python 3.9+** is recommended for this implementation.

**Rationale:**
- Readability and maintainability align with project goals
- Rich standard library reduces external dependencies
- Rapid iteration supports learning and experimentation
- Strong typing support via type hints improves code clarity

**Alternative Options:**
- **TypeScript/Node.js**: Suitable if maintaining a single language across database engine and web application is preferred
- **Rust**: Appropriate for performance-focused implementations or systems programming learning
- **Go**: Balanced choice offering good performance with straightforward syntax

### Core Libraries

**Required:**
- `json` - Ledger persistence
- `datetime` - Timestamp generation
- `typing` - Type annotations
- `dataclasses` - Structured data definitions

**Optional:**
- `re` or `ply` - SQL parsing (regex-based or parser generator)
- `pytest` - Testing framework
- `flask` or `fastapi` - Web application framework

---

## System Architecture

The system consists of four primary components:

```
┌─────────────────────────────────┐
│      SQL Parser                 │
│  - Tokenization                 │
│  - AST Construction             │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Query Executor                │
│  - Statement execution          │
│  - Constraint validation        │
│  - Result generation            │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Ledger Store                  │
│  - Entry persistence            │
│  - State reconstruction         │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Index Manager                 │
│  - Primary key indexes          │
│  - Unique constraint indexes   │
└─────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation

#### Data Type Definitions

Define core data structures for the system:

```python
# src/types.py
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, List, Dict
from datetime import datetime

class DataType(Enum):
    INT = "INT"
    TEXT = "TEXT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"

class OperationType(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

@dataclass
class Column:
    name: str
    data_type: DataType
    is_primary_key: bool = False
    is_unique: bool = False

@dataclass
class Table:
    name: str
    columns: List[Column]

@dataclass
class LedgerEntry:
    transaction_id: int
    table_name: str
    operation: OperationType
    timestamp: str
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
```

#### Schema Manager

The schema manager maintains table definitions in memory and validates schema operations.

**Responsibilities:**
- Store table schemas
- Validate schema definitions
- Track table existence
- Enforce schema constraints

**Implementation approach:**
- Use a dictionary mapping table names to `Table` objects
- Validate column definitions during table creation
- Ensure primary key uniqueness at schema level

---

### Phase 2: Ledger Storage

#### Ledger Entry Format

Each ledger entry is a JSON object representing a single data modification:

```json
{
    "transaction_id": 1,
    "table_name": "users",
    "operation": "INSERT",
    "timestamp": "2026-01-15T10:30:00Z",
    "old_value": null,
    "new_value": {"id": 1, "email": "user@mail.com", "balance": 500.0}
}
```

#### Storage Implementation

**File Format:** JSON Lines (`.jsonl`)
- One JSON object per line
- Append-only writes
- Sequential read for state reconstruction

**File Location:** `data/ledger.jsonl`

**Operations:**
- **Write**: Append new entry to file
- **Read**: Parse all entries sequentially
- **State Reconstruction**: Replay entries to derive current state

#### State Reconstruction Algorithm

```python
def reconstruct_table_state(table_name: str, ledger_entries: List[LedgerEntry]) -> List[Dict[str, Any]]:
    """
    Reconstruct current table state by replaying ledger entries.
    
    Args:
        table_name: Name of the table to reconstruct
        ledger_entries: All ledger entries in chronological order
        
    Returns:
        List of current row states
    """
    current_rows = {}
    
    for entry in ledger_entries:
        if entry.table_name != table_name:
            continue
            
        if entry.operation == OperationType.INSERT:
            primary_key = get_primary_key(entry.new_value, table_name)
            current_rows[primary_key] = entry.new_value
            
        elif entry.operation == OperationType.UPDATE:
            primary_key = get_primary_key(entry.new_value, table_name)
            current_rows[primary_key] = entry.new_value
            
        elif entry.operation == OperationType.DELETE:
            primary_key = get_primary_key(entry.old_value, table_name)
            if primary_key in current_rows:
                del current_rows[primary_key]
    
    return list(current_rows.values())
```

**Performance Note:** For larger datasets, consider maintaining an in-memory cache of current state, rebuilding from ledger on startup.

---

### Phase 3: SQL Parser

#### Parser Design

**Approach:** Recursive descent parser or regex-based parser

**Recommended:** Start with a simple regex-based parser for the initial implementation, then refactor to recursive descent if complexity increases.

#### Abstract Syntax Tree (AST)

Define AST nodes for each SQL statement type:

```python
# src/parser/ast.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class CreateTableStatement:
    table_name: str
    columns: List[Column]

@dataclass
class InsertStatement:
    table_name: str
    values: List[Any]

@dataclass
class SelectStatement:
    columns: List[str]  # ["*"] or specific column names
    table_name: str
    where_clause: Optional[Dict[str, Any]] = None
    joins: Optional[List['JoinClause']] = None

@dataclass
class UpdateStatement:
    table_name: str
    set_clauses: Dict[str, Any]
    where_clause: Optional[Dict[str, Any]] = None

@dataclass
class DeleteStatement:
    table_name: str
    where_clause: Optional[Dict[str, Any]] = None

@dataclass
class JoinClause:
    table_name: str
    join_type: str  # "INNER"
    condition: Dict[str, str]  # {"left_col": "right_col"}
```

#### Parsing Strategy

1. **Tokenization**: Split SQL string into tokens
2. **Statement Identification**: Determine statement type
3. **Structure Parsing**: Extract statement-specific components
4. **AST Construction**: Build structured representation
5. **Validation**: Check syntax correctness

---

### Phase 4: Query Executor

#### CREATE TABLE Execution

```python
def execute_create_table(stmt: CreateTableStatement, schema_manager: SchemaManager) -> None:
    """
    Execute CREATE TABLE statement.
    
    Validates schema and registers table definition.
    """
    # Validate table doesn't already exist
    if schema_manager.table_exists(stmt.table_name):
        raise TableExistsError(f"Table {stmt.table_name} already exists")
    
    # Validate schema constraints
    validate_table_schema(stmt.columns)
    
    # Register table
    schema_manager.add_table(Table(name=stmt.table_name, columns=stmt.columns))
```

#### INSERT Execution

```python
def execute_insert(stmt: InsertStatement, executor: QueryExecutor) -> None:
    """
    Execute INSERT statement.
    
    Validates constraints, creates ledger entry, updates indexes.
    """
    # Get table schema
    table = schema_manager.get_table(stmt.table_name)
    
    # Validate data types
    validate_row_types(stmt.values, table.columns)
    
    # Build row dictionary
    row = {col.name: val for col, val in zip(table.columns, stmt.values)}
    
    # Check primary key uniqueness
    primary_key_value = row[get_primary_key_column(table).name]
    if index_manager.primary_key_exists(stmt.table_name, primary_key_value):
        raise ConstraintViolationError("Primary key violation")
    
    # Check unique constraints
    for column in table.columns:
        if column.is_unique and row[column.name] is not None:
            if index_manager.unique_value_exists(stmt.table_name, column.name, row[column.name]):
                raise ConstraintViolationError(f"Unique constraint violation on {column.name}")
    
    # Create ledger entry
    entry = create_ledger_entry(
        table_name=stmt.table_name,
        operation=OperationType.INSERT,
        new_value=row
    )
    
    # Persist ledger entry
    ledger_store.append(entry)
    
    # Update indexes
    index_manager.add_row(stmt.table_name, row)
```

#### SELECT Execution

```python
def execute_select(stmt: SelectStatement, executor: QueryExecutor) -> List[Dict[str, Any]]:
    """
    Execute SELECT statement.
    
    Reconstructs table state, applies filters, handles joins, projects columns.
    """
    # Get current table state
    rows = ledger_store.reconstruct_state(stmt.table_name)
    
    # Apply WHERE clause filtering
    if stmt.where_clause:
        rows = apply_where_clause(rows, stmt.where_clause)
    
    # Handle JOINs
    if stmt.joins:
        for join in stmt.joins:
            right_rows = ledger_store.reconstruct_state(join.table_name)
            rows = execute_join(rows, right_rows, join)
    
    # Project columns
    if stmt.columns == ["*"]:
        return rows
    else:
        return [{col: row[col] for col in stmt.columns} for row in rows]
```

#### UPDATE Execution

```python
def execute_update(stmt: UpdateStatement, executor: QueryExecutor) -> int:
    """
    Execute UPDATE statement.
    
    Returns number of rows updated.
    """
    # Get current table state
    rows = ledger_store.reconstruct_state(stmt.table_name)
    table = schema_manager.get_table(stmt.table_name)
    
    # Apply WHERE clause to find matching rows
    matching_rows = apply_where_clause(rows, stmt.where_clause) if stmt.where_clause else rows
    
    updated_count = 0
    for row in matching_rows:
        # Create updated row
        updated_row = row.copy()
        updated_row.update(stmt.set_clauses)
        
        # Validate constraints
        validate_constraints(updated_row, table)
        
        # Create ledger entry
        entry = create_ledger_entry(
            table_name=stmt.table_name,
            operation=OperationType.UPDATE,
            old_value=row,
            new_value=updated_row
        )
        
        # Persist ledger entry
        ledger_store.append(entry)
        
        # Update indexes
        index_manager.update_row(stmt.table_name, row, updated_row)
        
        updated_count += 1
    
    return updated_count
```

#### DELETE Execution

```python
def execute_delete(stmt: DeleteStatement, executor: QueryExecutor) -> int:
    """
    Execute DELETE statement.
    
    Returns number of rows deleted.
    """
    # Get current table state
    rows = ledger_store.reconstruct_state(stmt.table_name)
    
    # Apply WHERE clause to find matching rows
    matching_rows = apply_where_clause(rows, stmt.where_clause) if stmt.where_clause else rows
    
    deleted_count = 0
    for row in matching_rows:
        # Create ledger entry
        entry = create_ledger_entry(
            table_name=stmt.table_name,
            operation=OperationType.DELETE,
            old_value=row,
            new_value=None
        )
        
        # Persist ledger entry
        ledger_store.append(entry)
        
        # Update indexes
        index_manager.remove_row(stmt.table_name, row)
        
        deleted_count += 1
    
    return deleted_count
```

---

### Phase 5: Index Management

#### Index Structure

**Primary Key Index:**
```python
primary_key_indexes: Dict[str, Dict[Any, str]] = {
    "users": {1: "row_id_1", 2: "row_id_2"}
}
```

**Unique Constraint Index:**
```python
unique_indexes: Dict[str, Dict[str, Dict[Any, str]]] = {
    "users": {
        "email": {"user@mail.com": "row_id_1"}
    }
}
```

#### Index Operations

**On INSERT:**
- Add primary key to primary key index
- Add unique column values to unique indexes

**On UPDATE:**
- Update primary key index if primary key changed
- Update unique indexes for modified unique columns
- Remove old values, add new values

**On DELETE:**
- Remove from primary key index
- Remove from all unique indexes

**On SELECT:**
- Use index for WHERE clause lookups when applicable
- Fall back to full table scan if index not available

---

### Phase 6: Constraint Validation

#### Primary Key Validation

- Must be unique across all rows
- Cannot be NULL
- Validated before INSERT and UPDATE operations

#### Unique Constraint Validation

- Column values must be unique (excluding NULL)
- Multiple NULL values are permitted
- Validated before INSERT and UPDATE operations

#### Type Validation

- Ensure values match declared column data types
- Perform type conversion where appropriate (e.g., string to integer)
- Raise errors for incompatible types

---

### Phase 7: JOIN Implementation

#### INNER JOIN Algorithm

```python
def execute_inner_join(
    left_rows: List[Dict[str, Any]],
    right_rows: List[Dict[str, Any]],
    join_condition: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Execute INNER JOIN operation.
    
    Args:
        left_rows: Rows from left table
        right_rows: Rows from right table
        join_condition: Mapping of left column to right column
        
    Returns:
        List of joined rows
    """
    results = []
    
    for left_row in left_rows:
        for right_row in right_rows:
            if join_condition_matches(left_row, right_row, join_condition):
                merged_row = {**left_row, **right_row}
                results.append(merged_row)
    
    return results

def join_condition_matches(
    left_row: Dict[str, Any],
    right_row: Dict[str, Any],
    condition: Dict[str, str]
) -> bool:
    """Check if join condition is satisfied."""
    for left_col, right_col in condition.items():
        if left_row.get(left_col) != right_row.get(right_col):
            return False
    return True
```

**Optimization:** Use indexes when join columns are indexed to reduce nested loop iterations.

---

### Phase 8: REPL Interface

#### REPL Structure

```python
# src/main.py
def start_repl():
    """Start interactive REPL."""
    db = DatabaseEngine()
    
    print("LedgerLite REPL")
    print("Type 'exit' or 'quit' to exit")
    print()
    
    while True:
        try:
            query = input("ledgerlite> ").strip()
            
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query:
                continue
            
            # Parse and execute
            result = db.execute(query)
            
            # Display results
            display_result(result)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def display_result(result: Any) -> None:
    """Format and display query results."""
    if result is None:
        return
    
    if isinstance(result, list):
        if not result:
            print("(0 rows)")
            return
        
        # Print header
        headers = list(result[0].keys())
        print(" | ".join(headers))
        print("-" * (len(" | ".join(headers))))
        
        # Print rows
        for row in result:
            values = [str(row.get(h, "")) for h in headers]
            print(" | ".join(values))
        
        print(f"\n({len(result)} row(s))")
    else:
        print(result)
```

#### REPL Features

- Multi-line query support (semicolon-terminated)
- Clear error messages
- Formatted result display
- Command history (optional, using `readline`)

---

### Phase 9: Web Application

#### Backend API

**Flask Example:**

```python
# web/app.py
from flask import Flask, request, jsonify, render_template
from src.main import DatabaseEngine

app = Flask(__name__)
db = DatabaseEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def execute_query():
    try:
        query = request.json.get('query')
        result = db.execute(query)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/tables', methods=['GET'])
def list_tables():
    tables = db.list_tables()
    return jsonify({'tables': tables})

if __name__ == '__main__':
    app.run(debug=True)
```

#### Frontend

A minimal admin interface demonstrating CRUD operations:

- Table creation form
- Data insertion form
- Query interface
- Results display
- Transaction history viewer

**Technology:** Vanilla JavaScript with Fetch API, or a lightweight framework if preferred.

---

## Project Structure

```
LedgerLite/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # REPL entry point
│   ├── types.py                # Core data types
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── lexer.py            # Tokenizer
│   │   ├── parser.py           # SQL parser
│   │   └── ast.py              # AST node definitions
│   ├── executor/
│   │   ├── __init__.py
│   │   ├── executor.py         # Query executor
│   │   └── validators.py       # Constraint validation
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── ledger.py           # Ledger store
│   │   └── schema.py           # Schema manager
│   ├── index/
│   │   ├── __init__.py
│   │   └── index_manager.py    # Index operations
│   └── utils.py                # Helper functions
├── web/
│   ├── app.py                  # Web application
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       └── index.html
├── data/
│   └── ledger.jsonl            # Ledger file
└── tests/
    ├── test_parser.py
    ├── test_executor.py
    ├── test_ledger.py
    └── test_constraints.py
```

---

## Implementation Timeline

**Week 1-2: Foundation**
- Data type definitions
- Schema manager
- Ledger storage system

**Week 3: Parser and Basic Operations**
- SQL parser (CREATE TABLE, INSERT)
- Basic executor
- Constraint validation

**Week 4: Query Operations**
- SELECT, UPDATE, DELETE executors
- Index manager
- WHERE clause support

**Week 5: Advanced Features**
- JOIN implementation
- REPL interface
- Error handling improvements

**Week 6: Web Application and Testing**
- Web API and frontend
- Unit and integration tests
- Documentation and examples

---

## Design Decisions

### Ledger Format

**Choice:** JSON Lines format

**Rationale:**
- Append-only writes are straightforward
- Human-readable for debugging
- Easy to parse and process
- Suitable for the project scope

**Alternative:** SQLite database for ledger storage (more complex, better performance)

### State Reconstruction

**Choice:** Replay all ledger entries

**Rationale:**
- Simple and clear implementation
- Demonstrates ledger concept directly
- Easy to reason about correctness

**Alternative:** In-memory cache with periodic snapshots (better performance, more complexity)

### Index Strategy

**Choice:** In-memory hash maps

**Rationale:**
- Fast lookups
- Simple implementation
- Sufficient for project scope

**Alternative:** Persistent indexes with disk storage (better for larger datasets)

### Error Handling

**Approach:** Fail fast with clear error messages

**Rationale:**
- Prevents inconsistent state
- Aids debugging
- Provides clear feedback

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

- Parser tests for each statement type
- Executor tests for each operation
- Constraint validation tests
- Index manager tests

### Integration Tests

Test components working together:

- End-to-end query execution
- Ledger persistence and replay
- Multi-table operations
- JOIN operations

### Example Test

```python
def test_primary_key_constraint():
    db = DatabaseEngine()
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    
    with pytest.raises(ConstraintViolationError):
        db.execute("INSERT INTO users VALUES (1, 'Bob')")
```

---

## Getting Started

1. Set up Python environment (virtualenv recommended)
2. Create project structure
3. Implement data type definitions
4. Build schema manager
5. Implement ledger storage
6. Create SQL parser
7. Build query executor
8. Add constraint validation
9. Implement indexes
10. Add JOIN support
11. Create REPL
12. Build web application
13. Write tests
14. Document and polish

---

## Notes

This implementation prioritizes clarity and correctness over performance. The ledger-based approach provides natural auditability and demonstrates understanding of alternative data storage paradigms. Focus on making the code readable, well-structured, and correct rather than optimized.
