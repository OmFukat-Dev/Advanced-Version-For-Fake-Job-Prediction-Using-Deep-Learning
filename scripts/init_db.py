import sqlite3
import os

DB_PATH = 'companies.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create companies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        domain TEXT,
        career_page_url TEXT,
        trust_score REAL DEFAULT 0.0,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        source_confidence TEXT DEFAULT 'low'
    )
    ''')
    
    # Create job_postings table for history/logging
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_postings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        content_hash TEXT,
        source_url TEXT,
        risk_score REAL,
        analysis_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    )
    ''')
    
    # Create scam_patterns table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scam_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_text TEXT NOT NULL UNIQUE,
        risk_level TEXT DEFAULT 'high',
        category TEXT
    )
    ''')
    
    # Seed some initial scam patterns
    initial_patterns = [
        ("wire transfer", "critical", "payment"),
        ("google hangouts interview", "high", "communication"),
        ("kindly send money", "critical", "payment"),
        ("pay for training", "high", "payment"),
        ("urgent hiring no interview", "high", "urgency")
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO scam_patterns (pattern_text, risk_level, category)
    VALUES (?, ?, ?)
    ''', initial_patterns)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
