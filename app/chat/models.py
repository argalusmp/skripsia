from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import Base

# SQLAlchemy Models
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("User")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    conversation = relationship("Conversation", back_populates="messages")

# Pydantic Models
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    message: MessageResponse
    conversation_id: int