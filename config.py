import getpass
import os
from dotenv import load_dotenv

load_dotenv()

def setup_environment():
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
        "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY"),
    }