"""
OpenAI GPT-4 client wrapper (fallback LLM).
"""
import os
from openai import AsyncOpenAI

class OpenAIClient:
    def __init__(self):
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            self.client = AsyncOpenAI(api_key=openai_key)
        else:
            self.client = None

    async def complete(self, system: str, user: str) -> str:
        if not self.client:
            return "[STUB] OpenAI API key not set."
        response = await self.client.chat.completions.create(
            model="gpt-4o", # corrected from gpt-4.1 to gpt-4o or similar valid model
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}]
        )
        return response.choices[0].message.content

    async def stream(self, system: str, user: str):
        if not self.client:
            yield "[STUB] OpenAI API key not set."
            return
        stream = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
