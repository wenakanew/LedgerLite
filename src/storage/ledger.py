"""
Ledger storage for LedgerLite.

Handles persistence and retrieval of ledger entries.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.types import LedgerEntry, OperationType


class LedgerStore:
    """Manages ledger entry storage and retrieval."""
    
    def __init__(self, ledger_file: str = "data/ledger.jsonl"):
        """
        Initialize ledger store.
        
        Args:
            ledger_file: Path to the ledger file (JSON Lines format)
        """
        self.ledger_file = Path(ledger_file)
        self._transaction_counter = 0
        self._ensure_data_directory()
        self._load_transaction_counter()
    
    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_transaction_counter(self) -> None:
        """Load the highest transaction ID from existing ledger entries."""
        if not self.ledger_file.exists():
            self._transaction_counter = 0
            return
        
        max_id = 0
        try:
            with open(self.ledger_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry_data = json.loads(line)
                        max_id = max(max_id, entry_data.get("transaction_id", 0))
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        self._transaction_counter = max_id
    
    def _get_next_transaction_id(self) -> int:
        """Get the next transaction ID."""
        self._transaction_counter += 1
        return self._transaction_counter
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()
    
    def append(self, entry: LedgerEntry) -> None:
        """
        Append a ledger entry to the file.
        
        Args:
            entry: Ledger entry to append
        """
        with open(self.ledger_file, 'a', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False)
            f.write('\n')
    
    def create_entry(
        self,
        table_name: str,
        operation: OperationType,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None
    ) -> LedgerEntry:
        """
        Create a new ledger entry.
        
        Args:
            table_name: Name of the table
            operation: Type of operation
            old_value: Previous value (for UPDATE/DELETE)
            new_value: New value (for INSERT/UPDATE)
            
        Returns:
            Created ledger entry
        """
        entry = LedgerEntry(
            transaction_id=self._get_next_transaction_id(),
            table_name=table_name,
            operation=operation,
            timestamp=self._get_timestamp(),
            old_value=old_value,
            new_value=new_value
        )
        return entry
    
    def read_all(self) -> List[LedgerEntry]:
        """
        Read all ledger entries from the file.
        
        Returns:
            List of ledger entries in chronological order
        """
        if not self.ledger_file.exists():
            return []
        
        entries = []
        try:
            with open(self.ledger_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry_data = json.loads(line)
                        entries.append(LedgerEntry.from_dict(entry_data))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise IOError(f"Error reading ledger file: {e}")
        
        return entries
    
    def reconstruct_state(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Reconstruct current table state by replaying ledger entries.
        
        Args:
            table_name: Name of the table to reconstruct
            
        Returns:
            List of current row states
        """
        entries = self.read_all()
        current_rows: Dict[Any, Dict[str, Any]] = {}
        
        for entry in entries:
            if entry.table_name != table_name:
                continue
            
            if entry.operation == OperationType.INSERT:
                if entry.new_value is None:
                    continue
                # Use the entire row as key for now; will be improved with primary key lookup
                # For now, we'll need the schema to get the primary key
                # This is a temporary implementation
                if entry.new_value:
                    # Store by a temporary key; will be improved
                    key = id(entry.new_value)  # Temporary: will use primary key
                    current_rows[key] = entry.new_value
            
            elif entry.operation == OperationType.UPDATE:
                if entry.new_value is None:
                    continue
                # Find the row to update
                # This will be improved when we have primary key information
                if entry.old_value:
                    old_key = id(entry.old_value)
                    if old_key in current_rows:
                        del current_rows[old_key]
                new_key = id(entry.new_value)
                current_rows[new_key] = entry.new_value
            
            elif entry.operation == OperationType.DELETE:
                if entry.old_value is None:
                    continue
                # Find and remove the row
                old_key = id(entry.old_value)
                if old_key in current_rows:
                    del current_rows[old_key]
        
        return list(current_rows.values())
    
    def reconstruct_state_with_primary_key(
        self,
        table_name: str,
        primary_key_column: str
    ) -> List[Dict[str, Any]]:
        """
        Reconstruct current table state using primary key for row identification.
        
        Args:
            table_name: Name of the table to reconstruct
            primary_key_column: Name of the primary key column
            
        Returns:
            List of current row states
        """
        entries = self.read_all()
        current_rows: Dict[Any, Dict[str, Any]] = {}
        
        for entry in entries:
            if entry.table_name != table_name:
                continue
            
            if entry.operation == OperationType.INSERT:
                if entry.new_value is None:
                    continue
                primary_key = entry.new_value.get(primary_key_column)
                if primary_key is not None:
                    current_rows[primary_key] = entry.new_value
            
            elif entry.operation == OperationType.UPDATE:
                if entry.new_value is None:
                    continue
                primary_key = entry.new_value.get(primary_key_column)
                if primary_key is not None:
                    current_rows[primary_key] = entry.new_value
            
            elif entry.operation == OperationType.DELETE:
                if entry.old_value is None:
                    continue
                primary_key = entry.old_value.get(primary_key_column)
                if primary_key is not None and primary_key in current_rows:
                    del current_rows[primary_key]
        
        return list(current_rows.values())
    
    def clear(self) -> None:
        """Clear all ledger entries (use with caution)."""
        if self.ledger_file.exists():
            self.ledger_file.unlink()
        self._transaction_counter = 0

