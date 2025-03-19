from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain import hub

def run_simple_rag(vector_store):

    llm = ChatGroq(model="llama3-8b-8192")

    # Define prompt for question-answering
    prompt = hub.pull("rlm/rag-prompt")

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
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response.content}

    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    response = graph.invoke({"question": "apa aturan seminar proposal?"})
    print(response["answer"])
