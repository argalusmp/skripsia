from langchain_community.document_loaders import PyPDFLoader
from mistralai import Mistral


def load_documents():
    file_path = "./Pedoman_Skripsi.pdf"
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print(len(docs))
    print(docs[0].page_content[0:100])
    print(docs[0].metadata)
    return docs

