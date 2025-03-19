import getpass
import os
from dotenv import load_dotenv

load_dotenv()

def setup_environment():
    os.getenv("LANGCHAIN_TRACING_V2", "true")
    os.getenv("LANGSMITH_API_KEY") 
    os.getenv("OPENAI_API_KEY")
    os.getenv("GROQ_API_KEY")  
    os.getenv("PINECONE_API_KEY")
