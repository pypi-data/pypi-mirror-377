from datalineagepy.connectors.database.mysql_connector import MySQLConnector
from datalineagepy.core import LineageTracker

# Update these credentials for your MySQL instance
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'test_db'
}

lineage_tracker = LineageTracker()
conn = MySQLConnector(**db_config, lineage_tracker=lineage_tracker)

try:
    conn.execute_query(
        'CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY, name VARCHAR(50))')
    conn.execute_query(
        'INSERT INTO test_table (id, name) VALUES (%s, %s)', (1, 'Alice'))
    result = conn.execute_query('SELECT * FROM test_table')
    print('Query Result:', result)
    print('Lineage Log:', lineage_tracker.get_log())
finally:
    conn.close()
