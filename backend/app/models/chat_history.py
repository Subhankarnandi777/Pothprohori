from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    role       = Column(String(20))   # "user" | "assistant"
    content    = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
