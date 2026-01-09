"""
Tests for ledger storage.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from src.storage.ledger import LedgerStore
from src.types import OperationType, LedgerEntry


def test_ledger_store_creation():
    """Test creating a ledger store."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "ledger.jsonl")
        store = LedgerStore(ledger_file=ledger_file)
        assert store.ledger_file == Path(ledger_file)


def test_create_entry():
    """Test creating a ledger entry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "ledger.jsonl")
        store = LedgerStore(ledger_file=ledger_file)
        
        entry = store.create_entry(
            table_name="users",
            operation=OperationType.INSERT,
            new_value={"id": 1, "name": "Alice"}
        )
        
        assert entry.table_name == "users"
        assert entry.operation == OperationType.INSERT
        assert entry.transaction_id == 1
        assert entry.new_value == {"id": 1, "name": "Alice"}


def test_append_and_read():
    """Test appending and reading ledger entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "ledger.jsonl")
        store = LedgerStore(ledger_file=ledger_file)
        
        entry1 = store.create_entry(
            table_name="users",
            operation=OperationType.INSERT,
            new_value={"id": 1, "name": "Alice"}
        )
        store.append(entry1)
        
        entry2 = store.create_entry(
            table_name="users",
            operation=OperationType.INSERT,
            new_value={"id": 2, "name": "Bob"}
        )
        store.append(entry2)
        
        entries = store.read_all()
        assert len(entries) == 2
        assert entries[0].transaction_id == 1
        assert entries[1].transaction_id == 2


def test_reconstruct_state_with_primary_key():
    """Test state reconstruction using primary key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "ledger.jsonl")
        store = LedgerStore(ledger_file=ledger_file)
        
        # Insert
        entry1 = store.create_entry(
            table_name="users",
            operation=OperationType.INSERT,
            new_value={"id": 1, "name": "Alice"}
        )
        store.append(entry1)
        
        # Update
        entry2 = store.create_entry(
            table_name="users",
            operation=OperationType.UPDATE,
            old_value={"id": 1, "name": "Alice"},
            new_value={"id": 1, "name": "Alice Updated"}
        )
        store.append(entry2)
        
        # Insert another
        entry3 = store.create_entry(
            table_name="users",
            operation=OperationType.INSERT,
            new_value={"id": 2, "name": "Bob"}
        )
        store.append(entry3)
        
        # Delete
        entry4 = store.create_entry(
            table_name="users",
            operation=OperationType.DELETE,
            old_value={"id": 2, "name": "Bob"}
        )
        store.append(entry4)
        
        state = store.reconstruct_state_with_primary_key("users", "id")
        assert len(state) == 1
        assert state[0]["id"] == 1
        assert state[0]["name"] == "Alice Updated"
