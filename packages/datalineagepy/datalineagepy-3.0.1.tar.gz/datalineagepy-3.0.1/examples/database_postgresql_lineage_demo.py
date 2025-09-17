from datalineagepy.connectors.database.postgresql_connector import PostgreSQLConnector
from datalineagepy.core import LineageTracker

# Update these credentials for your PostgreSQL instance
db_config = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'password',
    'database': 'test_db'
}

lineage_tracker = LineageTracker()
conn = PostgreSQLConnector(**db_config, lineage_tracker=lineage_tracker)

try:
    conn.execute_query(
        'CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(50))')
    conn.execute_query('INSERT INTO test_table (name) VALUES (%s)', ('Bob',))
    result = conn.execute_query('SELECT * FROM test_table')
    print('Query Result:', result)
    print('Lineage Log:', lineage_tracker.get_log())
finally:
    conn.close()
