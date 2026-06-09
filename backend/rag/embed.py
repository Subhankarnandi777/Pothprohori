"""
Wraps an embedding model.
Uses HuggingFace's all-MiniLM-L6-v2 to match the trained FAISS model.
"""
import os

class EmbeddingModel:
    def __init__(self):
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.available = True
        except ImportError:
            self.available = False

    def embed(self, text: str) -> list[float]:
        if self.available:
            try:
                return self.model.embed_query(text)
            except Exception:
                return self._stub_embed(text)
        return self._stub_embed(text)

    def _stub_embed(self, text: str) -> list[float]:
        # Fallback to stub if HF models fail to load
        import hashlib
        h = int(hashlib.md5(text.encode()).hexdigest(), 16)
        # Match the 384 dimensions of MiniLM
        return [(h >> (i % 16) & 0xFF) / 255.0 for i in range(384)]
