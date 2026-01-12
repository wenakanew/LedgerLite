#!/usr/bin/env python
"""
LedgerLite Demo Script

This script demonstrates all major features of LedgerLite:
- Table creation with constraints
- CRUD operations (Create, Read, Update, Delete)
- WHERE clauses with comparison and logical operators
- Joins with multiple tables
- Ledger inspection and transaction history

Run with: python demo.py
"""

import tempfile
import os
import json
from src.main import DatabaseEngine


def print_header(text):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_subheader(text):
    """Print a formatted subsection header."""
    print(f"\n{text}")
    print("-" * 70)


def execute_query(db, query):
    """Execute a query and display results."""
    try:
        result = db.execute(query)
        
        if isinstance(result, list):
            if not result:
                print("(0 rows)\n")
            else:
                # Display as table
                headers = list(result[0].keys())
                col_widths = {h: len(str(h)) for h in headers}
                for row in result:
                    for h in headers:
                        col_widths[h] = max(col_widths[h], len(str(row.get(h, ""))))
                
                # Header
                header_parts = [str(h).ljust(col_widths[h]) for h in headers]
                print(" | ".join(header_parts))
                print("-" * len(" | ".join(header_parts)))
                
                # Rows
                for row in result:
                    row_parts = [str(row.get(h, "")).ljust(col_widths[h]) for h in headers]
                    print(" | ".join(row_parts))
                
                print(f"\n({len(result)} row(s))\n")
        else:
            print(result + "\n")
    except Exception as e:
        print(f"ERROR: {e}\n")


def demo_basic_crud(db):
    """Demonstrate basic CRUD operations."""
    print_header("1. Basic CRUD Operations")
    
    print_subheader("CREATE TABLE")
    print("Creating 'employees' table with constraints...")
    execute_query(db, """
        CREATE TABLE employees (
            emp_id INT PRIMARY KEY,
            name TEXT UNIQUE,
            email TEXT UNIQUE,
            salary FLOAT
        )
    """)
    
    print_subheader("INSERT")
    print("Inserting 3 employee records...")
    execute_query(db, "INSERT INTO employees VALUES (1, 'Alice Johnson', 'alice@company.com', 75000.00)")
    execute_query(db, "INSERT INTO employees VALUES (2, 'Bob Smith', 'bob@company.com', 65000.00)")
    execute_query(db, "INSERT INTO employees VALUES (3, 'Charlie Brown', 'charlie@company.com', 55000.00)")
    
    print_subheader("SELECT")
    print("Retrieving all employees...")
    execute_query(db, "SELECT * FROM employees")
    
    print("Selecting specific columns...")
    execute_query(db, "SELECT name, salary FROM employees")
    
    print_subheader("UPDATE")
    print("Giving Alice a $10,000 raise...")
    execute_query(db, "UPDATE employees SET salary = 85000.00 WHERE emp_id = 1")
    
    print("Verifying the update...")
    execute_query(db, "SELECT * FROM employees WHERE emp_id = 1")
    
    print_subheader("DELETE")
    print("Removing Charlie from the system...")
    execute_query(db, "DELETE FROM employees WHERE emp_id = 3")
    
    print("Verifying deletion...")
    execute_query(db, "SELECT * FROM employees")


def demo_where_operators(db):
    """Demonstrate WHERE clauses with various operators."""
    print_header("2. WHERE Clauses & Operators")
    
    print_subheader("Comparison Operators")
    
    print("Find employees earning more than $60,000...")
    execute_query(db, "SELECT name, salary FROM employees WHERE salary > 60000.00")
    
    print("Find employees earning exactly $65,000...")
    execute_query(db, "SELECT name, salary FROM employees WHERE salary = 65000.00")
    
    print("Find employees NOT named Alice...")
    execute_query(db, "SELECT name FROM employees WHERE name != 'Alice Johnson'")
    
    print_subheader("Logical Operators - AND")
    
    print("Find employees earning between $60k and $80k (using AND)...")
    execute_query(db, "SELECT * FROM employees WHERE salary >= 60000.00 AND salary <= 80000.00")
    
    print_subheader("Logical Operators - OR")
    
    print("Find Alice OR Bob...")
    execute_query(db, "SELECT * FROM employees WHERE name = 'Alice Johnson' OR name = 'Bob Smith'")
    
    print_subheader("Complex Conditions - AND/OR Precedence")
    
    print("Find employees earning > $70k AND named Alice OR anyone earning > $80k...")
    print("(Note: AND has higher precedence, so this is: (salary > 70000 AND name = 'Alice') OR (salary > 80000))")
    execute_query(db, "SELECT name, salary FROM employees WHERE salary > 70000.00 AND name = 'Alice Johnson' OR salary > 80000.00")


def demo_joins(db):
    """Demonstrate JOIN operations."""
    print_header("3. Joins with Multiple Tables")
    
    print_subheader("Create Additional Tables")
    
    print("Creating 'departments' table...")
    execute_query(db, """
        CREATE TABLE departments (
            dept_id INT PRIMARY KEY,
            dept_name TEXT UNIQUE
        )
    """)
    
    print("Creating 'assignments' table to link employees to departments...")
    execute_query(db, """
        CREATE TABLE assignments (
            assign_id INT PRIMARY KEY,
            emp_id INT,
            dept_id INT
        )
    """)
    
    print_subheader("Insert Department Data")
    execute_query(db, "INSERT INTO departments VALUES (1, 'Engineering')")
    execute_query(db, "INSERT INTO departments VALUES (2, 'Sales')")
    execute_query(db, "INSERT INTO departments VALUES (3, 'HR')")
    
    print_subheader("Assign Employees to Departments")
    execute_query(db, "INSERT INTO assignments VALUES (1, 1, 1)")  # Alice -> Engineering
    execute_query(db, "INSERT INTO assignments VALUES (2, 2, 2)")  # Bob -> Sales
    
    print_subheader("INNER JOIN Query")
    print("Find all employees and their departments...")
    execute_query(db, """
        SELECT employees.name, departments.dept_name
        FROM employees
        INNER JOIN assignments ON employees.emp_id = assignments.emp_id
        INNER JOIN departments ON assignments.dept_id = departments.dept_id
    """)
    
    print_subheader("JOIN with WHERE")
    print("Find employees in the Engineering department...")
    execute_query(db, """
        SELECT employees.name, departments.dept_name
        FROM employees
        INNER JOIN assignments ON employees.emp_id = assignments.emp_id
        INNER JOIN departments ON assignments.dept_id = departments.dept_id
        WHERE departments.dept_name = 'Engineering'
    """)


def demo_constraints(db):
    """Demonstrate constraint validation."""
    print_header("4. Constraint Validation")
    
    print_subheader("Primary Key Uniqueness")
    print("Attempting to insert duplicate employee ID...")
    print("Expected: ERROR - Primary key already exists")
    execute_query(db, "INSERT INTO employees VALUES (1, 'Duplicate', 'dup@company.com', 50000.00)")
    
    print_subheader("Unique Column Constraint")
    print("Attempting to insert employee with duplicate name...")
    print("Expected: ERROR - Unique constraint violation")
    execute_query(db, "INSERT INTO employees VALUES (4, 'Alice Johnson', 'new@company.com', 60000.00)")
    
    print_subheader("Type Validation")
    print("Attempting to insert non-numeric salary...")
    print("Expected: ERROR - Type validation failure")
    execute_query(db, "INSERT INTO employees VALUES (4, 'David', 'david@company.com', 'expensive')")


def demo_ledger_inspection(db):
    """Demonstrate ledger inspection capabilities."""
    print_header("5. Ledger Inspection & Transaction History")
    
    print_subheader("View Raw Ledger Entries")
    print("Last 3 ledger entries (prettified):\n")
    
    try:
        entries = db.ledger_store.read_all()
        for entry in entries[-3:]:
            data = {
                "transaction_id": entry.transaction_id,
                "table_name": entry.table_name,
                "operation": entry.operation.value,
                "timestamp": entry.timestamp,
                "old_value": entry.old_value,
                "new_value": entry.new_value
            }
            print(json.dumps(data, indent=2))
            print()
    except Exception as e:
        print(f"Error reading ledger: {e}\n")


def demo_complex_scenario(db):
    """Demonstrate a complex real-world scenario."""
    print_header("6. Complex Real-World Scenario: Product Sales Tracking")
    
    print_subheader("Setup")
    
    print("Creating 'products' table...")
    execute_query(db, """
        CREATE TABLE products (
            product_id INT PRIMARY KEY,
            product_name TEXT UNIQUE,
            category TEXT,
            price FLOAT
        )
    """)
    
    print("Creating 'sales' table...")
    execute_query(db, """
        CREATE TABLE sales (
            sale_id INT PRIMARY KEY,
            product_id INT,
            quantity INT,
            sale_price FLOAT
        )
    """)
    
    print_subheader("Insert Sample Data")
    
    print("Adding products...")
    execute_query(db, "INSERT INTO products VALUES (1, 'Laptop', 'Electronics', 999.99)")
    execute_query(db, "INSERT INTO products VALUES (2, 'Mouse', 'Electronics', 29.99)")
    execute_query(db, "INSERT INTO products VALUES (3, 'Desk', 'Furniture', 299.99)")
    execute_query(db, "INSERT INTO products VALUES (4, 'Chair', 'Furniture', 199.99)")
    
    print("Recording sales...")
    execute_query(db, "INSERT INTO sales VALUES (1, 1, 1, 999.99)")   # Sold 1 Laptop
    execute_query(db, "INSERT INTO sales VALUES (2, 2, 5, 29.99)")    # Sold 5 Mice
    execute_query(db, "INSERT INTO sales VALUES (3, 3, 1, 299.99)")   # Sold 1 Desk
    execute_query(db, "INSERT INTO sales VALUES (4, 4, 2, 199.99)")   # Sold 2 Chairs
    execute_query(db, "INSERT INTO sales VALUES (5, 1, 1, 899.99)")   # Sold 1 Laptop (discounted)
    
    print_subheader("Complex Queries")
    
    print("Find all electronics that were sold...")
    execute_query(db, """
        SELECT DISTINCT products.product_name, products.category
        FROM products
        INNER JOIN sales ON products.product_id = sales.product_id
        WHERE products.category = 'Electronics'
    """)
    
    print("Find high-value sales (price > $100)...")
    execute_query(db, """
        SELECT products.product_name, sales.quantity, sales.sale_price
        FROM products
        INNER JOIN sales ON products.product_id = sales.product_id
        WHERE sales.sale_price > 100.00
    """)
    
    print("Find products in Electronics category OR furniture under $250...")
    execute_query(db, """
        SELECT * FROM products
        WHERE category = 'Electronics' OR (category = 'Furniture' AND price < 250.00)
    """)


def main():
    """Run the complete demo."""
    print("\n" + "=" * 70)
    print("  LEDGERLITE COMPREHENSIVE DEMO")
    print("  A Transaction-First Mini Relational Database System")
    print("=" * 70)
    
    # Create temporary ledger file for demo
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        ledger_file = f.name
    
    try:
        # Initialize database
        db = DatabaseEngine(ledger_file=ledger_file)
        
        # Run demos
        demo_basic_crud(db)
        demo_where_operators(db)
        demo_joins(db)
        demo_constraints(db)
        demo_ledger_inspection(db)
        demo_complex_scenario(db)
        
        # Summary
        print_header("Demo Complete!")
        print("""
LedgerLite successfully demonstrated:

✓ Table creation with PRIMARY KEY and UNIQUE constraints
✓ CRUD operations (CREATE, INSERT, SELECT, UPDATE, DELETE)
✓ WHERE clauses with comparison operators (=, !=, >, <, >=, <=)
✓ Logical operators (AND, OR) with proper precedence
✓ INNER JOIN operations with multiple tables
✓ Constraint validation and error handling
✓ Ledger inspection and transaction tracking
✓ Complex real-world scenarios

For more information, see:
  - docs/USAGE_GUIDE.md - Comprehensive usage guide with examples
  - docs/IMPLEMENTATION_GUIDE.md - Technical architecture and design
  - README.md - Project overview and features

To start the interactive REPL:
  python -m src.main

To start the web application:
  python web/app.py
""")
    
    finally:
        # Cleanup
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


if __name__ == "__main__":
    main()
