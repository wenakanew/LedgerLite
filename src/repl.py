"""
Interactive REPL interface for LedgerLite.
"""

import sys
from typing import Any, List, Optional
from src.main import DatabaseEngine


def format_result(result: Any) -> str:
    """
    Format query result for display.
    
    Args:
        result: Query result
        
    Returns:
        Formatted string
    """
    if result is None:
        return ""
    
    if isinstance(result, str):
        return result
    
    if isinstance(result, list):
        if not result:
            return "(0 rows)"
        
        # Handle list of dictionaries (SELECT results)
        if isinstance(result[0], dict):
            return format_table(result)
        
        # Handle list of other types
        return str(result)
    
    if isinstance(result, int):
        # Likely a count (rows affected)
        if result == 0:
            return "(0 rows affected)"
        elif result == 1:
            return "(1 row affected)"
        else:
            return f"({result} rows affected)"
    
    return str(result)


def format_table(rows: List[dict]) -> str:
    """
    Format query results as a table.
    
    Args:
        rows: List of dictionaries representing rows
        
    Returns:
        Formatted table string
    """
    if not rows:
        return "(0 rows)"
    
    # Get all column names
    headers = list(rows[0].keys())
    
    # Calculate column widths
    col_widths = {}
    for header in headers:
        # Minimum width is header length
        max_width = len(str(header))
        for row in rows:
            value = str(row.get(header, ""))
            max_width = max(max_width, len(value))
        col_widths[header] = max_width
    
    # Format header
    header_parts = []
    for header in headers:
        header_parts.append(str(header).ljust(col_widths[header]))
    header_line = " | ".join(header_parts)
    
    # Format separator
    separator = "-" * len(header_line)
    
    # Format rows
    row_lines = []
    for row in rows:
        row_parts = []
        for header in headers:
            value = str(row.get(header, ""))
            row_parts.append(value.ljust(col_widths[header]))
        row_lines.append(" | ".join(row_parts))
    
    # Combine everything
    output = [header_line, separator] + row_lines
    output.append(f"\n({len(rows)} row(s))")
    
    return "\n".join(output)


def read_multiline_query() -> Optional[str]:
    """
    Read a multi-line SQL query.
    
    Returns:
        Complete query string or None if cancelled
    """
    lines = []
    print("Enter SQL query (end with semicolon or empty line):")
    
    while True:
        try:
            line = input("... " if lines else "ledgerlite> ").strip()
            
            if not lines and line.lower() in ['exit', 'quit']:
                return None
            
            if not line and not lines:
                continue
            
            lines.append(line)
            
            # Check if query is complete (ends with semicolon or is empty line after content)
            if line.endswith(';'):
                # Remove semicolon and join
                query = " ".join(lines[:-1] + [line[:-1].strip()])
                if query:  # Ensure there's actual content
                    return query
                lines = []
            elif not line and lines:
                # Empty line after content - join and return
                query = " ".join([l for l in lines if l])
                if query:
                    return query
                lines = []
        
        except (KeyboardInterrupt, EOFError):
            print("\nQuery cancelled.")
            return None


def start_repl(ledger_file: str = "data/ledger.jsonl"):
    """
    Start the interactive REPL.
    
    Args:
        ledger_file: Path to ledger file
    """
    print("=" * 60)
    print("LedgerLite - A Transaction-First Mini Relational Database")
    print("Version 0.1.0")
    print("=" * 60)
    print()
    print("Commands:")
    print("  - Type SQL queries to execute")
    print("  - End queries with semicolon (;) or press Enter twice")
    print("  - Type 'exit' or 'quit' to exit")
    print("  - Press Ctrl+C to cancel current query")
    print()
    print("-" * 60)
    print()
    
    db = DatabaseEngine(ledger_file=ledger_file)
    
    while True:
        try:
            # Read single-line or multi-line query
            query = input("ledgerlite> ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            # If query doesn't end with semicolon, try to read more lines
            if not query.endswith(';'):
                lines = [query]
                while True:
                    try:
                        line = input("... ").strip()
                        if not line:
                            break
                        lines.append(line)
                        if line.endswith(';'):
                            query = " ".join(lines)
                            query = query[:-1].strip() if query.endswith(';') else query
                            break
                    except (KeyboardInterrupt, EOFError):
                        print("\nQuery cancelled.")
                        query = None
                        break
                
                if not query:
                    continue
            
            else:
                # Remove semicolon
                query = query[:-1].strip()
            
            if not query:
                continue
            
            # Execute query
            try:
                result = db.execute(query)
                output = format_result(result)
                if output:
                    print(output)
            
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Unexpected error: {e}", file=sys.stderr)
            
            print()  # Blank line after result
        
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            break


if __name__ == "__main__":
    import sys
    ledger_file = sys.argv[1] if len(sys.argv) > 1 else "data/ledger.jsonl"
    start_repl(ledger_file=ledger_file)
