# LedgerLite Usage Guide

A comprehensive guide to using LedgerLite, a transaction-first relational database system with full auditability through ledger-based storage.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [SQL Operations](#sql-operations)
3. [WHERE Clauses & Operators](#where-clauses--operators)
4. [Joins](#joins)
5. [Constraints](#constraints)
6. [Data Types](#data-types)
7. [REPL Interface](#repl-interface)
8. [Web Application](#web-application)
9. [Advanced Features](#advanced-features)
10. [FAQ](#faq)

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository_url>
cd LedgerLite

# Install dependencies
pip install -r requirements.txt
```

### Running the REPL

```bash
python -m src.main
```

You'll see:

```
============================================================
LedgerLite - A Transaction-First Mini Relational Database
Version 0.1.0
============================================================

Commands:
  - Type SQL queries to execute
  - End queries with semicolon (;) or press Enter twice
  - Type 'exit' or 'quit' to exit
  - Press Ctrl+C to cancel current query

------------------------------------------------------------

ledgerlite> 
```

### First Query

```sql
ledgerlite> CREATE TABLE users (
...         id INT PRIMARY KEY,
...         name TEXT UNIQUE,
...         age INT
...         );
Table 'users' created successfully

ledgerlite> INSERT INTO users VALUES (1, 'Alice', 30);
1 row inserted into 'users'

ledgerlite> SELECT * FROM users;
id | name  | age
-- | ----- | ---
1  | Alice | 30

(1 row(s))
```

---

## SQL Operations

### CREATE TABLE

Define a table with columns and constraints.

**Syntax:**
```sql
CREATE TABLE table_name (
    column_name DataType [PRIMARY KEY] [UNIQUE],
    ...
);
```

**Supported Data Types:**
- `INT` - Integer values
- `TEXT` - Text/string values
- `FLOAT` - Floating-point numbers
- `BOOLEAN` - True/false values
- `TIMESTAMP` - Date/time values (stored as strings)

**Example:**
```sql
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name TEXT UNIQUE,
    email TEXT UNIQUE,
    salary FLOAT,
    active BOOLEAN
);
```

**Constraints:**
- `PRIMARY KEY` - Uniquely identifies each row (required, only one per table)
- `UNIQUE` - Ensures all values in column are unique

### INSERT

Add new rows to a table.

**Syntax:**
```sql
INSERT INTO table_name VALUES (value1, value2, ...);
```

**Rules:**
- Values must match column order and data types
- Primary key must be unique
- Unique column values must not conflict
- Column count must match table definition

**Examples:**
```sql
INSERT INTO employees VALUES (1, 'Alice Johnson', 'alice@company.com', 75000.00, TRUE);
INSERT INTO employees VALUES (2, 'Bob Smith', 'bob@company.com', 65000.00, TRUE);
INSERT INTO employees VALUES (3, 'Charlie Brown', 'charlie@company.com', 55000.00, FALSE);
```

### SELECT

Retrieve data from tables.

**Syntax:**
```sql
SELECT column_list | * FROM table_name [WHERE condition] [JOIN ...];
```

**Examples:**

**All columns:**
```sql
SELECT * FROM employees;
```

**Specific columns:**
```sql
SELECT name, salary FROM employees;
```

**With WHERE clause:**
```sql
SELECT * FROM employees WHERE active = TRUE;
SELECT * FROM employees WHERE salary > 60000.00;
```

### UPDATE

Modify existing rows.

**Syntax:**
```sql
UPDATE table_name SET column = value [, column = value ...] [WHERE condition];
```

**Examples:**

**Update specific rows:**
```sql
UPDATE employees SET salary = 80000.00 WHERE emp_id = 1;
UPDATE employees SET active = FALSE WHERE salary < 50000.00;
```

**Update all rows (no WHERE clause):**
```sql
UPDATE employees SET active = TRUE;
```

### DELETE

Remove rows from a table.

**Syntax:**
```sql
DELETE FROM table_name [WHERE condition];
```

**Examples:**

**Delete specific rows:**
```sql
DELETE FROM employees WHERE emp_id = 3;
DELETE FROM employees WHERE active = FALSE;
```

**Delete all rows (no WHERE clause):**
```sql
DELETE FROM employees;
```

---

## WHERE Clauses & Operators

### Comparison Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=` | Equal to | `age = 30` |
| `!=` | Not equal to | `age != 30` |
| `>` | Greater than | `salary > 50000.00` |
| `<` | Less than | `salary < 100000.00` |
| `>=` | Greater or equal | `age >= 18` |
| `<=` | Less or equal | `age <= 65` |

### Logical Operators

#### AND

Both conditions must be true.

```sql
-- Find active employees with salary > 60000
SELECT * FROM employees WHERE active = TRUE AND salary > 60000.00;

-- Multiple AND conditions
SELECT * FROM employees WHERE active = TRUE AND salary > 50000.00 AND name = 'Alice Johnson';
```

#### OR

Either condition must be true.

```sql
-- Find employees named Alice or Bob
SELECT * FROM employees WHERE name = 'Alice Johnson' OR name = 'Bob Smith';

-- Employees who are inactive OR have low salary
SELECT * FROM employees WHERE active = FALSE OR salary < 40000.00;
```

#### Mixed AND/OR

AND has higher precedence than OR. Use carefully!

```sql
-- Find active employees earning > 60k OR anyone earning > 100k
-- Parsed as: (active = TRUE AND salary > 60000) OR (salary > 100000)
SELECT * FROM employees WHERE active = TRUE AND salary > 60000.00 OR salary > 100000.00;
```

### Examples

```sql
-- Find high-earning active employees
SELECT name, salary FROM employees 
WHERE active = TRUE AND salary > 70000.00;

-- Find employees with specific names
SELECT * FROM employees 
WHERE name = 'Alice Johnson' OR name = 'Bob Smith' OR name = 'Charlie Brown';

-- Complex condition
SELECT * FROM employees
WHERE (active = TRUE AND salary >= 60000.00) OR (active = FALSE AND salary >= 40000.00);
```

---

## Joins

### INNER JOIN

Returns rows where join condition matches.

**Syntax:**
```sql
SELECT columns FROM table1
INNER JOIN table2 ON table1.column = table2.column;
```

**Example Setup:**
```sql
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name TEXT
);

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name TEXT,
    dept_id INT
);

INSERT INTO departments VALUES (1, 'Engineering');
INSERT INTO departments VALUES (2, 'Sales');

INSERT INTO employees VALUES (1, 'Alice', 1);
INSERT INTO employees VALUES (2, 'Bob', 2);
INSERT INTO employees VALUES (3, 'Charlie', 1);
```

**Join Query:**
```sql
SELECT employees.name, departments.dept_name
FROM employees
INNER JOIN departments ON employees.dept_id = departments.dept_id;
```

**Result:**
```
name    | dept_name
--------|----------
Alice   | Engineering
Bob     | Sales
Charlie | Engineering

(3 row(s))
```

### Multiple Joins

Chain joins together:

```sql
SELECT employees.name, departments.dept_name, projects.project_name
FROM employees
INNER JOIN departments ON employees.dept_id = departments.dept_id
INNER JOIN projects ON employees.emp_id = projects.emp_id;
```

### Combining JOINs with WHERE

```sql
-- Find employees in Engineering earning > 70000
SELECT employees.name, departments.dept_name, employees.salary
FROM employees
INNER JOIN departments ON employees.dept_id = departments.dept_id
WHERE departments.dept_name = 'Engineering' AND employees.salary > 70000.00;
```

---

## Constraints

### Primary Key Constraint

Every table **requires** a primary key. It must be:
- Unique across all rows
- Not NULL
- Only one per table

**Violating Primary Key:**
```sql
INSERT INTO users VALUES (1, 'Alice');
INSERT INTO users VALUES (1, 'Bob');  -- ERROR: Primary key already exists!
```

### Unique Constraint

Values in a UNIQUE column must be distinct (NULL values allowed).

**Setup:**
```sql
CREATE TABLE accounts (
    account_id INT PRIMARY KEY,
    email TEXT UNIQUE,
    username TEXT UNIQUE
);
```

**Violating Unique:**
```sql
INSERT INTO accounts VALUES (1, 'alice@company.com', 'alice');
INSERT INTO accounts VALUES (2, 'alice@company.com', 'alice2');  -- ERROR: email already exists!
INSERT INTO accounts VALUES (2, 'bob@company.com', 'alice');  -- ERROR: username already exists!
```

**NULL Handling:**
```sql
-- This is allowed - multiple NULLs don't violate UNIQUE
INSERT INTO accounts VALUES (1, NULL, 'alice');
INSERT INTO accounts VALUES (2, NULL, 'bob');  -- OK
```

### Type Validation

All values are validated against their column type.

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name TEXT,
    price FLOAT
);

INSERT INTO products VALUES (1, 'Laptop', 999.99);  -- OK
INSERT INTO products VALUES (2, 'Mouse', 'expensive');  -- ERROR: 'expensive' is not a FLOAT!
```

---

## Data Types

### INT

Integer values (whole numbers).

```sql
CREATE TABLE items (id INT PRIMARY KEY, quantity INT);
INSERT INTO items VALUES (1, 100);
INSERT INTO items VALUES (2, -50);  -- Negative OK
```

### TEXT

Text/string values.

```sql
CREATE TABLE users (id INT PRIMARY KEY, name TEXT);
INSERT INTO users VALUES (1, 'Alice Johnson');
INSERT INTO users VALUES (2, 'Bob');
```

### FLOAT

Floating-point numbers (decimals).

```sql
CREATE TABLE products (id INT PRIMARY KEY, price FLOAT);
INSERT INTO products VALUES (1, 19.99);
INSERT INTO products VALUES (2, 100.00);
```

### BOOLEAN

True/false values.

```sql
CREATE TABLE features (id INT PRIMARY KEY, enabled BOOLEAN);
INSERT INTO features VALUES (1, TRUE);
INSERT INTO features VALUES (2, FALSE);
```

### TIMESTAMP

Date/time values (stored as strings).

```sql
CREATE TABLE events (id INT PRIMARY KEY, event_time TIMESTAMP);
INSERT INTO events VALUES (1, '2026-01-15T10:30:00Z');
INSERT INTO events VALUES (2, '2026-01-16T14:45:00Z');
```

---

## REPL Interface

### Basic Commands

**Execute a query:**
```
ledgerlite> SELECT * FROM users;
```

**Multi-line queries:**
```
ledgerlite> SELECT id, name
...         FROM users
...         WHERE age > 25;
```

**End query with semicolon or blank line:**
```
ledgerlite> UPDATE users SET age = 31 WHERE id = 1;
```

**Exit:**
```
ledgerlite> exit
```

or

```
ledgerlite> quit
```

### Keyboard Shortcuts

- `Ctrl+C` - Cancel current query
- `Ctrl+D` - Exit REPL

### Result Display

Query results are displayed in table format:

```
id | name  | age
-- | ----- | ---
1  | Alice | 30
2  | Bob   | 25

(2 row(s))
```

Write operations show message:
```
1 row inserted into 'users'
3 row(s) updated in 'table_name'
2 row(s) deleted from 'table_name'
```

---

## Web Application

### Starting the Server

```bash
python web/app.py
```

Server runs on `http://localhost:5000`

### API Endpoints

#### POST /api/query

Execute a SQL query.

**Request:**
```json
{
  "query": "SELECT * FROM users WHERE age > 25"
}
```

**Response:**
```json
{
  "success": true,
  "result": [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 3, "name": "Charlie", "age": 35}
  ],
  "type": "rows",
  "row_count": 2
}
```

#### GET /api/tables

List all tables in database.

**Response:**
```json
{
  "success": true,
  "tables": ["users", "products", "orders"]
}
```

#### GET /api/table/<table_name>

Get table schema information.

**Request:** `GET /api/table/users`

**Response:**
```json
{
  "success": true,
  "table": {
    "name": "users",
    "columns": [
      {"name": "id", "type": "INT", "primary_key": true, "unique": false},
      {"name": "name", "type": "TEXT", "primary_key": false, "unique": true},
      {"name": "age", "type": "INT", "primary_key": false, "unique": false}
    ]
  }
}
```

#### GET /api/history

Get transaction history (last 50 entries).

**Response:**
```json
{
  "success": true,
  "entries": [
    {
      "transaction_id": 1,
      "table_name": "users",
      "operation": "INSERT",
      "timestamp": "2026-01-15T10:30:00.123456Z",
      "old_value": null,
      "new_value": {"id": 1, "name": "Alice", "age": 30}
    }
  ]
}
```

---

## Advanced Features

### Ledger Inspection

Every data change is recorded in the ledger. The ledger is stored in `data/ledger.jsonl`.

**View raw ledger entries:**
```bash
cat data/ledger.jsonl | python -m json.tool
```

Each line contains:
```json
{
  "transaction_id": 1,
  "table_name": "users",
  "operation": "INSERT",
  "timestamp": "2026-01-15T10:30:00Z",
  "old_value": null,
  "new_value": {"id": 1, "name": "Alice", "age": 30}
}
```

### Ledger Replay

When the database starts, it reconstructs the current state by replaying the ledger:

1. All INSERTs are applied first
2. UPDATEs modify existing rows
3. DELETEs remove rows
4. Final state is current database state

### Indexing

Primary key and unique columns are automatically indexed for fast lookups. This is transparent to users - queries automatically use indexes when available.

### Performance Considerations

- State reconstruction is O(n) where n = number of ledger entries
- Lookups use indexes and are O(1) average case
- JOINs use nested-loop algorithm, O(n*m)
- WHERE filtering is O(n) or better with indexes

---

## FAQ

### How do I clear all data?

Delete the `data/ledger.jsonl` file:

```bash
rm data/ledger.jsonl
```

The database will start fresh next time.

### Can I have multiple primary keys?

No, each table can have **exactly one** primary key. If you need multiple unique columns, use UNIQUE constraints instead.

### Can primary keys be NULL?

No, primary keys cannot be NULL. This is enforced at validation time.

### How do I update a primary key?

You cannot update a primary key. Instead, DELETE the row and INSERT a new one:

```sql
-- Instead of: UPDATE users SET id = 2 WHERE id = 1;
DELETE FROM users WHERE id = 1;
INSERT INTO users VALUES (2, 'Alice', 30);
```

### How do backups work?

The entire database is in the `data/ledger.jsonl` file. To backup:

```bash
cp data/ledger.jsonl data/ledger.jsonl.backup
```

To restore:

```bash
cp data/ledger.jsonl.backup data/ledger.jsonl
```

### Can I export data to CSV?

You can query the data and manually convert:

```sql
SELECT * FROM users;
```

Then copy-paste results, or write a Python script to export.

### What happens if I get a constraint violation error?

The operation is rolled back - no data is written. Try again with valid data. Common causes:

- Duplicate primary key value
- Duplicate value in UNIQUE column
- Wrong data type
- Too many/few values in INSERT

### Can tables be dropped?

Not yet. You must clear the ledger file and restart the database.

### How do I see transaction history?

Use the web API endpoint:
```
GET /api/history
```

Or inspect the ledger file directly:
```bash
tail -n 10 data/ledger.jsonl
```

### Is LedgerLite thread-safe?

No, LedgerLite is single-threaded. It's designed for learning and demonstration, not production use.

### What's the maximum table size?

There's no hard limit, but performance degrades as the ledger grows (reconstruction is O(n)). Consider archiving old data.

---

## Examples

### Example 1: Basic CRUD

```sql
-- Create table
CREATE TABLE books (
    book_id INT PRIMARY KEY,
    title TEXT UNIQUE,
    author TEXT,
    price FLOAT
);

-- Insert data
INSERT INTO books VALUES (1, 'The Hobbit', 'Tolkien', 12.99);
INSERT INTO books VALUES (2, 'Dune', 'Herbert', 15.99);
INSERT INTO books VALUES (3, '1984', 'Orwell', 13.99);

-- Read data
SELECT * FROM books WHERE price < 14.00;

-- Update data
UPDATE books SET price = 11.99 WHERE title = 'The Hobbit';

-- Delete data
DELETE FROM books WHERE book_id = 3;
```

### Example 2: Complex Query with Joins

```sql
CREATE TABLE authors (
    author_id INT PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE books (
    book_id INT PRIMARY KEY,
    title TEXT UNIQUE,
    author_id INT
);

CREATE TABLE reviews (
    review_id INT PRIMARY KEY,
    book_id INT,
    rating INT
);

-- Insert data
INSERT INTO authors VALUES (1, 'Tolkien');
INSERT INTO authors VALUES (2, 'Herbert');

INSERT INTO books VALUES (1, 'The Hobbit', 1);
INSERT INTO books VALUES (2, 'Dune', 2);

INSERT INTO reviews VALUES (1, 1, 5);
INSERT INTO reviews VALUES (2, 1, 4);
INSERT INTO reviews VALUES (3, 2, 5);

-- Complex query with joins
SELECT books.title, authors.name, reviews.rating
FROM books
INNER JOIN authors ON books.author_id = authors.author_id
INNER JOIN reviews ON books.book_id = reviews.book_id
WHERE reviews.rating >= 4;
```

### Example 3: AND/OR Operators

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name TEXT,
    category TEXT,
    price FLOAT,
    in_stock BOOLEAN
);

INSERT INTO products VALUES (1, 'Laptop', 'Electronics', 999.99, TRUE);
INSERT INTO products VALUES (2, 'Mouse', 'Electronics', 29.99, TRUE);
INSERT INTO products VALUES (3, 'Desk', 'Furniture', 299.99, FALSE);
INSERT INTO products VALUES (4, 'Chair', 'Furniture', 199.99, TRUE);

-- Find electronics under $100 that are in stock
SELECT * FROM products
WHERE category = 'Electronics' AND price < 100.00 AND in_stock = TRUE;

-- Find products in Electronics OR under $50
SELECT * FROM products
WHERE category = 'Electronics' OR price < 50.00;

-- Complex: (Electronics AND in_stock) OR (Furniture AND under $200)
SELECT * FROM products
WHERE category = 'Electronics' AND in_stock = TRUE OR category = 'Furniture' AND price < 200.00;
```

---

## Getting Help

For issues or questions:

1. Check this guide first
2. Review example queries above
3. Check error messages - they're descriptive
4. Look at test files for usage patterns: `tests/`

---
