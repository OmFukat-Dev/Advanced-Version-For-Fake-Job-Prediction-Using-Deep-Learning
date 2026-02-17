import pandas as pd
import sqlite3
import os

CSV_PATH = 'data/seed_companies.csv'
DB_PATH = 'companies.db'

def populate_db():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Seed file not found at {CSV_PATH}")
        return

    try:
        df = pd.read_csv(CSV_PATH)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"📊 Found {len(df)} companies in seed file.")
        
        added_count = 0
        for _, row in df.iterrows():
            name = row['company_name']
            website = row['website']
            careers_url = row['careers_url']
            
            # Check if exists
            cursor.execute("SELECT id FROM companies WHERE name = ?", (name,))
            if cursor.fetchone():
                print(f"⚠️ {name} already exists. Skipping.")
                continue
                
            # Insert with high confidence
            cursor.execute('''
                INSERT INTO companies (name, website, careers_url, verified, verification_confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, website, careers_url, 1, 1.0))
            
            added_count += 1
            
        conn.commit()
        conn.close()
        print(f"✅ Successfully added {added_count} new companies to the database.")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")

if __name__ == "__main__":
    populate_db()
