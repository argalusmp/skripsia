from config import setup_environment
from document_loader import load_documents
from vector_store import initialize_vector_store
from rag_simple import run_simple_rag
from rag_multi import run_multi_rag

def main():
    setup_environment()
    docs = load_documents()
    vector_store = initialize_vector_store(docs)
    
    # Run simple RAG process
    run_simple_rag(vector_store)
    
    # Run multi-step RAG process
    run_multi_rag(vector_store)

if __name__ == "__main__":
    main()
