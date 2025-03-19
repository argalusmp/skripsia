from config import setup_environment
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter

def initialize_vector_store(docs):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    pc = Pinecone(api_key=setup_environment()["PINECONE_API_KEY"])
    index = pc.Index("rag")
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)
    
    # Index chunks
    vector_store.add_documents(documents=all_splits)
    return vector_store
