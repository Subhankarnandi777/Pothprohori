"""
Vector similarity search against FAISS, with a pure Python fallback.
"""
import os
import json
from rag.embed import EmbeddingModel

try:
    from langchain_community.vectorstores import FAISS
    FAISS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    FAISS_AVAILABLE = False

class Retriever:
    def __init__(self):
        self.faiss_available = FAISS_AVAILABLE
        self.vectorstore = None
        self.fallback_db = None
        self.embedder = EmbeddingModel()
        
        if self.faiss_available and self.embedder.available:
            try:
                db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../embeddings"))
                if os.path.exists(os.path.join(db_path, "index.faiss")):
                    self.vectorstore = FAISS.load_local(db_path, self.embedder.model, allow_dangerous_deserialization=True)
                else:
                    self.faiss_available = False
            except Exception as e:
                print(f"[FAISS Retriever] Failed to load index from {db_path}: {e}")
                self.faiss_available = False

        if not self.faiss_available:
            self._init_fallback_db()

    def _init_fallback_db(self):
        self.fallback_db = []
        data_path = os.path.join(os.path.dirname(__file__), "../../data/violation_fines.json")
        if not os.path.exists(data_path):
            return
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                laws = json.load(f)
            for law in laws:
                text = (
                    f"Violation: {law.get('violation', '')}. "
                    f"State: {law.get('state', 'National')}. "
                    f"Vehicle: {law.get('vehicle_type', 'All')}. "
                    f"Fine: ₹{law.get('fine_min', 0)}–₹{law.get('fine_max', 0)}. "
                    f"Section: {law.get('section', 'N/A')}. "
                    f"Penalties and Rules: {law.get('penalty_details', '')}"
                )
                vector = self.embedder.embed(text)
                self.fallback_db.append({
                    "text": text,
                    "id": str(law.get("id", "")),
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
        # Actually FAISS similarity_search takes a string query, but since the pipeline embeds it first, 
        # we can use similarity_search_by_vector
        if self.faiss_available and self.vectorstore:
            try:
                # Assuming state filtering isn't perfectly supported in simple FAISS without a metadata filter dict,
                # we'll fetch more and filter manually if state is provided
                search_k = k * 3 if state else k
                results = self.vectorstore.similarity_search_by_vector(query_vector, k=search_k)
                docs = []
                for doc in results:
                    meta = doc.metadata or {}
                    # Add to docs if state matches or no state requested
                    # Since we chunked texts without state metadata, we just return the chunks
                    docs.append({
                        "text": doc.page_content, 
                        "id": meta.get("chunk_id", ""), 
                        "section": meta.get("section", ""),
                        "state": meta.get("state", "")
                    })
                
                # Manual state filtering if metadata had state (currently chunks don't have state mapped yet)
                # For now, we just return top k
                return docs[:k]
            except Exception as e:
                print(f"[FAISS Retriever] Search failed: {e}")
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
