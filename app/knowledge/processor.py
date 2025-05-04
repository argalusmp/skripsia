from groq import Groq
import os
import logging
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


def extract_text_from_image(file_path: str) -> str:
    """Extract text from image files using Mistral OCR"""
    try:
        # Process similar to document but with appropriate settings for images
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        client = Mistral(api_key=settings.MISTRAL_API_KEY)

        logger.info(f"Uploading image to Mistral OCR: {file_path}")

        # Upload image to Mistral OCR
        uploaded_file = client.files.upload(
            file={
                "file_name": os.path.basename(file_path),
                "content": open(file_path, "rb"),
            },
            purpose="ocr"
        )

        # Retrieve the document URL
        signed_url_obj = client.files.get_signed_url(file_id=uploaded_file.id)
        signed_url = signed_url_obj.url

        # Process OCR on the image
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": signed_url}
        )

        # Extract text from the OCR response (single page for images)
        extracted_text = ocr_response.pages[0].markdown if ocr_response.pages else ""

        logger.info(f"Extracted {len(extracted_text)} characters from image")
        return extracted_text

    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise


def extract_text_from_audio(file_path: str) -> str:
    """Extract text from audio files using OpenAI Whisper"""
    try:
        # For this implementation, use OpenAI's Whisper model for audio transcription
        # or integrate with a different audio transcription service if preferred

        # Here is a placeholder implementation that would use OpenAI's API
        # import openai
        # from openai import OpenAI

        # client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # logger.info(f"Transcribing audio file: {file_path}")

        # with open(file_path, "rb") as audio_file:
        #     transcription = client.audio.transcriptions.create(
        #         model="whisper-1",
        #         file=audio_file
        #     )

        # logger.info(
        #     f"Transcribed {len(transcription.text)} characters from audio")
        # return transcription.text
    
    
        import os 
        from groq import Groq

        client = Groq()
        logger.info(f"Transcribing audio file: {file_path}")
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),  # Use os.path.basename
                model="whisper-large-v3",  # Specify the model.
                language="id",  # Specify the language.
                response_format="text", # Change to text.
            )
            
        logger.info(
            f"Transcribed {len(transcription.text)} characters from audio")
        return transcription.text

    except Exception as e:
        logger.error(f"Error extracting text from audio: {str(e)}")
        raise
