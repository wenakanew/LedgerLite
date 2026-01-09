"""
Main entry point for LedgerLite REPL.
"""

from typing import Any
from src.storage.schema import SchemaManager
from src.storage.ledger import LedgerStore
from src.index.index_manager import IndexManager
from src.executor.executor import QueryExecutor
from src.parser.parser import parse_sql, ParserError


class DatabaseEngine:
    """Main database engine."""
    
    def __init__(self, ledger_file: str = "data/ledger.jsonl"):
        """Initialize database engine."""
        self.schema_manager = SchemaManager()
        self.ledger_store = LedgerStore(ledger_file=ledger_file)
        self.index_manager = IndexManager()
        self.executor = QueryExecutor(
            self.schema_manager,
            self.ledger_store,
            self.index_manager
        )
    
    def execute(self, query: str) -> Any:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            
        Returns:
            Query result
        """
        # Parse the query
        try:
            ast = parse_sql(query)
            # Execute the AST
            return self.executor.execute(ast)
        except ParserError as e:
            raise ValueError(f"Parse error: {e}")
        except Exception as e:
            raise ValueError(f"Execution error: {e}")


def main():
    """Start the REPL."""
    print("LedgerLite - A Transaction-First Mini Relational Database System")
    print("Version 0.1.0")
    print()
    print("Type 'exit' or 'quit' to exit")
    print()
    
    db = DatabaseEngine()
    
    while True:
        try:
            query = input("ledgerlite> ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            # TODO: Parse and execute query
            result = db.execute(query)
            print(result)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
