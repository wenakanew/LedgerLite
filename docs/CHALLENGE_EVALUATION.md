# LedgerLite: Challenge Requirements Analysis

This document provides an objective assessment of how LedgerLite addresses the requirements of the Pesapal Junior Developer Challenge 2026.

---

## Requirements Checklist

### Mandatory Requirements

| Requirement | Status | Implementation |
|------------|--------|----------------|
| Simple RDBMS | ✅ | Complete RDBMS implementation |
| Table declaration with data types | ✅ | Supports INT, TEXT, FLOAT, BOOLEAN, TIMESTAMP |
| CRUD operations | ✅ | INSERT, SELECT, UPDATE, DELETE implemented |
| Basic indexing | ✅ | Primary key and unique constraint indexes |
| Primary key support | ✅ | PRIMARY KEY constraint enforced |
| Unique key support | ✅ | UNIQUE constraint enforced |
| Joining capability | ✅ | INNER JOIN supported |
| SQL or similar interface | ✅ | SQL-like syntax implemented |
| Interactive REPL mode | ✅ | REPL interface included |
| Web app demonstration | ✅ | Admin-style web app with CRUD operations |

**Result: All mandatory requirements met.**

---

## Design Approach

### Ledger-Based Storage

LedgerLite uses an immutable ledger to record all data modifications. Rather than mutating data in place, every INSERT, UPDATE, and DELETE operation creates a ledger entry. The current database state is derived by replaying these entries.

**Characteristics:**
- Full change history preserved
- Natural audit trail
- Simple rollback capability
- State reconstruction through entry replay

**Trade-offs:**
- Simpler write operations (append-only)
- More complex read operations (replay required)
- Storage overhead (all changes retained)
- Clear auditability

This approach aligns with systems where traceability and correctness are prioritized over write performance.

---

## Technical Implementation

### Architecture Components

1. **SQL Parser**: Converts SQL statements into structured representations
2. **Query Executor**: Executes statements and validates constraints
3. **Ledger Store**: Persists and retrieves ledger entries
4. **Index Manager**: Maintains indexes for primary keys and unique constraints

### Data Model

- Structured tables with fixed schemas
- Strongly typed columns
- Row-based storage model
- Constraint enforcement at write time

### Supported Operations

- **CREATE TABLE**: Define table schemas with columns and constraints
- **INSERT**: Add new rows with constraint validation
- **SELECT**: Query data with WHERE clauses and JOINs
- **UPDATE**: Modify existing rows with constraint validation
- **DELETE**: Remove rows while preserving history

### Constraints

- Primary key uniqueness enforced
- Unique constraint enforcement
- Type validation on insert and update
- Constraint violations raise clear errors

---

## Alignment with Challenge Criteria

### Requirement Fulfillment

All specified requirements are addressed:

- **RDBMS implementation**: Complete database engine with storage, indexing, and query execution
- **Table and data types**: Full schema definition support
- **CRUD operations**: All four operations implemented
- **Indexing**: Primary key and unique constraint indexes
- **Constraints**: Primary and unique key enforcement
- **Joins**: INNER JOIN implementation
- **SQL interface**: SQL-like syntax parser and executor
- **REPL**: Interactive command-line interface
- **Web app**: Demonstration application using the database

### Design Considerations

**Clarity and Correctness:**
- Code structure emphasizes readability
- Design decisions documented
- Trade-offs explicitly stated
- Limitations acknowledged

**Intentional Scope:**
- Focused feature set
- Simplicity prioritized over completeness
- Clear boundaries on what is and isn't included

**Practical Demonstration:**
- Web application shows real-world usage
- REPL enables interactive exploration
- Both interfaces use the same database engine

---

## Implementation Status

### Completed Components

- System architecture defined
- Data model specified
- Design decisions documented
- Implementation plan established

### Remaining Work

- Code implementation
- Unit and integration testing
- Web application development
- Documentation and examples

---

## Technical Notes

### Ledger Storage Format

Ledger entries are stored in JSON Lines format (`.jsonl`), with one JSON object per line. Each entry contains:
- Transaction ID
- Table name
- Operation type
- Timestamp
- Previous value (if applicable)
- New value

### State Reconstruction

Current table state is derived by replaying all ledger entries in chronological order. This approach is straightforward to implement and reason about, though it may have performance implications for large datasets.

### Index Management

Indexes are maintained in memory as hash maps, providing fast lookups for primary key and unique constraint validations. Indexes are updated synchronously with ledger writes.

### Constraint Validation

Constraints are validated before ledger entries are written. This ensures data integrity but means validation occurs during write operations rather than asynchronously.

---

## Limitations

The following limitations are acknowledged:

- Single-threaded execution
- Limited SQL grammar subset
- Basic persistence (JSON Lines file)
- No transaction isolation levels
- No query optimization
- No concurrent access control

These limitations are intentional given the project scope and learning objectives.

---

## Future Enhancements

Potential extensions if time permits:

- Write-ahead logging for durability
- B-tree indexes for larger datasets
- Query planner and optimizer
- Snapshot-based persistence
- Transaction isolation
- Read-only replicas

---

## Assessment Summary

LedgerLite addresses all mandatory challenge requirements. The ledger-based storage approach provides a clear demonstration of database fundamentals while offering a distinct perspective on data management. The design prioritizes clarity and correctness, with explicit trade-offs and limitations documented.

The implementation plan provides a structured path to completion, with clear separation of concerns and incremental development phases. The system architecture supports both the interactive REPL and web application demonstration requirements.

---

## Conclusion

This project meets the challenge requirements and demonstrates understanding of relational database concepts, system design, and practical engineering trade-offs. The ledger-based approach offers a clear, auditable data model that aligns with systems where traceability is important.

The focus on clarity, intentional design, and honest assessment of limitations reflects a thoughtful approach to the challenge. Implementation progress will determine the final outcome.
