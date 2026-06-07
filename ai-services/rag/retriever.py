"""
Vector similarity search against ChromaDB, with a pure Python fallback.
"""
import os
import json
from rag.embeddings import EmbeddingModel

try:
    import chromadb  # type: ignore
    CHROMA_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    CHROMA_AVAILABLE = False

CHROMA_HOST       = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT       = int(os.getenv("CHROMA_PORT", 8001))
COLLECTION_NAME   = os.getenv("CHROMA_COLLECTION", "traffic_laws")

class Retriever:
    def __init__(self):
        self.chroma_available = CHROMA_AVAILABLE
        self.client = None
        self.collection = None
        self.fallback_db = None
        
        if self.chroma_available:
            try:
                self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
                self.collection = self.client.get_or_create_collection(COLLECTION_NAME)
            except Exception:
                try:
                    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../chroma_db"))
                    self.client = chromadb.PersistentClient(path=db_path)
                    self.collection = self.client.get_or_create_collection(COLLECTION_NAME)
                except Exception:
                    self.chroma_available = False

        if not self.chroma_available:
            self.embedder = EmbeddingModel()
            self._init_fallback_db()

    def _init_fallback_db(self):
        self.fallback_db = []
        data_path = os.path.join(os.path.dirname(__file__), "../data/violation_fines.json")
        if not os.path.exists(data_path):
            return
        try:
            with open(data_path) as f:
                laws = json.load(f)
            for law in laws:
                text = (
                    f"Violation: {law['violation']}. "
                    f"State: {law.get('state', 'National')}. "
                    f"Vehicle: {law.get('vehicle_type', 'All')}. "
                    f"Fine: ₹{law['fine_min']}–₹{law['fine_max']}. "
                    f"Section: {law.get('section', 'N/A')}. "
                    f"Penalties and Rules: {law.get('penalty_details', '')}"
                )
                vector = self.embedder.embed(text)
                self.fallback_db.append({
                    "text": text,
                    "id": str(law["id"]),
                    "section": law.get("section", ""),
                    "state": law.get("state", ""),
                    "vector": vector
                })
        except Exception as e:
            print(f"[Retriever Fallback] Failed to initialize fallback db: {e}")

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = sum(a * a for a in v1) ** 0.5
        mag2 = sum(b * b for b in v2) ** 0.5
        if mag1 * mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)

    def search(self, query_vector: list[float], state: str = "", k: int = 5) -> list[dict]:
        if self.chroma_available and self.collection:
            try:
                if state:
                    where = {"$or": [{"state": state.title()}, {"state": "National"}]}
                else:
                    where = {"state": "National"}
                results = self.collection.query(
                    query_embeddings=[query_vector],
                    n_results=k,
                    where=where,
                    include=["documents", "metadatas", "distances"]
                )
                docs = []
                if results and "documents" in results and results["documents"]:
                    for i, doc in enumerate(results["documents"][0]):
                        meta = results["metadatas"][0][i] if results["metadatas"] else {}
                        docs.append({"text": doc, "id": meta.get("law_id"), "section": meta.get("section"), **meta})
                return docs
            except Exception:
                # Fall through to pure python search on query failure
                pass

        # Pure Python fallback search
        if not self.fallback_db:
            self._init_fallback_db()
            
        scored_docs = []
        for doc in self.fallback_db:
            if state and doc["state"] and doc["state"].lower() != state.lower():
                continue
            sim = self._cosine_similarity(query_vector, doc["vector"])
            scored_docs.append((sim, doc))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        return [
            {
                "text": d["text"],
                "id": d["id"],
                "section": d["section"],
                "state": d["state"]
            }
            for _, d in scored_docs[:k]
        ]
