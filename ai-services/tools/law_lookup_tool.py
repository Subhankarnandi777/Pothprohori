"""
LLM function-calling tool: look up a law by keyword.
"""
def lookup_law(keyword: str, state: str = "") -> dict:
    # Placeholder — wire to RAG retriever in production
    return {"keyword": keyword, "state": state, "result": "Use RAG pipeline for real lookup."}
