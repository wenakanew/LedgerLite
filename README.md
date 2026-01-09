# LedgerLite

*A Transaction-First Mini Relational Database System*

---

## Overview

**LedgerLite** is a lightweight relational database management system (RDBMS) built from scratch with a focus on **correctness, traceability, and clarity of design**.

Rather than mutating data in place, LedgerLite records **every data change as an immutable ledger entry**. The current state of the database is derived from these entries. This design is inspired by real-world financial and transactional systems where **auditability and consistency** are essential.

The project was built as part of the **Pesapal Junior Developer Challenge 2026** and aims to demonstrate solid understanding of database fundamentals, system design, and practical engineering trade-offs.

---

## Project Goals

* Demonstrate understanding of relational databases
* Implement a usable SQL-like interface
* Explore ledger-based data storage
* Balance simplicity with real-world relevance
* Build a system that is easy to inspect, reason about, and extend

The goal is not performance or completeness, but **clear thinking and intentional design**.

---

## Core Idea: Ledger-Based Storage

In LedgerLite, data is never overwritten or destroyed.

Every `INSERT`, `UPDATE`, or `DELETE` operation creates a **ledger entry** describing what changed and when it changed. The current database state is reconstructed by replaying these entries.

This approach provides:

* Full change history
* Natural audit trails
* Simple rollback capability
* Easier debugging and inspection

Data changes are treated as **facts**, not mutations.

---

## Features

### SQL-Like Query Interface

LedgerLite supports a simplified SQL-inspired syntax for interacting with the database.

Supported commands include:

* `CREATE TABLE`
* `INSERT`
* `SELECT`
* `UPDATE`
* `DELETE`

Example:

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email TEXT UNIQUE,
  balance FLOAT
);

INSERT INTO users VALUES (1, 'user@mail.com', 500.00);
SELECT * FROM users;
```

---

### Relational Data Model

* Structured tables with fixed schemas
* Strongly typed columns
* Row-based storage model

#### Supported Data Types

* `INT`
* `TEXT`
* `FLOAT`
* `BOOLEAN`
* `TIMESTAMP`

---

### Constraints

LedgerLite enforces basic data integrity rules:

* `PRIMARY KEY`
* `UNIQUE` constraints

All constraints are validated during write operations.

---

### CRUD Operations

Full support for:

* Create (`INSERT`)
* Read (`SELECT`)
* Update (`UPDATE`)
* Delete (`DELETE`)

All write operations generate ledger records.

---

### Basic Indexing

To avoid full table scans:

* Primary and unique keys are indexed
* Indexes map key values to internal record identifiers

This improves lookup performance and demonstrates indexing fundamentals.

---

### Joins

LedgerLite supports basic `INNER JOIN` operations between tables.

Example:

```sql
SELECT users.email, transactions.amount
FROM users
INNER JOIN transactions
ON users.id = transactions.user_id;
```

---

### Interactive REPL

An interactive **Read–Eval–Print Loop** allows users to:

* Define tables
* Execute queries
* Inspect results
* Experiment with the database engine

The REPL serves as both a developer tool and a learning interface.

---

## Ledger System

Each data-modifying operation produces a ledger entry containing:

* Transaction ID
* Table name
* Operation type
* Previous value (if applicable)
* New value
* Timestamp

Because of this:

* Data history is preserved
* Mistakes can be traced
* Rollbacks are possible

---

## Demo Web Application

LedgerLite includes a simple web application to demonstrate real-world usage.

### Purpose

A minimal admin-style app that:

* Manages users
* Records transactions
* Displays balances
* Shows transaction history

### Why This App

* Naturally requires CRUD operations
* Demonstrates joins
* Shows the database working outside the REPL
* Reflects transactional data flow

The web app and the REPL both use the **same database engine**.

---

## Architecture Overview

```
┌───────────────┐
│   Web App     │
└───────┬───────┘
        │
┌───────▼───────┐
│  DB Engine    │
│ (Parser +    │
│  Executor)   │
└───────┬───────┘
        │
┌───────▼───────┐
│ Ledger Store  │
│ + Indexes     │
└───────────────┘
```

---

## Design Trade-offs

### Prioritized

* Simplicity
* Transparency
* Correctness
* Ease of reasoning

### Intentionally Excluded

* Query optimization
* Concurrency control
* Advanced indexing structures
* Distributed execution

These choices keep the system focused and understandable.

---

## Limitations

LedgerLite is not production-ready.

Known limitations include:

* Single-threaded execution
* Limited SQL grammar
* Basic persistence
* No transaction isolation levels

These constraints are acceptable given the project’s scope.

---

## Future Improvements

With more time, the system could be extended with:

* Write-ahead logging
* Improved indexing (B-Trees)
* Query planner and optimizer
* Snapshot-based persistence
* Transaction isolation
* Read-only replicas

---

## Use of AI Tools

AI tools were used strictly as **assistive tools** for:

* Clarifying concepts
* Reviewing ideas
* Improving documentation structure

All code and architectural decisions were implemented and understood by the author.

---

## Author

**Name:** kanew
**Challenge:** Pesapal Junior Developer Challenge 2026
**Repository:** Public and open for review

---

## Closing Note

LedgerLite is a learning-focused system designed to demonstrate how databases **behave**, not just how they store data.

The project emphasizes:

* Intentional design
* Honest limitations
* Clear abstractions

Where the implementation is simple, the ideas are deliberate.

---
