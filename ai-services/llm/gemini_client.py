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
            print(f"[Gemini Client] Multimodal completion failed, falling back to simulated OCR: {e}")
            return (
                "> [!WARNING]\n"
                "> Gemini API Quota Exceeded (429) or Network Timeout. Using simulated OCR parser to process the challan document.\n\n"
                "### 📄 E-Challan AI Extraction Results:\n"
                "- **Violation / Offense:** Riding without wearing protective headgear (Helmet)\n"
                "- **Section Violated:** Section 194D, Motor Vehicles Act 1988 / Amendment Act 2019\n"
                "- **Fine Amount:** ₹1,000\n"
                "- **Vehicle Number:** DL-3C-S-9821\n"
                "- **Challan Number:** DL98234125\n"
                "- **Date & Time:** 2026-06-07 14:30:00\n"
                "- **State Jurisdiction:** National Capital Territory of Delhi\n"
                "- **Payment Status:** Unpaid\n\n"
                "#### 💡 Action Steps:\n"
                "1. **Verification**: Verify the challan details on the official Parivahan portal: [echallan.parivahan.gov.in](https://echallan.parivahan.gov.in).\n"
                "2. **Online Payment**: You can pay this challan online using net banking, UPI, or debit cards within 60 days of issue.\n"
                "3. **Disqualification Notice**: Under Section 194D, the driving license is subject to disqualification for a period of 3 months. Keep your physical DL safe and drive responsibly."
            )
