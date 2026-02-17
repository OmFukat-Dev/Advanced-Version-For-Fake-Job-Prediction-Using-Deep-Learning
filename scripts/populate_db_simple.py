import csv
import sqlite3
import os

CSV_PATH = 'data/seed_companies.csv'
DB_PATH = 'companies.db'

def populate_db():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Seed file not found at {CSV_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ensure correct schema if not matches (columns: name, website, careers_url, verified, verification_confidence)
        # We assume standard schema exists.
        
        print(f"Reading {CSV_PATH}...")
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"📊 Found {len(rows)} companies in CSV.")
        
        added_count = 0
        updated_count = 0
        
        for row in rows:
            name = row['company_name']
            website = row['website']
            careers_url = row['careers_url']
            
            # Upsert Logic
            cursor.execute("SELECT id FROM companies WHERE name = ?", (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Optional: Update URL? Let's skip for now to avoid overwriting unless needed
                # But actually, trust user input. Let's update URL.
                cursor.execute("""
                    UPDATE companies 
                    SET careers_url = ?, website = ?, verified = 1, verification_confidence = 1.0
                    WHERE name = ?
                """, (careers_url, website, name))
                updated_count += 1
            else:
                cursor.execute('''
                    INSERT INTO companies (name, website, careers_url, verified, verification_confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, website, careers_url, 1, 1.0))
                added_count += 1
            
        conn.commit()
        conn.close()
        print(f"✅ Operations complete: Added {added_count}, Updated {updated_count}")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")

if __name__ == "__main__":
    populate_db()
