from sqlalchemy import Column, Integer, String, DateTime, func
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.database import Base

# SQLAlchemy Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # 'admin' or 'student'
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Pydantic Models
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None