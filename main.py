
import logging
from config import setup_environment
from vector_store import initialize_vector_store, process_and_store_pdf
from rag_simple import run_simple_rag

def main():
    try:
        setup_environment()
        vector_store = initialize_vector_store()  # Pass an empty list if no initial docs

        # Process uploaded PDF and store in vector database
        pdf_path = "Pedoman_Skripsi.pdf"
        # process_and_store_pdf(pdf_path, vector_store)

        # Run simple RAG process
        run_simple_rag(vector_store)

    except Exception as e:
        logging.error(f"An error occurred in the main workflow: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
    main()


