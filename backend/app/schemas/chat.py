from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class LocationInput(BaseModel):
    state: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "en"
    location: Optional[LocationInput] = None
    mode: str = "standard"  # "standard" | "simple" | "why"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    content: str
    session_id: str
    sources: List[Dict[str, Any]] = []

class ChallanRequest(BaseModel):
    violation: str
    state: Optional[str] = ""
    vehicle_type: str = "all"
    repeat: bool = False

class ChallanResponse(BaseModel):
    violation: str
    state: str
    fine_inr: int
    repeat: bool
    section: str
    explanation: str
