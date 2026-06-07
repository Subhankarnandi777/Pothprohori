"""
Gemini Pro client wrapper (primary LLM).
"""
import os
import google.generativeai as genai

class GeminiClient:
    def __init__(self):
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

    async def complete(self, system: str, user: str) -> str:
        if not self.model:
            return "[STUB] Gemini API key not set. Set GEMINI_API_KEY in .env"
        prompt = f"{system}\n\n{user}"
        response = self.model.generate_content(prompt)
        return response.text

    async def stream(self, system: str, user: str):
        if not self.model:
            yield "[STUB] Gemini API key not set."
            return
        prompt = f"{system}\n\n{user}"
        for chunk in self.model.generate_content(prompt, stream=True):
            if chunk.text:
                yield chunk.text

    async def complete_multimodal(self, prompt: str, file_bytes: bytes, mime_type: str) -> str:
        if not self.model:
            return (
                "[STUB OCR] Gemini API key not set.\n\n"
                "### Mocked Challan OCR Output:\n"
                "- **Violation:** Riding without Helmet\n"
                "- **Vehicle Number:** DL-3S-CQ-1234\n"
                "- **Fine Amount:** ₹1,000\n"
                "- **Challan Number:** CH-9876543\n"
                "- **Section:** Section 194D, Motor Vehicles Act 2019\n"
                "- **Suggested Action:** Please visit [echallan.parivahan.gov.in](https://echallan.parivahan.gov.in) to pay online within 60 days."
            )
        try:
            image_part = {
                "mime_type": mime_type,
                "data": file_bytes
            }
            # gemini-1.5-pro handles image objects directly in a list
            response = self.model.generate_content([prompt, image_part])
            return response.text
        except Exception as e:
            return f"Error executing multimodal Gemini OCR: {str(e)}"
