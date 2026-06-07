import uuid
import sys
import os

# Add ai-services to python path to resolve tool imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../ai-services"))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.chat import ChatRequest, ChatResponse, ChallanRequest, ChallanResponse
from app.services.chat_service import ChatService
from app.core.database import get_db
from tools.challan_tool import calculate_challan  # type: ignore

router = APIRouter()
MAX_CHALLAN_IMAGE_SIZE = 5 * 1024 * 1024
SUPPORTED_CHALLAN_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id or str(uuid.uuid4())
    try:
        service = ChatService(db)
        response = await service.handle(request, session_id)
        return ChatResponse(content=response["content"],
                            session_id=session_id,
                            sources=response.get("sources", []))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id or str(uuid.uuid4())
    service = ChatService(db)
    return StreamingResponse(
        service.stream(request, session_id),
        media_type="text/event-stream"
    )

@router.post("/calculate-challan", response_model=ChallanResponse)
async def calculate_challan_endpoint(request: ChallanRequest, db: Session = Depends(get_db)):
    try:
        from app.models.traffic import Violation, FineByState, LawSection
        
        # 1. Match violation
        v_cat = request.violation.lower().replace(" ", "_")
        v_rec = db.query(Violation).filter(
            (Violation.category == request.violation.lower()) | 
            (Violation.category == v_cat) |
            (Violation.name.ilike(request.violation)) |
            (Violation.name.ilike(f"%{request.violation}%"))
        ).first()
        
        if not v_rec:
            raise HTTPException(status_code=404, detail=f"Violation '{request.violation}' not found in database.")
            
        # Check if the violation is compatible with the selected vehicle type
        compatible_entry = db.query(FineByState).filter(
            FineByState.violation_id == v_rec.id,
            FineByState.vehicle_type.in_([request.vehicle_type, "all"])
        ).first()
        
        if not compatible_entry:
            vehicle_labels = {
                "2W": "2-Wheeler",
                "3W": "3-Wheeler",
                "4W": "Car / LMV",
                "HV": "Truck / Heavy Vehicle"
            }
            vehicle_label = vehicle_labels.get(request.vehicle_type, request.vehicle_type)
            return ChallanResponse(
                violation=v_rec.name,
                state=request.state or "National",
                fine_inr=0,
                repeat=request.repeat,
                section="N/A",
                explanation=(
                    f"Not Applicable: '{v_rec.name}' does not apply to {vehicle_label} vehicles. "
                    f"Please select a compatible vehicle class."
                )
            )
            
        # 2. Get fine for state and vehicle type (or fallback)
        state_str = request.state or ""
        if state_str.lower() in ["national", "central"]:
            state_str = ""
            
        if state_str:
            has_state_fine = db.query(FineByState).filter(
                FineByState.violation_id == v_rec.id,
                FineByState.state.ilike(state_str)
            ).first()
            
            if not has_state_fine:
                from tools.web_search import web_search
                from llm.gemini_client import GeminiClient
                import json
                
                search_query = f"fine amount for {v_rec.name} in {state_str} {request.vehicle_type or ''}"
                print(f"[Calculator Fallback] Running live search for: '{search_query}'")
                search_results = web_search(search_query)
                
                context_list = []
                for res in search_results:
                    context_list.append(f"Source: {res['title']} ({res['url']})\nSnippet: {res['snippet']}")
                context_text = "\n\n".join(context_list)
                
                gemini = GeminiClient()
                prompt = f"""You are a precise traffic law JSON extractor. Based on the following web search snippets, extract the traffic fine amount (in INR, integer only) and the law section code for the violation '{v_rec.name}' in {state_str} for a {request.vehicle_type} vehicle.
                
                Search Context:
                {context_text}
                
                Rules:
                1. Return ONLY a valid JSON object. Do not include any other text or markdown formatting (like ```json).
                2. The JSON object must contain these exact keys:
                   - "fine_inr": integer fine amount (e.g., 1000)
                   - "section": string section code (e.g., "194D")
                   - "explanation": string detailing the fine, state procedure, and source URL citation.
                3. If no information is found in the search context, default to the central Motor Vehicles Act 2019 fine values.
                """
                
                try:
                    raw_response = await gemini.complete(
                        system="You are a precise traffic law JSON extractor.",
                        user=prompt
                    )
                    cleaned_resp = raw_response.strip()
                    if cleaned_resp.startswith("```json"):
                        cleaned_resp = cleaned_resp.replace("```json", "", 1)
                    if cleaned_resp.endswith("```"):
                        cleaned_resp = cleaned_resp[:-3].strip()
                    cleaned_resp = cleaned_resp.strip()
                    
                    extracted_data = json.loads(cleaned_resp)
                    
                    return ChallanResponse(
                        violation=v_rec.name,
                        state=state_str,
                        fine_inr=extracted_data.get("fine_inr", 0),
                        repeat=request.repeat,
                        section=extracted_data.get("section", "N/A"),
                        explanation=extracted_data.get("explanation", "")
                    )
                except Exception as ex:
                    print(f"[Calculator Fallback] Failed to extract from web search: {ex}")
            
        # First, try matching the specific state and vehicle type
        fine_entry = db.query(FineByState).filter(
            FineByState.violation_id == v_rec.id,
            FineByState.state.ilike(state_str),
            FineByState.vehicle_type == request.vehicle_type
        ).first()
        
        # If not found, try matching the specific state with "all" vehicles
        if not fine_entry:
            fine_entry = db.query(FineByState).filter(
                FineByState.violation_id == v_rec.id,
                FineByState.state.ilike(state_str),
                FineByState.vehicle_type == "all"
            ).first()
            
        # If not found, fall back to any vehicle type for this state
        if not fine_entry:
            fine_entry = db.query(FineByState).filter(
                FineByState.violation_id == v_rec.id,
                FineByState.state.ilike(state_str)
            ).first()
            
        # If not found and a specific state was requested, fall back to national/central rules
        if not fine_entry and state_str != "":
            # Try national/central and specific vehicle type
            fine_entry = db.query(FineByState).filter(
                FineByState.violation_id == v_rec.id,
                FineByState.state == "",
                FineByState.vehicle_type == request.vehicle_type
            ).first()
            
            # Try national/central and "all" vehicles
            if not fine_entry:
                fine_entry = db.query(FineByState).filter(
                    FineByState.violation_id == v_rec.id,
                    FineByState.state == "",
                    FineByState.vehicle_type == "all"
                ).first()
                
            # Try national/central and any vehicle type
            if not fine_entry:
                fine_entry = db.query(FineByState).filter(
                    FineByState.violation_id == v_rec.id,
                    FineByState.state == ""
                ).first()
            
        if not fine_entry:
            raise HTTPException(status_code=404, detail="Fine details not found in database.")
            
        # 3. Determine fine amount
        amount = fine_entry.fine_repeat_max if request.repeat else fine_entry.fine_max
        amount = amount or fine_entry.fine_max or 0
        
        # 4. Get section
        sec_rec = db.query(LawSection).filter(LawSection.violation_id == v_rec.id).first()
        section = sec_rec.section_code if sec_rec else "N/A"
        act_name = sec_rec.act_name if sec_rec else "Motor Vehicles Act 2019"
        
        offense_type = "repeat" if request.repeat else "first"
        explanation = (
            f"Fine of ₹{amount} calculated for {v_rec.name} ({request.vehicle_type}) "
            f"in {request.state or 'National'} ({offense_type} offense) under {act_name}."
        )
        
        return ChallanResponse(
            violation=v_rec.name,
            state=request.state or "National",
            fine_inr=amount,
            repeat=request.repeat,
            section=section,
            explanation=explanation
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    session_id = session_id or str(uuid.uuid4())
    try:
        if file.content_type not in SUPPORTED_CHALLAN_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Upload a PNG, JPG, or JPEG challan image."
            )

        contents = await file.read()
        if len(contents) > MAX_CHALLAN_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File is too large. Upload a challan image up to 5MB."
            )
        
        # Call Gemini client multimodal completed OCR
        service = ChatService(db)
        response_text = await service.handle_multimodal(contents, file.content_type, session_id)
        
        return {
            "content": response_text,
            "session_id": session_id,
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    try:
        from app.models.chat_history import ChatHistory
        sessions = db.query(ChatHistory.session_id).distinct().all()
        return [s[0] for s in sessions if s[0]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    try:
        from app.models.chat_history import ChatHistory
        history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.asc()).all()
        return [
            {"role": h.role, "content": h.content, "created_at": h.created_at.isoformat() if h.created_at else None}
            for h in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
