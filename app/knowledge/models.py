from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import os
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
    created_at = Column(DateTime, nullable=True)  # Remove default, set manually

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
    file_name: Optional[str]  # Pastikan ini opsional untuk menghindari error jika None
    
    @field_validator('file_name', mode="before")
    def extract_file_name(cls, v, values):
        if not v and 'file_path' in values and values['file_path']:
            return os.path.basename(values['file_path'])
        return v
    
    class Config:
        from_attributes = True

class KnowledgeSourceList(BaseModel):
    items: List[KnowledgeSourceResponse]
    total: int