import re
import csv
import pandas as pd
from urllib.parse import urlparse

RAW_FILE = 'data/raw_companies.txt'
CSV_FILE = 'data/seed_companies.csv'

def process_and_merge():
    print("Reading raw file...")
    with open(RAW_FILE, 'r') as f:
        content = f.read()
    
    # Parse lines: 'name': 'url',
    # Regex to capture name and url
    # matches 'name': 'url' pattern
    matches = re.findall(r"'([^']+)':\s*'([^']+)'", content)
    
    print(f"Found {len(matches)} entries in raw text.")
    
    new_data = []
    for name, url in matches:
        # Clean name (capitalize mostly)
        clean_name = name.title()
        
        # Specific fixes
        if clean_name.lower() == 'tcs':
            clean_name = 'TCS'
        elif clean_name.lower() == 'ibm':
            clean_name = 'IBM'
        elif clean_name.lower() == 'hcltech':
            clean_name = 'HCLTech'
            
        # Extract website domain
        parsed = urlparse(url)
        # simplistic: scheme://netloc
        website = f"{parsed.scheme}://{parsed.netloc}"
        
        new_data.append({
            'company_name': clean_name,
            'careers_url': url,
            'website': website
        })
        
    if not new_data:
        print("No data parsed!")
        return

    # Load existing CSV
    try:
        existing_df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=['company_name', 'careers_url', 'website'])
        
    new_df = pd.DataFrame(new_data)
    
    # Combine and drop duplicates based on company_name (insensitive)
    combined_df = pd.concat([existing_df, new_df])
    
    # Simple deduplication on Lowercase Name
    combined_df['lower_name'] = combined_df['company_name'].str.lower()
    combined_df = combined_df.drop_duplicates(subset='lower_name', keep='last') # Keep user's new list if conflict
    combined_df = combined_df.drop(columns=['lower_name'])
    
    # Determine how many added
    added_count = len(combined_df) - len(existing_df)
    
    print(f"Total companies after merge: {len(combined_df)}")
    if len(existing_df) > 0:
        print(f"Added/Updated: {len(new_df)} (Note: some might be duplicates)")
    
    # Save back
    combined_df.to_csv(CSV_FILE, index=False)
    print(f"✅ Saved updated list to {CSV_FILE}")

if __name__ == "__main__":
    process_and_merge()
