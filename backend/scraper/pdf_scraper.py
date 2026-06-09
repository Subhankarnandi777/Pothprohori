import os
import requests
import PyPDF2
import io

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DIR = os.path.join(BASE_DIR, "data/raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

URL = "https://bidhannagarcitypolice.gov.in/assets/docs/TrafficRules.pdf"

def extract_pdf_data():
    print(f"\n--- Downloading and Extracting Bidhannagar Police PDF ---")
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get(URL, headers=headers, verify=False, timeout=15)
        res.raise_for_status()
        
        pdf_path = os.path.join(RAW_DIR, "Bidhannagar_TrafficRules.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(res.content)
            
        print(f"[Scraper] PDF downloaded to {pdf_path}")
        
        # Extract text
        text_content = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content += f"\n--- Page {i+1} ---\n{page_text}\n"
                    
        txt_path = os.path.join(PROCESSED_DIR, "bidhannagar_traffic_rules.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=== Bidhannagar City Police Traffic Rules ===\n")
            f.write(f"Source: {URL}\n\n")
            f.write(text_content)
            
        print(f"[Scraper] Extracted PDF text saved to {txt_path}")
        return True

    except Exception as e:
        print(f"[Scraper] Failed to download or extract PDF: {e}")
        return False

if __name__ == "__main__":
    extract_pdf_data()
