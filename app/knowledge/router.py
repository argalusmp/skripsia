import logging
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.vector_store.pinecone_client import get_vector_store
from app.auth.dependencies import get_current_admin, get_current_user
from app.database import get_db
from app.knowledge.models import KnowledgeSource, KnowledgeSourceResponse, KnowledgeSourceList
from app.knowledge.service import process_knowledge_source
from app.users.models import User
from app.config import settings
import mimetypes
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI
from fastapi import Request

app = FastAPI()
router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Tambahkan ke middleware
app.add_middleware(SlowAPIMiddleware)


@router.post("/upload", response_model=KnowledgeSourceResponse)
async def upload_knowledge_source(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
     # Log file details
    logging.info(f"Received file: {file.filename}")
    file_extension = os.path.splitext(file.filename)[1].lower()
    logging.info(f"File extension: {file_extension}")

    if file_extension in ['.pdf', '.docx', '.doc']:
        file_type = 'document'
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        file_type = 'image'
    elif file_extension in ['.mp3', '.wav', '.m4a']:
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

     # Convert SQLAlchemy object to Pydantic model
    return KnowledgeSourceResponse(
        id=db_knowledge.id,
        title=db_knowledge.title,
        file_type=db_knowledge.file_type,
        status=db_knowledge.status,
        created_at=db_knowledge.created_at,
        file_name=os.path.basename(db_knowledge.file_path)
    )


@router.get("/", response_model=KnowledgeSourceList)
async def list_knowledge_sources(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total = db.query(KnowledgeSource).count()
    items = db.query(KnowledgeSource).offset(skip).limit(limit).all()

     # Convert SQLAlchemy objects to Pydantic models
    response_items = [
        KnowledgeSourceResponse(
            id=item.id,
            title=item.title,
            file_type=item.file_type,
            status=item.status,
            created_at=item.created_at,
            file_name=os.path.basename(item.file_path) if item.file_path else None
        )
        for item in items
    ]

    return {"items": response_items, "total": total}


@router.get("/{knowledge_id}", response_model=KnowledgeSourceResponse)
async def get_knowledge_source(
    knowledge_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    knowledge = db.query(KnowledgeSource).filter(
        KnowledgeSource.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(
            status_code=404, detail="Knowledge source not found")

    return knowledge


@router.delete("/{knowledge_id}", status_code=200)
async def delete_knowledge_source(
    knowledge_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Query the knowledge source
    knowledge = db.query(KnowledgeSource).filter(
        KnowledgeSource.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(
            status_code=404, detail="Knowledge source not found")

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


@router.get("/file/{knowledge_id}", response_class=Response)
@limiter.limit("10/minute")
async def get_knowledge_file(
    request: Request,
    knowledge_id: int,
    # Menggunakan get_current_user bukan admin
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Query the knowledge source
    knowledge = db.query(KnowledgeSource).filter(
        KnowledgeSource.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(
            status_code=404, detail="Knowledge source not found")

    # Check if file exists
    if not os.path.exists(knowledge.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # Get file MIME type
    mime_type, _ = mimetypes.guess_type(knowledge.file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Return file as response
    return FileResponse(
        path=knowledge.file_path,
        filename=os.path.basename(knowledge.file_path),
        media_type=mime_type
    )


@router.get("/preview/{knowledge_id}")
async def preview_knowledge_source(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    knowledge = db.query(KnowledgeSource).filter(
        KnowledgeSource.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(
            status_code=404, detail="Knowledge source not found")

    file_path = knowledge.file_path
    file_type = knowledge.file_type
    file_name = os.path.basename(file_path)

    # Generate signed URL or token for frontend to access
    # This is a simple implementation - could be enhanced with temporary tokens
    preview_data = {
        "id": knowledge.id,
        "title": knowledge.title,
        "file_name": file_name,
        "file_type": file_type,
        "file_url": f"/knowledge/file/{knowledge.id}",
        "created_at": knowledge.created_at
    }

    return preview_data
