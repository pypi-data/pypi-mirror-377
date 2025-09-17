from datalineagepy.connectors.database.sqlite_connector import SQLiteConnector
from datalineagepy.core import LineageTracker

lineage_tracker = LineageTracker()
conn = SQLiteConnector('test_sqlite.db', lineage_tracker=lineage_tracker)

try:
    conn.execute_query(
        'CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)')
    conn.execute_query(
        'INSERT INTO test_table (id, name) VALUES (?, ?)', (1, 'Charlie'))
    result = conn.execute_query('SELECT * FROM test_table')
    print('Query Result:', result)
    print('Lineage Graph:', lineage_tracker.export_graph(format='dict'))
finally:
    conn.close()
