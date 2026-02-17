import sqlite3
import os

db_path = 'companies.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table in tables:
        print(f"\nSchema for {table[0]}:")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        for col in cursor.fetchall():
            print(col)
    conn.close()
else:
    print("Database not found")
