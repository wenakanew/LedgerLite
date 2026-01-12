"""
Web application for LedgerLite demonstration.
"""

import os
from flask import Flask, render_template, request, jsonify
from src.main import DatabaseEngine

app = Flask(__name__)

# Initialize database engine
ledger_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'ledger.jsonl')
db = DatabaseEngine(ledger_file=ledger_file)


@app.route('/')
def index():
    """Serve main page."""
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a SQL query."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'No query provided'}), 400
        
        result = db.execute(query)
        
        # Format result for JSON response
        if isinstance(result, list):
            return jsonify({
                'success': True,
                'result': result,
                'type': 'rows',
                'row_count': len(result)
            })
        elif isinstance(result, str):
            return jsonify({
                'success': True,
                'result': result,
                'type': 'message'
            })
        elif isinstance(result, int):
            return jsonify({
                'success': True,
                'result': f'{result} row(s) affected',
                'type': 'message',
                'rows_affected': result
            })
        else:
            return jsonify({
                'success': True,
                'result': str(result),
                'type': 'message'
            })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500


@app.route('/api/tables', methods=['GET'])
def list_tables():
    """List all tables in the database."""
    try:
        tables = db.schema_manager.get_all_tables()
        table_names = [table.name for table in tables]
        return jsonify({
            'success': True,
            'tables': table_names
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/table/<table_name>', methods=['GET'])
def get_table_info(table_name):
    """Get table schema information."""
    try:
        table = db.schema_manager.get_table(table_name)
        if not table:
            return jsonify({
                'success': False,
                'error': f'Table {table_name} not found'
            }), 404
        
        columns = []
        for col in table.columns:
            columns.append({
                'name': col.name,
                'type': col.data_type.value,
                'primary_key': col.is_primary_key,
                'unique': col.is_unique
            })
        
        return jsonify({
            'success': True,
            'table': {
                'name': table.name,
                'columns': columns
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get transaction history (ledger entries)."""
    try:
        # Get recent entries (limit to last 50 for performance)
        all_entries = db.ledger_store.read_all()
        entries = all_entries[-50:]  # Get last 50 entries
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                'transaction_id': entry.transaction_id,
                'table_name': entry.table_name,
                'operation': entry.operation.value,
                'timestamp': entry.timestamp,
                'old_value': entry.old_value,
                'new_value': entry.new_value
            })
        
        return jsonify({
            'success': True,
            'entries': formatted_entries
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
