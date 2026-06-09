import os
import sys
import json
import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

URL = "https://www.bankbazaar.com/driving-licence/traffic-fines.html"

def scrape_bankbazaar():
    print(f"\n--- Scraping BankBazaar Traffic Fines ---")
    print(f"[Scraper] Fetching data from {URL}...")
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get(URL, headers=headers, verify=False, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Scrape headings and text to get the rules
        content = soup.get_text(separator='\n', strip=True)
        
        # We can try to extract tables for fines
        dataset = []
        tables = soup.find_all("table")
        if tables:
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    cols = [ele.text.strip().replace('\n', ' ').replace('\r', '') for ele in cols]
                    if cols:
                        dataset.append(cols)
                        
        txt_path = os.path.join(PROCESSED_DIR, "bankbazaar_traffic_fines.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=== BankBazaar Traffic Fines India ===\n")
            f.write(f"Source: {URL}\n\n")
            
            if dataset and len(dataset) > 1:
                # Use table data
                headers_list = dataset[0]
                for row in dataset[1:]:
                    row_text = []
                    for i, col in enumerate(row):
                        header = headers_list[i] if i < len(headers_list) else f"Column {i}"
                        row_text.append(f"{header}: {col}")
                    f.write(" | ".join(row_text) + "\n\n")
            else:
                f.write(content)
                
        print(f"[Scraper] Saved text data for RAG ingestion to {os.path.basename(txt_path)}")
        return True
    
    except Exception as e:
        print(f"[Scraper] Failed to scrape BankBazaar website: {e}")
        return False

if __name__ == "__main__":
    scrape_bankbazaar()
