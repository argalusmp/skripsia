import os
import logging
from app.config import setup_environment
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter
from mistralai import Mistral
import hashlib


def generate_content_hash(text):
    """Generate SHA-256 hash for text content"""
    return hashlib.sha256(text.encode()).hexdigest()


def initialize_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    api_key = setup_environment().get("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index = pc.Index("ragv2")
    vector_store = PineconeVectorStore(embedding=embeddings, index=index)
    return vector_store

def process_and_store_pdf(file_path, vector_store):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Initialize Mistral client
        api_key = setup_environment().get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is not set in the environment variables.")
        client = Mistral(api_key=api_key, debug_logger=logging.getLogger("mistralai"))
        
        logging.info("Uploading PDF to Mistral OCR...")

        # Upload PDF to Mistral OCR
        uploaded_pdf = client.files.upload(
            file={
                "file_name": os.path.basename(file_path),
                "content": open(file_path, "rb"),
            },
            purpose="ocr"
        )
        # print(uploaded_pdf)

        # Retrieve the document URL from the uploaded file
        signed_url_obj = client.files.get_signed_url(file_id=uploaded_pdf.id) 
        signed_url = signed_url_obj.url
        print(signed_url)

        if not signed_url:
            raise ValueError("The retrieved file response does not contain a valid 'document_url'.")

        # Process OCR using the document URL
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": signed_url},
            include_image_base64=True,
        )
        
        logging.info("Extracting text and image content from OCR response...")
        all_text = ""
        
        for page_idx, page in enumerate(ocr_response.pages):
            # Add page markdown content
            page_content = page.markdown + "\n\n"
            
            # Process images on the page if any
            if hasattr(page, 'images') and page.images:
                for img_idx, image in enumerate(page.images):
                    # Create image reference with position information
                    img_ref = f"[IMAGE {img_idx+1} ON PAGE {page_idx+1}] - Located at coordinates: " + \
                             f"({image.top_left_x}, {image.top_left_y}) to ({image.bottom_right_x}, {image.bottom_right_y})\n"
                    
                    # Add image reference to the page content
                    page_content += img_ref + "\n"
                    
                    logging.info(f"Processed image {img_idx+1} on page {page_idx+1}")
            
            all_text += page_content
        
        logging.info(f"Extracted {len(all_text)} characters from {len(ocr_response.pages)} pages")
        
        # Split text into chunks
        logging.info("Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        
        chunks = text_splitter.split_text(all_text)
        logging.info(f"Created {len(chunks)} text chunks")
        
        # Generate content hashes
        hash_ids = [generate_content_hash(chunk) for chunk in chunks]
        file_name = os.path.basename(file_path)
        
        # Check existing IDs in Pinecone
        existing_ids = []
        try:
            # Fetch in batches untuk menghindari limit API
            batch_size = 100
            for i in range(0, len(hash_ids), batch_size):
                batch_ids = hash_ids[i:i+batch_size]
                fetch_response = vector_store.index.fetch(ids=batch_ids)
                existing_ids += list(fetch_response.get("vectors", {}).keys())
        except Exception as e:
            logging.error(f"Error checking existing IDs: {e}")
            return False
        
          # Filter new chunks
        new_texts = []
        new_metadatas = []
        new_ids = []
        for idx, (chunk, hash_id) in enumerate(zip(chunks, hash_ids)):
            if hash_id not in existing_ids:
                new_texts.append(chunk)
                new_metadatas.append({
                    "source": file_name,
                    "chunk": idx,
                    "content_hash": hash_id
                })
                new_ids.append(hash_id)
                
        # Store only new chunks
        if new_texts:
            logging.info(f"Adding {len(new_texts)} new chunks out of {len(chunks)} total")
            vector_store.add_texts(
                texts=new_texts,
                metadatas=new_metadatas,
                ids=new_ids
            )
        else:
            logging.info("No new content to store")

        return True

    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        return False
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False

