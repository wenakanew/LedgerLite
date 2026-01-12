# LedgerLite Quick Start Guide

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd LedgerLite
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the REPL

Start the interactive REPL:

```bash
python -m src.main
```

Or directly:

```bash
python -m src.repl
```

### Example REPL Session

```
ledgerlite> CREATE TABLE users (id INT PRIMARY KEY, name TEXT, email TEXT UNIQUE);
Table 'users' created successfully

ledgerlite> INSERT INTO users VALUES (1, 'Alice', 'alice@example.com');
(1 row affected)

ledgerlite> INSERT INTO users VALUES (2, 'Bob', 'bob@example.com');
(1 row affected)

ledgerlite> SELECT * FROM users;
id | name | email
--------------
1  | Alice | alice@example.com
2  | Bob   | bob@example.com

(2 row(s))

ledgerlite> SELECT * FROM users WHERE id = 1;
id | name | email
--------------
1  | Alice | alice@example.com

(1 row(s))

ledgerlite> UPDATE users SET name = 'Alice Smith' WHERE id = 1;
(1 row affected)

ledgerlite> DELETE FROM users WHERE id = 2;
(1 row affected)

ledgerlite> exit
Goodbye!
```

## Running the Web Application

1. **Start the Flask server:**
   ```bash
   cd web
   python app.py
   ```

   Or from the project root:
   ```bash
   python web/app.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Use the web interface:**
   - Enter SQL queries in the text area
   - Click "Execute Query" or press Ctrl+Enter
   - View results, tables, and transaction history

## Example Queries

### Create a Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    balance FLOAT
);
```

### Insert Data
```sql
INSERT INTO users VALUES (1, 'Alice', 'alice@example.com', 100.50);
INSERT INTO users VALUES (2, 'Bob', 'bob@example.com', 250.75);
```

### Query Data
```sql
-- Select all
SELECT * FROM users;

-- Select with WHERE
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE balance > 150;

-- Select specific columns
SELECT name, email FROM users;
```

### Update Data
```sql
UPDATE users SET balance = 200.00 WHERE id = 1;
UPDATE users SET name = 'Alice Smith', balance = 150.00 WHERE id = 1;
```

### Delete Data
```sql
DELETE FROM users WHERE id = 2;
DELETE FROM users WHERE balance < 100;
```

### Joins
```sql
-- Create a second table
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    user_id INT,
    amount FLOAT,
    description TEXT
);

-- Insert some transactions
INSERT INTO transactions VALUES (1, 1, 50.00, 'Purchase');
INSERT INTO transactions VALUES (2, 1, 25.00, 'Refund');

-- Join tables
SELECT users.name, transactions.amount, transactions.description
FROM users
INNER JOIN transactions
ON users.id = transactions.user_id;
```

## Data Persistence

Data is persisted in `data/ledger.jsonl`. Each data modification creates a ledger entry. The current database state is reconstructed by replaying these entries.

You can inspect the ledger file to see the full transaction history:

```bash
cat data/ledger.jsonl
```

## Troubleshooting

### Import Errors
Make sure you're in the project root directory and the virtual environment is activated.

### Port Already in Use (Web App)
If port 5000 is in use, modify `web/app.py` to use a different port:

```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Data Not Persisting
Ensure the `data/` directory exists and is writable. The ledger file will be created automatically on first use.

## Next Steps

- Explore the codebase in `src/`
- Read the [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)
- Review the [Challenge Evaluation](docs/CHALLENGE_EVALUATION.md)
- Check out the test files in `tests/`
