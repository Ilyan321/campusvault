import io
import time
import logging
from typing import Optional
from config import GEMINI_API_KEY, GEMINI_OCR_MODEL

logger = logging.getLogger("campusvault.ocr")

_genai_client = None

def get_gemini_client():
    global _genai_client
    if _genai_client is None and GEMINI_API_KEY:
        try:
            from google import genai
            _genai_client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize google-genai client: {e}")
    return _genai_client

def extract_text_from_pdf_local(file_bytes: bytes, max_pages: int = 150) -> str:
    """Fast digital text extraction from PDF using pypdf / pdfplumber with 0 API calls."""
    text_content = []
    
    # 1. Ultra-fast pypdf stream extraction (<0.05s for 50+ pages)
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, max_pages)
        for page_idx in range(pages_to_read):
            try:
                page_text = reader.pages[page_idx].extract_text()
                if page_text and page_text.strip():
                    text_content.append(f"--- Page {page_idx + 1} ---\n{page_text.strip()}")
            except Exception:
                continue
        if text_content:
            return "\n\n".join(text_content)
    except Exception as e:
        logger.debug(f"pypdf reader fallback: {e}")

    # 2. pdfplumber fallback (without expensive curve layout calculations)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            total_pages = len(pdf.pages)
            pages_to_read = min(total_pages, min(max_pages, 35))
            for page_idx in range(pages_to_read):
                try:
                    page_text = pdf.pages[page_idx].extract_text(layout=False)
                    if page_text and page_text.strip():
                        text_content.append(f"--- Page {page_idx + 1} ---\n{page_text.strip()}")
                except Exception:
                    continue
            if text_content:
                return "\n\n".join(text_content)
    except Exception as e:
        logger.warning(f"pdfplumber fallback error: {e}")

    return "\n\n".join(text_content)

def ocr_scanned_pdf_pages(file_bytes: bytes, max_scanned_pages: int = 3) -> str:
    """
    For PDFs that are 100% scanned image photocopies, transcribes the first 3 pages
    via Gemini Flash OCR to enable immediate syllabus alignment without hanging.
    """
    client = get_gemini_client()
    if not client:
        return ""
        
    try:
        import pdfplumber
        from google.genai import types
        ocr_results = []
        
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            total = len(pdf.pages)
            limit = min(total, max_scanned_pages)
            logger.info(f"PDF is scanned image document. Processing first {limit} pages with Gemini OCR...")
            
            for page_num in range(limit):
                page = pdf.pages[page_num]
                img = page.to_image(resolution=120).original
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=80)
                page_bytes = img_byte_arr.getvalue()
                
                part = types.Part.from_bytes(data=page_bytes, mime_type='image/jpeg')
                prompt = (
                    "Transcribe all handwritten/printed academic content, formulas, and code "
                    f"from Page {page_num + 1} with high precision."
                )
                
                resp = client.models.generate_content(
                    model=GEMINI_OCR_MODEL,
                    contents=[part, prompt]
                )
                if resp and resp.text:
                    ocr_results.append(f"--- Page {page_num + 1} (OCR) ---\n{resp.text.strip()}")
                time.sleep(0.5)
                
        return "\n\n".join(ocr_results)
    except Exception as e:
        logger.error(f"Scanned PDF OCR processing failed: {e}")
        return ""

def extract_text_from_document(file_bytes: bytes, filename: str, mime_type: str) -> str:
    """
    Smart Local-First Document Parser:
    1. Code/Text files -> Instant local extraction (0 API calls, <0.01s).
    2. Digital PDFs -> High-speed local extraction (<0.1s).
    3. Scanned PDFs -> Fast bounded OCR on initial pages (<3s).
    4. Image files (.png, .jpg) -> Gemini Flash Multimodal OCR.
    """
    filename_lower = filename.lower()
    
    # 1. Text & Code files: Instant local extraction
    if filename_lower.endswith(('.py', '.cpp', '.c', '.java', '.js', '.ts', '.txt', '.md', '.sql', '.html', '.css')):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return file_bytes.decode('latin-1', errors='ignore')

    # 2. PDFs: High-Speed Digital Extraction
    if filename_lower.endswith('.pdf') or 'pdf' in mime_type:
        try:
            local_text = extract_text_from_pdf_local(file_bytes)
            if local_text and len(local_text.strip()) > 30:
                logger.info(f"Extracted {len(local_text)} characters from {filename} locally in milliseconds.")
                return local_text
            else:
                logger.info(f"PDF {filename} is scanned. Running bounded OCR...")
                scanned_text = ocr_scanned_pdf_pages(file_bytes, max_scanned_pages=3)
                if scanned_text.strip():
                    return scanned_text
        except Exception as e:
            logger.warning(f"PDF extraction error: {e}")

    # 3. Single Image Photos / Handwriting (.png, .jpg, .jpeg)
    client = get_gemini_client()
    if client:
        try:
            from google.genai import types
            
            prompt = (
                "You are an academic OCR system. Transcribe all text, equations, and code "
                "from this note precisely into clean Markdown."
            )
            
            part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            response = client.models.generate_content(
                model=GEMINI_OCR_MODEL,
                contents=[part, prompt]
            )
            if response and response.text:
                return response.text
        except Exception as e:
            logger.warning(f"Gemini OCR processing failed: {e}")

    return f"[Document: {filename} uploaded successfully]"

