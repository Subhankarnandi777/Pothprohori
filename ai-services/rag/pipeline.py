"""
Main RAG orchestrator.
Flow: query → embed → retrieve → build prompt → LLM → return answer
"""
from rag.retriever import Retriever
from rag.embeddings import EmbeddingModel
from llm.gemini_client import GeminiClient
from llm.prompt_templates import build_system_prompt, build_user_prompt

class RAGPipeline:
    def __init__(self):
        self.retriever  = Retriever()
        self.embedder   = EmbeddingModel()
        self.llm        = GeminiClient()

    async def run(self, query: str, state: str = "", language: str = "en", mode: str = "standard", db_context: str = "") -> dict:
        # 1. Embed the query
        query_vector = self.embedder.embed(query)

        # 2. Retrieve top-K relevant law chunks
        docs = self.retriever.search(query_vector, state=state, k=3)

        # 3. Build prompt
        context = db_context + "\n\n".join([d["text"] for d in docs])
        system  = build_system_prompt(state=state, language=language, mode=mode)
        user    = build_user_prompt(query=query, context=context)

        # 4. Call LLM
        answer = await self.llm.complete(system=system, user=user)

        sources = [{"law_id": d.get("id"), "section": d.get("section")} for d in docs]
        return {"answer": answer, "sources": sources}

    async def stream(self, query: str, state: str = "", mode: str = "standard", db_context: str = ""):
        query_vector = self.embedder.embed(query)
        docs = self.retriever.search(query_vector, state=state, k=3)
        context = db_context + "\n\n".join([d["text"] for d in docs])
        system = build_system_prompt(state=state, mode=mode)
        user   = build_user_prompt(query=query, context=context)
        async for chunk in self.llm.stream(system=system, user=user):
            yield chunk
