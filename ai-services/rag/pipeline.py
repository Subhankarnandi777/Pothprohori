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

    def _get_web_search_context(self, query: str, state: str) -> list[dict]:
        # Determine if web search fallback is needed
        need_web_search = False
        
        # 1. Trigger if query mentions states outside our primary local rules (WB, Delhi, Maharashtra)
        unindexed_states = ["karnataka", "tamil", "kerala", "up", "uttar", "gujarat", "punjab", "haryana", "bihar", "rajasthan", "mp", "madhya", "andhra", "telangana", "odisha", "assam", "goa"]
        query_lower = query.lower()
        if any(s in query_lower for s in unindexed_states):
            need_web_search = True
        elif state and state.lower() not in ["west bengal", "delhi", "maharashtra"]:
            need_web_search = True
            
        web_docs = []
        if need_web_search:
            try:
                from tools.web_search import web_search
                print(f"[RAG Fallback] Query requires live web search context. Searching for: '{query}'")
                web_results = web_search(query)
                for res in web_results:
                    web_docs.append({
                        "text": f"Source: {res['title']} ({res['url']})\nSnippet: {res['snippet']}",
                        "id": f"web_{hash(res['url'])}",
                        "section": "Web Search Fallback",
                        "url": res["url"]
                    })
            except Exception as e:
                print(f"[RAG Pipeline] Web search fallback failed: {e}")
        return web_docs

    async def run(self, query: str, state: str = "", language: str = "en", mode: str = "standard", db_context: str = "") -> dict:
        # 1. Embed the query
        query_vector = self.embedder.embed(query)

        # 2. Retrieve top-K relevant law chunks
        docs = self.retriever.search(query_vector, state=state, k=3)

        # 3. Dynamic Web Search Fallback if no local rules matched or unindexed state requested
        web_docs = []
        if not docs or state.lower() not in ["", "west bengal", "delhi", "maharashtra"] or any(s in query.lower() for s in ["karnataka", "kerala", "tamil"]):
            web_docs = self._get_web_search_context(query, state)

        # 4. Build prompt
        all_docs = docs + web_docs
        context = db_context + "\n\n".join([d["text"] for d in all_docs])
        system  = build_system_prompt(state=state, language=language, mode=mode)
        user    = build_user_prompt(query=query, context=context)

        # 5. Call LLM
        answer = await self.llm.complete(system=system, user=user)

        sources = [{"law_id": d.get("id"), "section": d.get("section"), "url": d.get("url", "")} for d in all_docs]
        return {"answer": answer, "sources": sources}

    async def stream(self, query: str, state: str = "", mode: str = "standard", db_context: str = ""):
        query_vector = self.embedder.embed(query)
        docs = self.retriever.search(query_vector, state=state, k=3)

        web_docs = []
        if not docs or state.lower() not in ["", "west bengal", "delhi", "maharashtra"] or any(s in query.lower() for s in ["karnataka", "kerala", "tamil"]):
            web_docs = self._get_web_search_context(query, state)

        all_docs = docs + web_docs
        context = db_context + "\n\n".join([d["text"] for d in all_docs])
        system = build_system_prompt(state=state, mode=mode)
        user   = build_user_prompt(query=query, context=context)
        async for chunk in self.llm.stream(system=system, user=user):
            yield chunk
