import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Skripsi Chatbot API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 5  # 5 Hours
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    # Groq settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    # Mistral settings
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY")
    
    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "ragv2")
    
    # File storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    # Add these to your Settings class
    DO_SPACE_REGION: str = os.getenv("DO_SPACE_REGION")
    DO_SPACE_ENDPOINT: str = os.getenv("DO_SPACE_ENDPOINT")
    DO_SPACE_KEY: str = os.getenv("DO_SPACE_KEY")
    DO_SPACE_SECRET: str = os.getenv("DO_SPACE_SECRET")
    DO_SPACE_NAME: str = os.getenv("DO_SPACE_NAME")
    USE_SPACES: bool = os.getenv("USE_SPACES", "false").lower() == "true"

# Create a settings instance
settings = Settings()

# For backward compatibility
def setup_environment():
    """For compatibility with older code"""
    return {
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "GROQ_API_KEY": settings.GROQ_API_KEY,
        "MISTRAL_API_KEY": settings.MISTRAL_API_KEY,
        "PINECONE_API_KEY": settings.PINECONE_API_KEY,
        "PINECONE_INDEX_NAME": settings.PINECONE_INDEX_NAME,
    }