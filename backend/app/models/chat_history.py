from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String(100), primary_key=True, index=True) # UUID string
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String(200), default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    user = relationship("User")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role       = Column(String(20))   # "user" | "assistant"
    content    = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # relationship
    session = relationship("ChatSession")
