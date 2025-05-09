import logging
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.auth.dependencies import get_current_admin
from app.database import get_db
from app.knowledge.models import KnowledgeSource, KnowledgeSourceResponse, KnowledgeSourceList
from app.knowledge.service import process_knowledge_source
from app.users.models import User
from app.config import settings

router = APIRouter()

@router.post("/upload", response_model=KnowledgeSourceResponse)
async def upload_knowledge_source(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension in ['.pdf', '.docx', '.doc']:
        file_type = 'document'
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        file_type = 'image'
    elif file_extension in ['.mp3', '.wav', 'm4a']:
        file_type = 'audio'
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Supported types: PDF, DOCX, JPG, PNG, MP3, WAV, M4A."
        )
    
    # Create directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{title}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database entry
    db_knowledge = KnowledgeSource(
        title=title,
        file_path=file_path,
        file_type=file_type,
        uploaded_by=current_user.id
    )
    
    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)
    
    # Process knowledge source in background
    background_tasks.add_task(
        process_knowledge_source, 
        db_knowledge.id, 
        file_path, 
        file_type
    )
    
    return db_knowledge

@router.get("/", response_model=KnowledgeSourceList)
async def list_knowledge_sources(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total = db.query(KnowledgeSource).count()
    items = db.query(KnowledgeSource).offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}

@router.get("/{knowledge_id}", response_model=KnowledgeSourceResponse)
async def get_knowledge_source(
    knowledge_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    knowledge = db.query(KnowledgeSource).filter(KnowledgeSource.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    
    return knowledge

from app.vector_store.pinecone_client import get_vector_store

@router.delete("/{knowledge_id}", status_code=200)
async def delete_knowledge_source(
    knowledge_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Query the knowledge source
    knowledge = db.query(KnowledgeSource).filter(KnowledgeSource.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    
    # Delete the file if it exists
    if os.path.exists(knowledge.file_path):
        os.remove(knowledge.file_path)
    
    # Delete related vectors from Pinecone
    vector_store = get_vector_store()
    try:
        vector_store._index.delete(filter={"source_id": knowledge_id})
    except Exception as e:
        logging.error(f"Failed to delete vectors from Pinecone: {e}")
    
    # Delete the knowledge source from the database
    db.delete(knowledge)
    db.commit()
    
    return {"detail": "Knowledge source deleted successfully"}