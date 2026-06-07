import sys
import os
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest
from app.models.chat_history import ChatHistory

# Add ai-services to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai-services")))
from rag.pipeline import RAGPipeline

pipeline = RAGPipeline()

def get_db_direct_answer(db: Session, intent: dict) -> Optional[str]:
    from typing import Optional
    from app.models.traffic import Violation, FineByState, LawSection
    
    try:
        violations = intent["violations"]
        states = intent["states"]
        
        # Primary state
        state_str = states[0] if states else ""
        if state_str.lower() in ["national", "central"]:
            state_str = ""
            
        if intent["is_comparison"] and len(violations) >= 1:
            v_cat = violations[0]
            v_rec = db.query(Violation).filter(Violation.category == v_cat).first()
            if not v_rec:
                return None
                
            s1 = states[0] if len(states) > 0 else ""
            s2 = states[1] if len(states) > 1 else ""  # if only 1 state, compare with central ("")
            
            f1 = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state.ilike(s1)).first()
            f2 = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state.ilike(s2)).first()
            
            # Fallback to central
            if not f1 and s1 != "":
                f1 = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state == "").first()
            if not f2 and s2 != "":
                f2 = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state == "").first()
                
            if not f1 or not f2:
                return None
                
            sec_rec = db.query(LawSection).filter(LawSection.violation_id == v_rec.id).first()
            sec_code = sec_rec.section_code if sec_rec else "N/A"
            act_name = sec_rec.act_name if sec_rec else "Motor Vehicles Act 2019"
            
            s1_name = s1 if s1 else "National"
            s2_name = s2 if s2 else "National"
            
            f1_str = f"₹{f1.fine_min}" if f1.fine_min == f1.fine_max else f"₹{f1.fine_min}–₹{f1.fine_max}"
            f2_str = f"₹{f2.fine_min}" if f2.fine_min == f2.fine_max else f"₹{f2.fine_min}–₹{f2.fine_max}"
            
            return (
                f"### Traffic Fine Comparison: {v_rec.name}\n\n"
                f"- **{s1_name}**: Fine is {f1_str} (Section: {sec_code}, Source: {f1.details or act_name})\n"
                f"- **{s2_name}**: Fine is {f2_str} (Section: {sec_code}, Source: {f2.details or act_name})\n\n"
                f"*Note: Comparison is pulled directly from official traffic rules and the Motor Vehicles Act.*"
            )
            
        elif intent["is_multi_violation"]:
            lines = []
            total_min = 0
            total_max = 0
            
            for v_cat in violations:
                v_rec = db.query(Violation).filter(Violation.category == v_cat).first()
                if not v_rec:
                    continue
                    
                f = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state.ilike(state_str)).first()
                if not f and state_str != "":
                    f = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state == "").first()
                    
                if f:
                    sec_rec = db.query(LawSection).filter(LawSection.violation_id == v_rec.id).first()
                    sec_code = sec_rec.section_code if sec_rec else "N/A"
                    act_name = sec_rec.act_name if sec_rec else "Motor Vehicles Act 2019"
                    
                    fine_str = f"₹{f.fine_min}" if f.fine_min == f.fine_max else f"₹{f.fine_min}–₹{f.fine_max}"
                    lines.append(f"{len(lines)+1}. **{v_rec.name}**: {fine_str} (Section: {sec_code}, Source: {act_name})")
                    total_min += f.fine_min
                    total_max += f.fine_max
                    
            if not lines:
                return None
                
            state_label = state_str if state_str else "National"
            total_fine_str = f"₹{total_min}" if total_min == total_max else f"₹{total_min}–₹{total_max}"
            
            return (
                f"### Combined Traffic Fines ({state_label})\n\n"
                f"For the multiple offenses mentioned:\n"
                + "\n".join(lines) + "\n\n"
                f"**Total Aggregated Fine**: {total_fine_str}\n\n"
                f"Source: Motor Vehicles Act 2019 / {state_label} Rules"
            )
            
        else:
            # Single violation direct lookup
            v_cat = violations[0]
            v_rec = db.query(Violation).filter(Violation.category == v_cat).first()
            if not v_rec:
                return None
                
            f = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state.ilike(state_str)).first()
            if not f and state_str != "":
                f = db.query(FineByState).filter(FineByState.violation_id == v_rec.id, FineByState.state == "").first()
                
            if f:
                sec_rec = db.query(LawSection).filter(LawSection.violation_id == v_rec.id).first()
                sec_code = sec_rec.section_code if sec_rec else "N/A"
                act_name = sec_rec.act_name if sec_rec else "Motor Vehicles Act 2019"
                
                fine_str = f"₹{f.fine_min}" if f.fine_min == f.fine_max else f"₹{f.fine_min}–₹{f.fine_max}"
                
                return (
                    f"Fine: {fine_str}  \n"
                    f"Section: {sec_code}  \n"
                    f"Source: {act_name}  \n\n"
                    f"*Details*: {f.details or 'Penalty governed by Motor Vehicles Act 2019.'}"
                )
    except Exception as e:
        print(f"[Direct DB Lookup] Error: {e}")
    return None

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, req: ChatRequest, session_id: str) -> dict:
        # Persist user message
        self.db.add(ChatHistory(session_id=session_id, role="user", content=req.message))
        self.db.commit()

        # Build location context string
        location_ctx = ""
        if req.location and req.location.state:
            location_ctx = req.location.state

        # Run intent detection
        from app.utils.detector import parse_query_intent
        intent = parse_query_intent(req.message, location_state=location_ctx)

        # Check if direct database lookup applies
        direct_answer = None
        if intent["is_direct_eligible"]:
            direct_answer = get_db_direct_answer(self.db, intent)

        if direct_answer:
            answer = direct_answer
            sources = []
            for v_cat in intent["violations"]:
                sources.append({"law_id": v_cat, "section": "Direct DB Query"})
        else:
            # Extract database record to ground the LLM if we have violations, preventing hallucinations
            db_context = ""
            if len(intent["violations"]) > 0:
                mock_intent = intent.copy()
                mock_intent["is_direct_eligible"] = True
                db_answer = get_db_direct_answer(self.db, mock_intent)
                if db_answer:
                    db_context = f"[EXACT DATABASE LAW RECORD]:\n{db_answer}\n\n"

            # Fall back to RAG
            result = await pipeline.run(
                query=req.message,
                state=location_ctx,
                language=req.language,
                mode=req.mode,
                db_context=db_context
            )
            answer = result["answer"]
            sources = result.get("sources", [])

        # Persist assistant reply
        self.db.add(ChatHistory(session_id=session_id, role="assistant", content=answer))
        self.db.commit()

        return {"content": answer, "sources": sources}

    async def stream(self, req: ChatRequest, session_id: str):
        location_ctx = ""
        if req.location and req.location.state:
            location_ctx = req.location.state
        
        # Run intent detection
        from app.utils.detector import parse_query_intent
        intent = parse_query_intent(req.message, location_state=location_ctx)
        
        direct_answer = None
        if intent["is_direct_eligible"]:
            direct_answer = get_db_direct_answer(self.db, intent)
            
        full_answer = []
        if direct_answer:
            full_answer.append(direct_answer)
            yield f"data: {direct_answer}\n\n"
        else:
            db_context = ""
            if len(intent["violations"]) > 0:
                mock_intent = intent.copy()
                mock_intent["is_direct_eligible"] = True
                db_answer = get_db_direct_answer(self.db, mock_intent)
                if db_answer:
                    db_context = f"[EXACT DATABASE LAW RECORD]:\n{db_answer}\n\n"

            # Fall back to streaming RAG
            async for chunk in pipeline.stream(req.message, state=location_ctx, mode=req.mode, db_context=db_context):
                full_answer.append(chunk)
                yield f"data: {chunk}\n\n"
                
        # Persist user message & assistant reply
        self.db.add(ChatHistory(session_id=session_id, role="user", content=req.message))
        self.db.add(ChatHistory(session_id=session_id, role="assistant", content="".join(full_answer)))
        self.db.commit()
        
        yield "data: [DONE]\n\n"

    async def handle_multimodal(self, file_bytes: bytes, mime_type: str, session_id: str) -> str:
        from llm.gemini_client import GeminiClient
        client = GeminiClient()
        
        prompt = """You are DriveLegal AI. Look at this uploaded Traffic Challan image or document.
Extract the following information in a clear format:
- Violation details (e.g. No Helmet, Speeding)
- Vehicle Number (if visible)
- Fine Amount (₹)
- Challan Number & Date
- Offense Location & State

Provide a simple, clear, and layperson-friendly breakdown of what this means, what section of the Motor Vehicles Act it references, and immediate steps the user should take (e.g. how/where to pay)."""
        
        answer = await client.complete_multimodal(
            prompt=prompt,
            file_bytes=file_bytes,
            mime_type=mime_type
        )
        
        # Persist the interaction in the chat history
        self.db.add(ChatHistory(session_id=session_id, role="user", content=f"[Uploaded Document]"))
        self.db.add(ChatHistory(session_id=session_id, role="assistant", content=answer))
        self.db.commit()
        
        return answer
