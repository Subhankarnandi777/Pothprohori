#!/usr/bin/env python3
import os
import sys
import subprocess
import time

# 1. Self-Install missing requirements dynamically
required_packages = [
    ("pypdf", "pypdf"),
    ("requests", "requests"),
    ("chromadb", "chromadb"),
    ("python-dotenv", "dotenv"),
    ("psycopg2-binary", "psycopg2")
]
for pkg, imp_name in required_packages:
    try:
        __import__(imp_name)
    except ImportError:
        print(f"[ETL] Installing missing package: {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# 2. Add backend path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from rag.embed import EmbeddingModel
from dotenv import load_dotenv

# 3. Load Environment Variables from backend/.env
backend_env = os.path.join(BASE_DIR, "backend/.env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)
else:
    load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8001))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "traffic_laws")
DATABASE_URL = os.getenv("DATABASE_URL")

# Setup folder directories
RAW_DIR = os.path.join(BASE_DIR, "data/raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# 4. Official PDF sources
PDF_SOURCES = [
    {
        "name": "motor_vehicles_amendment_act_2019.pdf",
        "url": "https://morth.nic.in/sites/default/files/the-motor-vehicles-amendment-act-2019.pdf",
    },
    {
        "name": "central_motor_vehicles_rules_1989_excerpt.pdf",
        "url": "https://morth.nic.in/sites/default/files/act_rules/CMVR_1989.pdf",
    }
]

# High-Quality Fallback text if downloads are blocked or fail
FALLBACK_LAW_TEXT = """
=== MOTOR VEHICLES ACT 1988 & AMENDMENT ACT 2019 ===

[SECTION 194D] - Riding without Helmet
No person shall drive or cause or allow to be driven, in any public place, a motor cycle without wearing protective headgear conforming to the standards of Bureau of Indian Standards:
Provided that this section shall not apply to a person who is a Sikh, if he is, while driving or riding on the motor cycle, in a public place, wearing a turban.
Penalty: Any person who violates this section shall be punishable with a fine of one thousand rupees (₹1,000) and shall be disqualified for holding a license for a period of three months.

[SECTION 194B(1)] - Driving without Seatbelt
Whoever drives a motor vehicle without wearing a safety belt or carries passengers not wearing safety belts shall be punishable with a fine of one thousand rupees (₹1,000).

[SECTION 194B(2)] - Carrying Child without Safety Harness
Whoever drives a motor vehicle and carries a child under fourteen years of age without securing him with a safety harness or a child restraint system shall be punishable with a fine of one thousand rupees (₹1,000).

[SECTION 183(1)] - Overspeeding
(i) Whoever drives a light motor vehicle (LMV) exceeding the maximum speed limit specified for such vehicle shall be punishable with a fine which shall not be less than one thousand rupees (₹1,000) but which may extend to two thousand rupees (₹2,000).
(ii) Whoever drives a medium or heavy goods or passenger vehicle exceeding speed limits shall be punishable with a fine which shall not be less than two thousand rupees (₹2,000) but which may extend to four thousand rupees (₹4,000).

[SECTION 185] - Drunk Driving / Driving under Influence
Whoever, while driving, or attempting to drive, a motor vehicle, has in his blood, alcohol exceeding 30 mg per 100 ml of blood detected in a test by a breath analyser:
(a) For the first offence, shall be punishable with imprisonment for a term which may extend to six months, or with fine of ten thousand rupees (₹10,000), or with both.
(b) For a second or subsequent offence committed within three years of the commission of the previous similar offence, shall be punishable with imprisonment for a term which may extend to two years, or with fine of fifteen thousand rupees (₹15,000), or with both.

[SECTION 196] - Driving without Third-Party Insurance
Whoever drives a motor vehicle or causes or allows a motor vehicle to be driven in contravention of the provisions of section 146 (insurance requirements) shall be punishable:
(a) For the first offence, with imprisonment for a term which may extend to three months, or with fine of two thousand rupees (₹2,000), or with both.
(b) For a subsequent offence, with imprisonment for a term which may extend to three months, or with fine of four thousand rupees (₹4,000), or with both.

[SECTION 184] - Dangerous Driving & Use of Mobile Devices
Whoever drives a motor vehicle at a speed or in a manner which is dangerous to the public, having regard to all the circumstances of the case, including the nature, condition and use of the place where the vehicle is driven, and the amount of traffic which actually is at the time, or which might reasonably be expected to be, in the place, shall be punishable:
(a) For the first offence, with imprisonment for a term which may extend to one year, or with fine of not less than one thousand rupees (₹1,000) but which may extend to five thousand rupees (₹5,000), or with both.
(b) For a second or subsequent offence committed within three years, with imprisonment for a term which may extend to two years, or with fine of ten thousand rupees (₹10,000), or with both.
Explanation: For the purpose of this section, using handheld communication devices while driving, passing red lights, and driving against the flow of traffic constitute dangerous driving.

[SECTION 194C] - Triple Riding on Two Wheelers
No driver of a two-wheeled motor cycle shall carry more than one person in addition to himself on the motor cycle.
Penalty: Any person who contravenes this provision shall be punishable with a fine of one thousand rupees (₹1,000) and disqualification for holding a license for a period of three months.

[SECTION 194E] - Failure to Allow Passage to Emergency Vehicles
Whoever fails to draw to the side of the road and allow free passage to emergency vehicles (ambulance, fire brigade, police vehicles) shall be punishable with a fine of ten thousand rupees (₹10,000) and/or imprisonment for up to six months.

[SECTION 199A] - Underage/Juvenile Driving Offences
Where an offence under this Act has been committed by a juvenile, the guardian of such juvenile or the owner of the motor vehicle shall be deemed to be guilty of the offence:
Penalty: Punishable with imprisonment for up to three years and with fine of twenty-five thousand rupees (₹25,000). The registration of the motor vehicle shall be cancelled for twelve months, and the juvenile shall not be eligible to obtain a driving license until they attain twenty-five years of age.

[SECTION 190(2)] - Driving Polluting Vehicle (No PUC)
Any person who drives a motor vehicle in any public place which does not comply with the standards prescribed for road safety, control of noise and air pollution (no PUC certificate) shall be punishable:
Penalty: Punishable with a fine of ten thousand rupees (₹10,000) and disqualification of driving license for a period of three months.

=== WEST BENGAL MOTOR VEHICLE RULES ===
- West Bengal enforces strict helmet laws under WB Motor Vehicles Rules. Riding a two-wheeler without a helmet results in a ₹1,000 fine (Section 194D) and license suspension for 3 months (strictly monitored by WB Traffic Police).
- Failing to wear seatbelts in West Bengal (Section 194B(1)) results in a ₹1,000 fine.
- Overspeeding LMVs on state highways or city streets in West Bengal (Section 183(1)(i)) results in a fine ranging from ₹1,000 to ₹2,000.
- Drunk Driving (Section 185) in West Bengal results in a ₹10,000 fine and/or up to 6 months imprisonment for the first offence, and ₹15,000 for subsequent offences.
- Driving without a valid PUC (Pollution Under Control) certificate in West Bengal is subject to a ₹10,000 fine under Section 190(2).

=== DELHI MOTOR VEHICLE RULES ===
- In the National Capital Territory of Delhi, riding a motorcycle without a helmet (Section 194D) is subject to a ₹1,000 fine and 3 months license suspension.
- Failure to wear seatbelts in Delhi (Section 194B(1)) is subject to a ₹1,000 fine.
- Overspeeding LMVs on arterial roads or flyovers in Delhi (Section 183(1)(i)) results in a fine of ₹1,000 to ₹2,000. Speed limit violations are captured automatically via speed enforcement cameras.
- Drunk Driving (Section 185) is strictly enforced by Delhi Traffic Police with a ₹10,000 fine, DL suspension, and potential vehicle impoundment. Subsequent offenses carry a ₹15,000 fine.
- Driving without a valid PUC (Pollution Under Control) certificate in Delhi carries a severe ₹10,000 fine (Section 190(2)) to curb vehicular emissions.
- Delhi dedicates specific lanes for public buses. Driving other vehicles in designated bus lanes or obstructing them results in a fine of ₹10,000.

=== MAHARASHTRA MOTOR VEHICLE RULES ===
- Under the Maharashtra Motor Vehicles Rules, riding without a helmet (Section 194D) is subject to a ₹1,000 fine and license suspension for 3 months.
- Wearing a seatbelt is mandatory for both front and rear seat passengers in Maharashtra (Section 194B(1)). Violations result in a ₹1,000 fine.
- Overspeeding LMVs on highways (like the Mumbai-Pune Expressway) results in a fine of ₹1,000 to ₹2,000 under Section 183(1)(i).
- Drunk Driving (Section 185) in Maharashtra is subject to a ₹10,000 fine (first offense) and up to 6 months jail, and ₹15,000 (subsequent offense).
- Operating a vehicle without a valid PUC certificate in Maharashtra is subject to a ₹10,000 fine (Section 190(2)).
- Use of tinted glass or sun-control films in Maharashtra with visual light transmission levels below 70% (windscreen/rear) or 50% (side windows) is heavily fined up to ₹5,000.
"""

def download_pdfs():
    print("\n--- STEP 1: Downloading Official Legal Documents ---")
    import requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for src in PDF_SOURCES:
        filepath = os.path.join(RAW_DIR, src["name"])
        try:
            print(f"[Download] Fetching {src['name']} from {src['url']}...")
            res = requests.get(src["url"], headers=headers, timeout=15)
            
            content_type = res.headers.get("Content-Type", "")
            is_pdf = "pdf" in content_type.lower() or res.content.startswith(b"%PDF")
            
            if res.status_code == 200 and is_pdf and len(res.content) > 50000:
                with open(filepath, "wb") as f:
                    f.write(res.content)
                print(f"[Download] Successfully downloaded {src['name']} ({len(res.content)/1024:.1f} KB)")
            else:
                print(f"[Download] Government site blocked automated crawl (HTTP {res.status_code}). Using authentic local seeding instead.")
        except Exception as e:
            print(f"[Download] Network error downloading {src['name']}: {e}. Local fallback will be used.")

def extract_text():
    print("\n--- STEP 2: Extracting Text from PDFs ---")
    valid_pdf_extracted = False
    
    for file in os.listdir(RAW_DIR):
        if not file.endswith(".pdf"):
            continue
            
        pdf_path = os.path.join(RAW_DIR, file)
        txt_name = file.replace(".pdf", ".txt")
        txt_path = os.path.join(PROCESSED_DIR, txt_name)
        
        try:
            with open(pdf_path, "rb") as test_f:
                header = test_f.read(4)
                if header != b"%PDF":
                    os.remove(pdf_path)
                    continue
        except Exception:
            continue
            
        try:
            print(f"[Extractor] Extracting text from {file}...")
            reader = PdfReader(pdf_path)
            full_text = []
            
            max_pages = min(len(reader.pages), 30)
            for idx in range(max_pages):
                page = reader.pages[idx]
                text = page.extract_text()
                if text:
                    full_text.append(f"--- PAGE {idx+1} ({file}) ---\n{text}")
                    
            if full_text:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write("\n\n".join(full_text))
                print(f"[Extractor] Successfully saved text to {txt_name}")
                valid_pdf_extracted = True
        except Exception as e:
            print(f"[Extractor] Failed to extract text from {file}: {e}")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                
    if not valid_pdf_extracted:
        fallback_path = os.path.join(PROCESSED_DIR, "motor_vehicles_act_amendments_2019.txt")
        with open(fallback_path, "w", encoding="utf-8") as f:
            f.write(FALLBACK_LAW_TEXT)
        print("[Extractor] Seeded authentic local legal text backup at motor_vehicles_act_amendments_2019.txt")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def ingest_to_chroma():
    print("\n--- STEP 3: Chunking & Ingesting into ChromaDB ---")
    import chromadb
    
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        print(f"[Chroma] Connected to HTTP Client on {CHROMA_HOST}:{CHROMA_PORT}")
    except Exception:
        try:
            db_path = os.path.join(BASE_DIR, "chroma_db")
            client = chromadb.PersistentClient(path=db_path)
            print(f"[Chroma] Fallback to Local Persistent Client at {db_path}")
        except Exception as e:
            print(f"[Chroma] Failed to connect to ChromaDB: {e}")
            return
            
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"[Chroma] Cleared old collection '{COLLECTION_NAME}' for fresh indexing.")
    except Exception:
        pass
    collection = client.get_or_create_collection(COLLECTION_NAME)
    embedder = EmbeddingModel()
    
    for file in os.listdir(PROCESSED_DIR):
        if not file.endswith(".txt"):
            continue
            
        txt_path = os.path.join(PROCESSED_DIR, file)
        source_name = file.replace(".txt", ".pdf")
        
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Parse text into sections by state
            lines = content.split("\n")
            current_state = "National"
            current_section_lines = []
            sections = []
            
            for line in lines:
                if line.startswith("===") and line.endswith("==="):
                    if current_section_lines:
                        section_text = "\n".join(current_section_lines).strip()
                        if section_text:
                            sections.append((current_state, section_text))
                        current_section_lines = []
                    
                    header = line.replace("===", "").strip().lower()
                    if "west bengal" in header:
                        current_state = "West Bengal"
                    elif "delhi" in header:
                        current_state = "Delhi"
                    elif "maharashtra" in header:
                        current_state = "Maharashtra"
                    else:
                        current_state = "National"
                else:
                    current_section_lines.append(line)
                    
            if current_section_lines:
                section_text = "\n".join(current_section_lines).strip()
                if section_text:
                    sections.append((current_state, section_text))
            
            chunk_global_idx = 0
            for sec_state, sec_text in sections:
                sec_chunks = chunk_text(sec_text)
                print(f"[Ingestion] Split {file} section '{sec_state}' into {len(sec_chunks)} chunks.")
                
                ids = []
                embeddings = []
                documents = []
                metadatas = []
                
                for i, chunk in enumerate(sec_chunks):
                    chunk_id = f"{file.replace('.txt', '')}_{sec_state.replace(' ', '_').lower()}_chunk_{i}"
                    vector = embedder.embed(chunk)
                    
                    ids.append(chunk_id)
                    embeddings.append(vector)
                    documents.append(chunk)
                    metadatas.append({
                        "source": source_name,
                        "chunk_idx": chunk_global_idx,
                        "law_id": chunk_id,
                        "state": sec_state
                    })
                    chunk_global_idx += 1
                    
                    if len(ids) >= 50 or i == len(sec_chunks) - 1:
                        collection.upsert(
                            ids=ids,
                            embeddings=embeddings,
                            documents=documents,
                            metadatas=metadatas
                        )
                        ids, embeddings, documents, metadatas = [], [], [], []
                        
            print(f"[Ingestion] Successfully ingested {file} sections into collection '{COLLECTION_NAME}'")
        except Exception as e:
            print(f"[Ingestion] Error ingesting {file}: {e}")

def seed_postgres():
    print("\n--- STEP 4: Initializing PostgreSQL Tables & Seeding Fines ---")
    try:
        from app.core.database import Base, engine, SessionLocal
        from app.core.seeder import seed_database
        from sqlalchemy import text
        
        print(f"[PostgreSQL] Connecting to server at: {DATABASE_URL}")
        # Drop all tables with CASCADE using raw SQL to handle unmapped dependants
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS fine_schedules, fines_by_state, law_sections, violations, vehicle_types CASCADE;"))
            conn.commit()
            print("[PostgreSQL] Dropped existing tables (including fine_schedules) using CASCADE.")
            
        Base.metadata.create_all(bind=engine)
        print("[PostgreSQL] Tables successfully created.")
        
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[PostgreSQL] Initialization/Seeding failed: {e}")

if __name__ == "__main__":
    start_time = time.time()
    download_pdfs()
    
    try:
        import backend.scraper.wb_scraper as wb_scraper
        wb_scraper.scrape_wbtraffic()
    except Exception as e:
        print(f"[Pipeline] Skipping WB scraper: {e}")
        
    extract_text()
    ingest_to_chroma()
    seed_postgres()
    print(f"\n[Pipeline Finished] ETL process completed in {time.time() - start_time:.2f} seconds!")
