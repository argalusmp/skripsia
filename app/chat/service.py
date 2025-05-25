from typing import List, Tuple
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from app.vector_store.pinecone_client import retrieve_relevant_chunks

def generate_response(query: str, history: List[Tuple[str, str]] = None) -> str:
    """Generate a response using RAG with conversation history"""
    
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    context = retrieve_relevant_chunks(query)
    
    chat_history = ""
    if history:
        for i, (role, content) in enumerate(history):
            # Skip the most recent user message as it's already in the query
            if i == len(history) - 1 and role == "user":
                continue
            prefix = "User: " if role == "user" else "Assistant: "
            chat_history += f"{prefix}{content}\n\n"

    template = """
    You are a helpful assistant specializing in providing information about skripsi (thesis) guidelines and processes.
    
    Your task is to answer the user's question based on the provided context. If the answer is not in the context or you're unsure, say that you don't know rather than making up information.
    
    When providing responses:
    - Keep your answers concise and focused on the user's question
    - Format your response in a clear, readable way
    - Maintain a helpful and supportive tone
    - If you give documentation or references, also provide a brief summary of the content

    Chat History:
    {chat_history}
    
    Context:
    {context}
    
    User Question: {question}
    
    Assistant:
    """

    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {
            "context": lambda x: context,
            "question": lambda x: x,
            "chat_history": lambda _: chat_history
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    response = rag_chain.invoke(query)
    
    return response