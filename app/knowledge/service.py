import logging
from sqlalchemy.orm import Session
import os
from app.database import SessionLocal
from app.knowledge.models import KnowledgeSource
from app.knowledge.processor import extract_text_from_document, extract_text_from_image, extract_text_from_audio
from app.vector_store.pinecone_client import store_chunks_in_pinecone
from app.config import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_knowledge_source(source_id: int, file_path: str, file_type: str):
    """Process knowledge source file and store in vector database"""
    try:
        logger.info(
            f"Processing knowledge source {source_id} of type {file_type}")

        # Extract text based on file type
        text = ""
        if file_type == "document":
            text = extract_text_from_document(file_path)
        elif file_type == "image":
            text = extract_text_from_image(file_path)
        elif file_type == "audio":
            text = extract_text_from_audio(file_path)

        if not text:
            raise ValueError(f"No text extracted from file: {file_path}")

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = text_splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")

        # Prepare metadata
        file_name = os.path.basename(file_path)
        metadata = [{"source": file_name, "source_id": source_id, "chunk": i}
                    for i in range(len(chunks))]

        # Store in vector database
        store_chunks_in_pinecone(
            chunks,
            metadata,
            [f"source_{source_id}_chunk_{i}" for i in range(len(chunks))]
        )

        # Update source status
        with SessionLocal() as db:
            knowledge_source = db.query(KnowledgeSource).filter(
                KnowledgeSource.id == source_id).first()
            if knowledge_source:
                knowledge_source.status = "completed"
                db.commit()
                logger.info(
                    f"Knowledge source {source_id} processing completed")
            else:
                logger.error(f"Knowledge source {source_id} not found in DB")

    except Exception as e:
        logger.error(
            f"Error processing knowledge source {source_id}: {str(e)}")

        # Update source status to failed
        with SessionLocal() as db:
            knowledge_source = db.query(KnowledgeSource).filter(
                KnowledgeSource.id == source_id).first()
            if knowledge_source:
                knowledge_source.status = "failed"
                db.commit()
                logger.info(f"Knowledge source {source_id} marked as failed")


def extract_file_metadata(file_path):
    """Extract metadata from file like creation date, size, etc."""
    try:
        file_stats = os.stat(file_path)
        file_name = os.path.basename(file_path)
        file_size = file_stats.st_size
        file_extension = os.path.splitext(file_name)[1].lower()

        return {
            "file_name": file_name,
            "file_size": file_size,
            "file_extension": file_extension,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime)
        }
    except Exception as e:
        logger.error(f"Error extracting file metadata: {e}")
        return {}
