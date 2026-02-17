import re
import csv
import os
from urllib.parse import urlparse

RAW_FILE = 'data/raw_companies.txt'
CSV_FILE = 'data/seed_companies.csv'

def process_and_merge():
    print(f"Reading raw file: {RAW_FILE}")
    if not os.path.exists(RAW_FILE):
        print("Raw file not found!")
        return

    with open(RAW_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Regex for 'name': 'url'
    # matches 'tcs': 'http...'
    matches = re.findall(r"'([^']+)':\s*'([^']+)'", content)
    print(f"Found {len(matches)} entries.")
    
    existing_companies = {}
    
    # Load existing if any
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                norm_name = row['company_name'].lower().strip()
                existing_companies[norm_name] = row

    # Process new Matches
    added = 0
    for name, url in matches:
        clean_name = name.title().strip()
        # manual fixes
        if clean_name.lower() == 'tcs': clean_name = 'TCS'
        if clean_name.lower() == 'ibm': clean_name = 'IBM'
        if clean_name.lower() == 'hcltech': clean_name = 'HCLTech'
        
        parsed = urlparse(url)
        website = f"{parsed.scheme}://{parsed.netloc}"
        
        entry = {
            'company_name': clean_name,
            'careers_url': url,
            'website': website
        }
        
        # Upsert based on lower name
        norm_name = clean_name.lower()
        if norm_name not in existing_companies:
            added += 1
            
        existing_companies[norm_name] = entry

    # Write back
    fieldnames = ['company_name', 'careers_url', 'website']
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key in sorted(existing_companies.keys()):
            writer.writerow(existing_companies[key])
            
    print(f"✅ Total companies in CSV: {len(existing_companies)}")
    print(f"✅ Newly merged: {added}")

if __name__ == "__main__":
    process_and_merge()
