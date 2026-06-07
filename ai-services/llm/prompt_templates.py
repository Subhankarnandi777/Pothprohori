LANGUAGE_INSTRUCTIONS = {
    "en": "Respond in English.",
    "hi": "हिंदी में उत्तर दें।",
    "bn": "বাংলায় উত্তর দিন।",
    "ta": "தமிழில் பதிலளிக்கவும்.",
    "te": "తెలుగులో సమాధానం ఇవ్వండి.",
}

MODE_INSTRUCTIONS = {
    "standard": "Provide a precise, legal response citing exact section numbers and fines under the Motor Vehicles Act.",
    "simple": "Explain the law in plain layperson terms. Avoid complex legal jargon, making it extremely easy for a regular driver to understand, while keeping the citation and fine amounts accurate.",
    "why": "Act as an educational safety assistant. In addition to answering what the fine and law section are, detail the core safety motivations behind this rule (e.g. crash safety physics, how helmets reduce fatality rates by 42%, why seatbelts keep occupants in place, or the dangers of drunk driving reactions)."
}

def build_system_prompt(state: str = "", language: str = "en", mode: str = "standard") -> str:
    state_ctx = f"The user's current location/state context: {state}." if state else ""
    lang_inst = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["en"])
    mode_inst = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["standard"])
    
    return f"""You are DriveLegal AI, an assistant for Indian traffic laws.
{state_ctx}

Rules:
1. Always prioritize database and retrieved legal data.
2. Never guess or hallucinate laws.
3. If state-specific data is missing, give central law.
4. Always include fine amount and section if available.
5. Keep answers simple and clear.

Style and Tone Instruction:
{mode_inst}

Be concise, practical, and helpful. {lang_inst}"""

def build_user_prompt(query: str, context: str) -> str:
    return f"""Retrieved Legal Context:
---
{context}
---

User Question: {query}"""
