import unittest
import os
import sqlite3
from main import createdb, populatedb, status

class TestDatabaseFunctions(unittest.TestCase):
    
    def setUp(self):
        # Set up a test database and environment
        self.db_path = './resources/test_normanpd.db'
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                incident_time TEXT, 
                incident_number TEXT, 
                incident_location TEXT, 
                nature TEXT, 
                incident_ori TEXT
            )
        ''')

    def tearDown(self):
        # Clean up the database after tests
        self.conn.close()
        os.remove(self.db_path)

    def test_createdb(self):
        conn = createdb()
        self.assertIsNotNone(conn)
        conn.close()

    def test_populatedb(self):
        test_incidents = [
            ("2023-01-01 12:00:00", "12345", "Location A", "Nature A", "ORI123"),
            ("2023-01-02 12:00:00", "12346", "Location B", "Nature B", "ORI124"),
        ]
        populatedb(self.conn, test_incidents)
        
        self.cur.execute("SELECT COUNT(*) FROM incidents")
        count = self.cur.fetchone()[0]
        self.assertEqual(count, 2)

    def test_status(self):
        # Insert test data
        test_incidents = [
            ("2023-01-01 12:00:00", "12345", "Location A", "Nature A", "ORI123"),
            ("2023-01-01 12:30:00", "12346", "Location B", "Nature A", "ORI124"),
            ("2023-01-02 13:00:00", "12347", "Location C", "Nature B", "ORI125"),
        ]
        populatedb(self.conn, test_incidents)
        
        # Capture the output of the status function
        with self.assertLogs(level='INFO') as log:
            status(self.conn)
        
        # Check for specific log messages (might need to adapt based on actual output format)
        self.assertIn('Nature A|2', log.output[0])
        self.assertIn('Nature B|1', log.output[1])

if __name__ == '__main__':
    unittest.main()
