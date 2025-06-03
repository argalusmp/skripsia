from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from typing import List, Dict, Any

from app.config import settings

def get_vector_store():
    """Initialize and return the vector store instance"""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)
    return vector_store

def store_chunks_in_pinecone(texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
    """Store text chunks in Pinecone vector store"""
    vector_store = get_vector_store()
    vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    return True

def retrieve_relevant_chunks(query: str, k: int = 5) -> list:
    """Retrieve relevant chunks from vector store based on query, including source metadata"""
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(query, k=k)
    results = []
    for doc in docs:
        results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown")
        })
    return results

def format_context_with_sources(chunks: list) -> tuple:
    """Gabungkan context dan kumpulkan sumber unik"""
    context = ""
    sources = set()
    for i, chunk in enumerate(chunks):
        context += f"Document {i+1} (source: {chunk['source']}):\n{chunk['content']}\n\n"
        sources.add(chunk['source'])
    return context, sources