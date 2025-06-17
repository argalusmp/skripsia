from groq import Groq
import os
import logging
import base64
from mistralai import Mistral
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_document(file_path: str) -> str:
    """Extract text from PDF or document files using Mistral OCR"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Initialize Mistral client
        client = Mistral(api_key=settings.MISTRAL_API_KEY)

        logger.info(f"Uploading document to Mistral OCR: {file_path}")

        # Upload document to Mistral OCR
        uploaded_file = client.files.upload(
            file={
                "file_name": os.path.basename(file_path),
                "content": open(file_path, "rb"),
            },
            purpose="ocr"
        )

        # Retrieve the document URL from the uploaded file
        signed_url_obj = client.files.get_signed_url(file_id=uploaded_file.id)
        signed_url = signed_url_obj.url

        if not signed_url:
            raise ValueError(
                "The retrieved file response does not contain a valid 'document_url'.")

        # Process OCR using the document URL
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": signed_url},
            include_image_base64=True,
        )

        logger.info("Extracting text and image content from OCR response...")
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

            all_text += page_content

        logger.info(
            f"Extracted {len(all_text)} characters from {len(ocr_response.pages)} pages")
        return all_text

    except Exception as e:
        logger.error(f"Error extracting text from document: {str(e)}")
        raise


def encode_image_to_base64(image_path: str) -> str:
    """Encode the image to Base64 format."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        logger.error(f"Error: The file {image_path} was not found.")
        raise
    except Exception as e:
        logger.error(f"Error encoding image to Base64: {e}")
        raise

def extract_text_from_image(file_path: str) -> str:
    """Extract text from image files using Mistral OCR."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Encode image to Base64
        base64_image = encode_image_to_base64(file_path)

        # Initialize Mistral client
        client = Mistral(api_key=settings.MISTRAL_API_KEY)

        logger.info(f"Uploading image to Mistral OCR: {file_path}")

        # Process OCR using Base64 encoded image
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            }
        )

        # Extract text from the OCR response
        extracted_text = ocr_response.pages[0].markdown if ocr_response.pages else ""

        logger.info(f"Extracted {len(extracted_text)} characters from image")
        return extracted_text

    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        raise

def extract_text_from_audio(file_path: str) -> str:
    """Extract text from audio files using Groq API"""
    try:
        import os
        import json
        from groq import Groq

        # Initialize Groq client
        client = Groq()

        logger.info(f"Transcribing audio file: {file_path}")

        # Open the audio file
        with open(file_path, "rb") as audio_file:
            # Create a transcription of the audio file
            transcription = client.audio.transcriptions.create(
                file=audio_file,  # Required audio file
                model="whisper-large-v3-turbo",  # Required model to use for transcription
                prompt="Specify context or spelling",  
                response_format="verbose_json", 
                timestamp_granularities=["word", "segment"],  
                language="id",  
                temperature=0.0  
            )

        # Log the full transcription object
        logger.info(f"Full transcription response: {json.dumps(transcription, indent=2, default=str)}")

        # Extract the transcription text
        transcription_text = transcription.text
        if not transcription_text:
            raise ValueError("No transcription text found in the response.")

        logger.info(f"Transcribed {len(transcription_text)} characters from audio")
        return transcription_text

    except Exception as e:
        logger.error(f"Error extracting text from audio: {str(e)}")
        raise

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from .txt files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error extracting text from .txt file: {e}")
        raise