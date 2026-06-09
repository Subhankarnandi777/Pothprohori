"""
Chatbot agent with tool-use loop.
Currently wraps RAGPipeline directly.
Extend here to add multi-step reasoning or LangChain agent.
"""
from ingestion.pipeline import RAGPipeline

class ChatbotAgent:
    def __init__(self):
        self.pipeline = RAGPipeline()

    async def run(self, query: str, state: str = "", language: str = "en") -> dict:
        return await self.pipeline.run(query=query, state=state, language=language)
