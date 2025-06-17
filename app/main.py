from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime, timezone

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.knowledge.router import router as knowledge_router
from app.chat.router import router as chat_router

app = FastAPI(
    title="Skripsi Chatbot API",
    description="Backend API for RAG-based Skripsi Information Chatbot",
    version="1.0.0"
)

# Custom JSON encoder for datetime with timezone
def custom_json_encoder(obj):
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=timezone.utc)
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://skripsia-fe.vercel.app",
        "http://localhost:3000",
        "http://143.198.214.90",
        "https://vidimarpaung.tech"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge Base"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to Skripsi Chatbot API"}