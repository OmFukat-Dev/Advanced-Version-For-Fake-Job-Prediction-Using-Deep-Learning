import sqlite3
import re
import os

# Path to app.py and db
APP_PATH = 'app.py'
DB_PATH = 'companies.db'

def migrate():
    # 1. Read app.py content
    with open(APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 2. Extract the dictionary - this is a simple regex approach
    # Looking for lines like: 'company name': 'url',
    # This might need refinement depending on exact formatting
    pattern = r"'([^']+)'\s*:\s*'([^']+)'"
    matches = re.findall(pattern, content)
    
    print(f"Found {len(matches)} potential company entries.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    for name, url in matches:
        # Filter out obvious non-company matches if any (e.g. config keys)
        if len(name) < 2 or 'http' not in url:
            continue
            
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO companies (name, career_page_url, trust_score, source_confidence)
            VALUES (?, ?, ?, ?)
            ''', (name.strip(), url.strip(), 1.0, 'high'))
            if cursor.rowcount > 0:
                count += 1
        except Exception as e:
            print(f"Error inserting {name}: {e}")
            
    conn.commit()
    conn.close()
    print(f"✅ Migrated {count} companies to companies.db")

if __name__ == "__main__":
    migrate()
