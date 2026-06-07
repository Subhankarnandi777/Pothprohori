"""
Wraps an embedding model.
Uses Google's embedding-001 by default (free tier).
Falls back to a simple hash-based stub if no API key set.
"""
import os

class EmbeddingModel:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.use_google = bool(self.api_key)

    def embed(self, text: str) -> list[float]:
        if self.use_google:
            try:
                return self._google_embed(text)
            except Exception as e:
                # Handle any API failure or library import failure gracefully
                return self._stub_embed(text)
        return self._stub_embed(text)

    def _google_embed(self, text: str) -> list[float]:
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]

    def _stub_embed(self, text: str) -> list[float]:
        # Deterministic stub — replace with real model in production
        import hashlib
        h = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(h >> i & 0xFF) / 255.0 for i in range(768)]
