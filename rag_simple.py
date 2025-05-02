from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain import hub

def run_simple_rag(vector_store):

    llm = ChatGroq(model="llama-3.3-70b-versatile")

    # Define prompt for question-answering
    prompt = """
    You are an AI assistant. Answer the following question based on the provided context.
    If you don't know the answer, say that you don't know. answer like a student friend.
    
    Question: {question}

    Context:
    {context}

    Answer:
    """

    # Define state for application
    class State(TypedDict):
        question: str
        context: List[Document]
        answer: str

    # Define application steps
    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}

    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.format(question=state["question"], context=docs_content)
        response = llm.invoke(messages)
        return {"answer": response.content}

    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    response = graph.invoke({"question": "berikan saya Contoh lembar pengesahan"})
    print(response["answer"])

