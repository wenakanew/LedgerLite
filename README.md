# LedgerLite

> **A Transaction-First Mini Relational Database System Built from Scratch**
>
> A complete, working relational database with immutable ledger-based storage, SQL parsing, constraint validation, and multiple user interfaces.

![Status](https://img.shields.io/badge/Status-Complete-brightgreen) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Tests](https://img.shields.io/badge/Tests-50%2B%20Passing-brightgreen)

---

## 📚 Table of Contents

- [Quick Start](#quick-start)
- [Overview](#overview)
- [Key Features](#key-features)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Core Concept: Ledger-Based Storage](#core-concept-ledger-based-storage)
- [Architecture](#architecture)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Documentation](#documentation)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Limitations & Future Work](#limitations--future-work)
- [Project Stats](#project-stats)
- [Contributing](#contributing)

---

## Quick Start

### Installation

```bash
# Clone and setup
git clone <repository_url>
cd LedgerLite
pip install -r requirements.txt
```

### Try it Now (Choose One)

```bash
# 1. Run comprehensive demo showing all features
python demo.py

# 2. Or start interactive REPL
python -m src.main

# 3. Or run web application
python web/app.py
# Then visit http://localhost:5000
```

### Simple Example

```sql
-- Create a table with constraints
CREATE TABLE users (
  id INT PRIMARY KEY,
  name TEXT UNIQUE,
  email TEXT UNIQUE,
  balance FLOAT
);

-- Insert data with validation
INSERT INTO users VALUES (1, 'Alice', 'alice@company.com', 1000.00);
INSERT INTO users VALUES (2, 'Bob', 'bob@company.com', 500.00);

-- Query with complex filters
SELECT * FROM users WHERE balance > 750.00 AND name = 'Alice';

-- Update with WHERE clause
UPDATE users SET balance = 1100.00 WHERE id = 1;

-- Delete with WHERE clause
DELETE FROM users WHERE balance < 600.00;
```

---

## Overview

**LedgerLite** is a lightweight relational database management system (RDBMS) built entirely from scratch. It prioritizes **correctness, clarity, and traceability** over performance or feature completeness.

### Core Philosophy

Instead of overwriting data, LedgerLite records **every change as an immutable ledger entry**. The current database state is derived by replaying these entries. This design, inspired by real-world financial systems, provides:

- ✅ **Full auditability** - Complete change history
- ✅ **Natural consistency** - Derived state is always consistent
- ✅ **Easy debugging** - Trace any change through the ledger
- ✅ **Simple rollback** - Just remove entries and replay
- ✅ **Clear reasoning** - Data changes are facts, not mutations

### Why LedgerLite?

LedgerLite was created as part of the **Pesapal Junior Developer Challenge 2026** to demonstrate:

1. Understanding of **relational database fundamentals**
2. Ability to **build complex systems from scratch**
3. **Software engineering** discipline (modular design, testing, documentation)
4. **System design** thinking (architecture, trade-offs, clarity)

---

## Key Features

### ✅ Core Database Functionality

| Feature | Status | Details |
|---------|--------|---------|
| **Ledger-Based Storage** | ✅ | Immutable transaction log for auditability |
| **CRUD Operations** | ✅ | Full Create, Read, Update, Delete |
| **Constraints** | ✅ | PRIMARY KEY, UNIQUE constraints enforced |
| **Type System** | ✅ | INT, TEXT, FLOAT, BOOLEAN, TIMESTAMP |
| **Indexes** | ✅ | Fast lookups on primary/unique keys |
| **JOINs** | ✅ | INNER JOIN with multiple tables |
| **WHERE Clauses** | ✅ | All operators + AND/OR with precedence |
| **State Reconstruction** | ✅ | Replay ledger for current state |

### 🎯 User Interfaces

- **Interactive REPL** - Full SQL in the terminal with pretty formatting
- **Web API** - RESTful endpoints for programmatic access
- **Demo Script** - Comprehensive feature showcase
- **Programmatic API** - Direct Python access to database engine

### 🛠️ SQL Support

**Statements:**
- `CREATE TABLE` - Define schemas with constraints
- `INSERT INTO` - Add rows with validation
- `SELECT` - Query with filtering and joins
- `UPDATE` - Modify rows with WHERE clauses
- `DELETE FROM` - Remove rows with WHERE clauses

**Operators:**
- **Comparison:** `=`, `!=`, `>`, `<`, `>=`, `<=`
- **Logical:** `AND`, `OR` (with proper precedence - AND binds tighter)
- **Supported in:** SELECT WHERE, UPDATE WHERE, DELETE WHERE, JOIN conditions

**Data Types:**
- `INT` - Integers
- `TEXT` - Strings
- `FLOAT` - Decimals
- `BOOLEAN` - True/False
- `TIMESTAMP` - Date/Time (as strings)

### 📊 Data Integrity

- PRIMARY KEY uniqueness enforced on INSERT/UPDATE
- UNIQUE constraints validated
- Type checking on all operations
- NULL validation for primary keys
- Automatic rollback on constraint violation

---

## Installation & Setup

### Requirements

- Python 3.9 or higher
- pip package manager
- ~5 MB disk space
- No external database required

### Standard Installation

```bash
# Clone repository
git clone <repository_url>
cd LedgerLite

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Run tests
pytest tests/ -v
# Expected: 50+ tests passing ✓

# Try the demo
python demo.py
# Should show 6 demonstrations without errors
```

### What Gets Installed

- **pytest** - Testing framework
- **flask** - Web framework for demo app
- **mypy** - Type checking (optional)
- **black** - Code formatter (optional)

---

## Usage

### Method 1: Interactive REPL (Best for Learning)

```bash
python -m src.main
```

**Features:**
- Multi-line query support (end with `;` or blank line)
- Pretty table formatting for results
- Clear error messages
- Commands: `exit`, `quit`, or `Ctrl+C`

**Example Session:**

```
ledgerlite> CREATE TABLE employees (
...         emp_id INT PRIMARY KEY,
...         name TEXT,
...         salary FLOAT
...         );
Table 'employees' created successfully

ledgerlite> INSERT INTO employees VALUES (1, 'Alice', 75000.00);
1 row inserted into 'employees'

ledgerlite> SELECT * FROM employees WHERE salary > 60000;
emp_id | name  | salary
-------|-------|-------
1      | Alice | 75000.0

(1 row(s))

ledgerlite> exit
Goodbye!
```

### Method 2: Web Application

```bash
python web/app.py
```

Then visit `http://localhost:5000`

**REST API Endpoints:**

```bash
# Execute a query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users"}'

# List all tables
curl http://localhost:5000/api/tables

# Get table schema
curl http://localhost:5000/api/table/users

# Get transaction history
curl http://localhost:5000/api/history
```

### Method 3: Run the Demo

```bash
python demo.py
```

Shows all 6 features:
1. Basic CRUD operations
2. WHERE clauses (comparison operators)
3. Joins with multiple tables
4. Constraint validation
5. Ledger inspection
6. Complex real-world scenario

### Method 4: Programmatic Access

```python
from src.main import DatabaseEngine

# Initialize
db = DatabaseEngine(ledger_file='data/ledger.jsonl')

# Create table
db.execute('''
    CREATE TABLE products (
        product_id INT PRIMARY KEY,
        name TEXT UNIQUE,
        price FLOAT
    )
''')

# Insert data
db.execute("INSERT INTO products VALUES (1, 'Laptop', 999.99)")
db.execute("INSERT INTO products VALUES (2, 'Mouse', 29.99)")

# Query
result = db.execute("SELECT * FROM products WHERE price > 50.00")
print(result)
# Output: [{'product_id': 1, 'name': 'Laptop', 'price': 999.99}]

# Update
db.execute("UPDATE products SET price = 999.00 WHERE product_id = 1")

# Delete
db.execute("DELETE FROM products WHERE price < 30.00")

# View history
entries = db.ledger_store.read_all()
for entry in entries:
    print(f"{entry.operation} on {entry.table_name} at {entry.timestamp}")
```

---

## Core Concept: Ledger-Based Storage

### How It Works

Instead of updating or deleting data in-place, every operation creates an immutable ledger entry:

```json
{
  "transaction_id": 1,
  "table_name": "users",
  "operation": "INSERT",
  "timestamp": "2026-01-15T10:30:00Z",
  "old_value": null,
  "new_value": {"id": 1, "name": "Alice", "balance": 1000.00}
}
```

### State Reconstruction

The current database state is reconstructed by replaying entries:

1. **INSERT** - Add row to current state
2. **UPDATE** - Replace row in current state
3. **DELETE** - Remove row from current state

### Benefits

| Benefit | Real-World Use |
|---------|----------------|
| **Full History** | Audit trails for financial systems |
| **Traceability** | Understand when/why data changed |
| **Simple Rollback** | Remove entries, replay from ledger |
| **Debugging** | Find bugs by inspecting ledger |
| **Consistency** | Derived state is always correct |

---

## Architecture

### System Layers

```
┌─────────────────────────────┐
│      User Interface         │
│  (REPL, Web API, Demo)      │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│   Database Engine           │
│  (Parser + Executor)        │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│    Storage Layer            │
│  (Ledger + Schema + Index)  │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│    Persistence              │
│  (data/ledger.jsonl)        │
└─────────────────────────────┘
```

### Component Overview

| Component | File | Purpose |
|-----------|------|---------|
| **Lexer** | `src/parser/lexer.py` | Tokenizes SQL strings |
| **Parser** | `src/parser/parser.py` | Builds AST from tokens |
| **Executor** | `src/executor/executor.py` | Executes AST nodes |
| **Schema** | `src/storage/schema.py` | Manages table definitions |
| **Ledger** | `src/storage/ledger.py` | Persists transactions |
| **Index** | `src/index/index_manager.py` | Fast key lookups |
| **Engine** | `src/main.py` | Coordinates components |
| **REPL** | `src/repl.py` | Interactive interface |

### Data Flow

```
SQL Query
   ↓
Lexer (tokenization)
   ↓
Parser (AST construction)
   ↓
Executor (query execution)
   ↓
Validators (constraint checking)
   ↓
Ledger Store (persistence)
   ↓
Result (returned to user)
```

---

## Examples

### Example 1: Basic CRUD

```sql
-- Create
CREATE TABLE books (
  book_id INT PRIMARY KEY,
  title TEXT UNIQUE,
  author TEXT,
  price FLOAT
);

-- Create
INSERT INTO books VALUES (1, 'The Hobbit', 'Tolkien', 12.99);
INSERT INTO books VALUES (2, 'Dune', 'Herbert', 15.99);
INSERT INTO books VALUES (3, '1984', 'Orwell', 13.99);

-- Read
SELECT * FROM books WHERE price < 14.00;

-- Update
UPDATE books SET price = 11.99 WHERE title = 'The Hobbit';

-- Delete
DELETE FROM books WHERE book_id = 3;
```

### Example 2: WHERE Clauses with Operators

```sql
-- Comparison operators
SELECT * FROM books WHERE price > 10.00;         -- Greater than
SELECT * FROM books WHERE price <= 14.00;        -- Less or equal
SELECT * FROM books WHERE author = 'Tolkien';    -- Equality
SELECT * FROM books WHERE author != 'Orwell';    -- Not equal

-- AND operator (all conditions must be true)
SELECT * FROM books WHERE price > 12.00 AND author = 'Herbert';

-- OR operator (any condition can be true)
SELECT * FROM books WHERE author = 'Tolkien' OR author = 'Orwell';

-- Complex (AND has higher precedence)
SELECT * FROM books 
WHERE price > 10.00 AND author = 'Tolkien' OR price > 15.00;
-- Parsed as: (price > 10.00 AND author = 'Tolkien') OR (price > 15.00)
```

### Example 3: Joins with Multiple Tables

```sql
-- Create related tables
CREATE TABLE authors (
  author_id INT PRIMARY KEY,
  name TEXT UNIQUE,
  country TEXT
);

CREATE TABLE books (
  book_id INT PRIMARY KEY,
  title TEXT,
  author_id INT
);

-- Insert data
INSERT INTO authors VALUES (1, 'Tolkien', 'UK');
INSERT INTO authors VALUES (2, 'Herbert', 'USA');

INSERT INTO books VALUES (1, 'The Hobbit', 1);
INSERT INTO books VALUES (2, 'Dune', 2);

-- Join
SELECT books.title, authors.name, authors.country
FROM books
INNER JOIN authors ON books.author_id = authors.author_id;

-- Join with WHERE
SELECT books.title, authors.name
FROM books
INNER JOIN authors ON books.author_id = authors.author_id
WHERE authors.country = 'UK';
```

### Example 4: Constraint Validation

```sql
-- Create table with constraints
CREATE TABLE users (
  id INT PRIMARY KEY,
  email TEXT UNIQUE,
  name TEXT
);

-- Valid insert
INSERT INTO users VALUES (1, 'alice@company.com', 'Alice');  -- OK

-- Constraint violation - duplicate primary key
INSERT INTO users VALUES (1, 'bob@company.com', 'Bob');      -- ERROR

-- Constraint violation - duplicate unique value
INSERT INTO users VALUES (2, 'alice@company.com', 'Alice2'); -- ERROR

-- Valid insert
INSERT INTO users VALUES (2, 'bob@company.com', 'Bob');      -- OK
```

---

## API Reference

### REPL Commands

| Command | Effect |
|---------|--------|
| `exit` or `quit` | Exit the REPL |
| `Ctrl+C` | Cancel current query |
| `;` | End multi-line query |
| Empty line | End multi-line query |

### Python API

```python
from src.main import DatabaseEngine

db = DatabaseEngine()

# Execute any SQL statement
result = db.execute(sql_string)

# Access components
db.schema_manager         # Table schemas
db.ledger_store          # Transaction log
db.index_manager         # Key indexes
db.executor              # Query executor
```

### Web API Endpoints

**POST /api/query**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users"}'
```

**GET /api/tables**
```bash
curl http://localhost:5000/api/tables
# Returns: {"success": true, "tables": ["users", "products"]}
```

**GET /api/table/{name}**
```bash
curl http://localhost:5000/api/table/users
# Returns table schema with column info
```

**GET /api/history**
```bash
curl http://localhost:5000/api/history
# Returns last 50 ledger entries
```

---

## Documentation

### Available Docs

| Document | Location | Purpose |
|----------|----------|---------|
| **Usage Guide** | `docs/USAGE_GUIDE.md` | Complete user guide with examples |
| **Implementation Guide** | `docs/IMPLEMENTATION_GUIDE.md` | Technical architecture & design |
| **Completion Summary** | `COMPLETION_SUMMARY.md` | Project status & statistics |
| **This README** | `README.md` | Overview & quick reference |

### Quick Resources

- **Demo Script** → `python demo.py` (shows all features)
- **Test Cases** → `tests/` (usage patterns and expected behavior)
- **Code Comments** → Throughout codebase (implementation details)

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suite

```bash
pytest tests/test_parser.py -v        # Parser tests
pytest tests/test_executor.py -v      # Executor tests
pytest tests/test_integration.py -v   # Integration tests
```

### Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| Parser | 20+ | ✅ All passing |
| Executor | 10+ | ✅ All passing |
| Integration | 15+ | ✅ All passing |
| Constraints | 5+ | ✅ All passing |
| **Total** | **50+** | **✅ All passing** |

---

## Design Decisions

### What We Prioritized

✅ **Simplicity** - Code is easy to understand
✅ **Correctness** - All operations are valid and consistent
✅ **Clarity** - Design is obvious and intentional
✅ **Testability** - Components are independent and testable

### What We Excluded (Intentionally)

❌ Query optimization - Not needed for scope
❌ Concurrency control - Single-threaded is sufficient
❌ Advanced indexing - Hash maps are fast enough
❌ Distributed execution - Beyond scope

### Why Ledger-Based Storage?

Instead of overwriting data, we record changes because:

1. **Auditability** - Every change is logged permanently
2. **Consistency** - Derived state is always correct
3. **Simplicity** - No complex update-in-place logic
4. **Real-world relevance** - Financial systems use this approach
5. **Learning value** - Demonstrates alternative paradigm

---

## Limitations & Future Work

### Current Limitations

| Limitation | Why | Impact |
|-----------|-----|--------|
| Single-threaded | Simpler design | One query at a time |
| No query optimization | Beyond scope | Full table scans are OK |
| Basic persistence | Simpler code | No compression/WAL |
| Limited SQL | Learning focus | No aggregates, GROUP BY |
| No schema persistence | Simple demo | Must recreate on restart |

### Future Enhancements

With more time, we could add:

- 📌 Write-ahead logging (WAL) for crash recovery
- 📌 Query planner and optimizer
- 📌 Additional SQL features (GROUP BY, ORDER BY, LIMIT)
- 📌 Aggregation functions (COUNT, SUM, AVG, MAX, MIN)
- 📌 Transaction support (BEGIN, COMMIT, ROLLBACK)
- 📌 Additional join types (LEFT, RIGHT, OUTER)
- 📌 Schema persistence
- 📌 Multi-threaded execution with locking

---

## Project Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | 5,000+ |
| **Python Files** | 15+ |
| **Test Cases** | 50+ |
| **Documentation** | 2,500+ lines |
| **SQL Statements** | 5 types |
| **Data Types** | 5 types |
| **Operators** | 10 total |
| **API Endpoints** | 4 |
| **Time to Build** | ~6 weeks |
| **Phases Completed** | 9/9 |

---

## Contributing

### Code Style

- Follow PEP 8 conventions
- Use type hints where possible
- Add docstrings to functions
- Write tests for new features

### Adding Features

1. Create a test first
2. Implement the feature
3. Ensure all tests pass
4. Update documentation
5. Submit with clear commit message

### Reporting Issues

When reporting issues, include:

- Python version
- Full error message
- Steps to reproduce
- Expected vs actual behavior

---

## FAQ

### How do I clear all data?

```bash
rm data/ledger.jsonl
```

The database will start fresh next time.

### Can I use this in production?

No. LedgerLite is designed for learning and demonstration. Use a production database system instead.

### What's the maximum table size?

No hard limit, but performance degrades as the ledger grows. For learning/demo purposes, 10,000 rows is fine.

### How do I export data?

Query the data and save results:

```bash
# In REPL
SELECT * FROM users;
```

Then copy results, or write a Python script to export to CSV.

### Is it thread-safe?

No. LedgerLite is single-threaded and not designed for concurrent access.

### Can I update a primary key?

No. Instead, delete the row and insert a new one with the new key.

---

## License

This project is provided as-is for educational purposes.

---

## Author

**kanew**

Built for: **Pesapal Junior Developer Challenge 2026**

---

## Closing Note

LedgerLite demonstrates how databases **behave**, not just how they store data. Every feature choice is intentional, every limitation is acknowledged, and every design decision is justified.

It's designed to teach:

- 🎓 Database fundamentals
- 🎓 Software architecture
- 🎓 System design thinking
- 🎓 Code quality and testing
- 🎓 Clear communication through documentation

**Start here:** `python demo.py`

**Learn more:** See `docs/USAGE_GUIDE.md` for comprehensive guide.

**Explore code:** Start with `src/main.py` to understand the architecture.

---

**LedgerLite: Clear thinking. Intentional design. Educational value.** 🚀
