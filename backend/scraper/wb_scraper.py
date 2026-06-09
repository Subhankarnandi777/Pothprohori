#!/usr/bin/env python3
import os
import sys
import json
import subprocess

# Self-Install missing requirements dynamically
required_packages = [
    ("beautifulsoup4", "bs4"),
    ("requests", "requests"),
]
for pkg, imp_name in required_packages:
    try:
        __import__(imp_name)
    except ImportError:
        print(f"[Scraper] Installing missing package: {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

URL = "https://www.wbtrafficpolice.com/offences-and-penalties.php"

def scrape_wbtraffic():
    print(f"\n--- STEP 1.5: Scraping WB Traffic Police Website ---")
    print(f"[Scraper] Fetching data from {URL}...")
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Use headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get(URL, headers=headers, verify=False, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Get all text as a fallback
        content = soup.get_text(separator='\n', strip=True)
        
        # Parse tables into a dataset
        tables = soup.find_all("table")
        dataset = []
        if tables:
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    cols = [ele.text.strip().replace('\n', ' ').replace('\r', '') for ele in cols]
                    if cols:
                        dataset.append(cols)
        
        # Save JSON dataset
        json_path = os.path.join(PROCESSED_DIR, "wb_traffic_offences.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=4, ensure_ascii=False)
        print(f"[Scraper] Saved structured JSON data ({len(dataset)} rows) to {os.path.basename(json_path)}")
        
        # For RAG, save it as a text file partitioned by "=== West Bengal ===" 
        txt_path = os.path.join(PROCESSED_DIR, "wb_traffic_offences.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=== West Bengal ===\n")
            f.write("Source: WB Traffic Police Official Website (Offences and Penalties)\n\n")
            
            if dataset and len(dataset) > 1:
                # Use table data
                headers = dataset[0]
                for row in dataset[1:]:
                    row_text = []
                    for i, col in enumerate(row):
                        header = headers[i] if i < len(headers) else f"Column {i}"
                        row_text.append(f"{header}: {col}")
                    f.write(" | ".join(row_text) + "\n\n")
            else:
                # Fallback to plain text
                f.write(content)
        
        print(f"[Scraper] Saved text data for RAG ingestion to {os.path.basename(txt_path)}")
        return True
    
    except Exception as e:
        print(f"[Scraper] Failed to scrape WB Traffic Police website: {e}")
        return False

if __name__ == "__main__":
    scrape_wbtraffic()
