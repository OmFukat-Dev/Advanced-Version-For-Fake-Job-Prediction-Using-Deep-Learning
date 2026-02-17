import sqlite3
import os

DB_PATH = 'companies.db'
OUTPUT_FILE = 'db_inspect_output.txt'

with open(OUTPUT_FILE, 'w') as f:
    if not os.path.exists(DB_PATH):
        f.write("Database file not found.\n")
    else:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            f.write(f"Tables found: {tables}\n\n")
            
            for table in tables:
                table_name = table[0]
                f.write(f"Schema for {table_name}:\n")
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                for col in columns:
                    f.write(f"{col}\n")
                f.write("\n")
                
            conn.close()
        except Exception as e:
            f.write(f"Error inspecting DB: {e}\n")
