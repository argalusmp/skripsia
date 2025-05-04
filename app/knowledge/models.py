from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import Base

# SQLAlchemy Models
class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    file_path = Column(String)
    file_type = Column(String)  # 'pdf', 'doc', 'image', 'audio'
    status = Column(String, default="processing")  # 'processing', 'completed', 'failed'
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User")

# Pydantic Models
class KnowledgeSourceBase(BaseModel):
    title: str
    file_type: str

class KnowledgeSourceCreate(KnowledgeSourceBase):
    pass

class KnowledgeSourceResponse(KnowledgeSourceBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class KnowledgeSourceList(BaseModel):
    items: List[KnowledgeSourceResponse]
    total: int