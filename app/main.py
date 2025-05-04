from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.knowledge.router import router as knowledge_router
from app.chat.router import router as chat_router

app = FastAPI(
    title="Skripsi Chatbot API",
    description="Backend API for RAG-based Skripsi Information Chatbot",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
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