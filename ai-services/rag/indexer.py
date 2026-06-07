"""
Ingest traffic laws JSON → embed → store in ChromaDB.
Run:  python ai-services/rag/indexer.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.embeddings import EmbeddingModel

try:
    import chromadb  # type: ignore
    CHROMA_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    CHROMA_AVAILABLE = False

CHROMA_HOST     = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT     = int(os.getenv("CHROMA_PORT", 8001))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "traffic_laws")
DATA_PATH       = os.path.join(os.path.dirname(__file__), "../data/violation_fines.json")

def ingest():
    if not CHROMA_AVAILABLE:
        print("[Indexer Fallback] ChromaDB is not installed. Pure Python fallback will be used instead. Ingest skipped.")
        return

    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    except Exception:
        try:
            client = chromadb.Client()
        except Exception as e:
            print(f"[Indexer Fallback] Failed to initialize ChromaDB: {e}. Skipping ingestion.")
            return

    try:
        collection = client.get_or_create_collection(COLLECTION_NAME)
        embedder   = EmbeddingModel()

        with open(DATA_PATH) as f:
            laws = json.load(f)

        ids, embeddings, documents, metadatas = [], [], [], []

        for law in laws:
            text = (
                f"Violation: {law['violation']}. "
                f"State: {law.get('state', 'National')}. "
                f"Vehicle: {law.get('vehicle_type', 'All')}. "
                f"Fine: ₹{law['fine_min']}–₹{law['fine_max']}. "
                f"Section: {law.get('section', 'N/A')}. "
                f"Penalties and Rules: {law.get('penalty_details', '')}"
            )
            ids.append(str(law["id"]))
            embeddings.append(embedder.embed(text))
            documents.append(text)
            metadatas.append({
                "law_id":       str(law["id"]),
                "state":        law.get("state", ""),
                "section":      law.get("section", ""),
                "vehicle_type": law.get("vehicle_type", "all"),
                "category":     law.get("category", ""),
            })

        collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        print(f"[Indexer] Ingested {len(ids)} laws into ChromaDB collection '{COLLECTION_NAME}'")
    except Exception as e:
        print(f"[Indexer] Ingestion failed: {e}")

if __name__ == "__main__":
    ingest()
