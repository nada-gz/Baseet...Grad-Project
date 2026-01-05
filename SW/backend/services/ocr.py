import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import arabic_reshaper
from bidi.algorithm import get_display
import platform

# Set tesseract path for Windows
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Helper function to reshape Arabic text so it displays correctly (Right-to-Left)
def format_arabic_text(text, lang):
    if "ara" in lang:
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text
        except Exception:
            return text
    return text

# Function to handle Images
def process_image_for_ocr(image_content: bytes, lang: str):
    """
    Extract text from an image (JPEG, PNG, etc.)
    """
    image = Image.open(io.BytesIO(image_content)).convert("RGB")
    try:
        text = pytesseract.image_to_string(image, lang=lang)
    except Exception as e:
        print(f"[Image OCR] Failed: {e}")
        text = ""
    return format_arabic_text(text, lang)

# Function to handle PDFs (production-ready)
def process_pdf_for_ocr(pdf_content: bytes, lang: str, debug=False):
    """
    Extract text from a PDF.
    1. Use embedded text if available (fast)
    2. Run OCR only on pages without embedded text (scanned/handwritten pages)
    """
    all_text = []

    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
    except Exception as e:
        if debug:
            print(f"[PDF] Failed to open PDF: {e}")
        return ""

    for i, page in enumerate(doc):
        if debug:
            print(f"[PDF] Processing page {i+1}/{len(doc)}...")

        # 1️⃣ Try embedded text first
        text = page.get_text("text")
        if text.strip():
            if debug:
                print(f"[PDF] Embedded text found, skipping OCR")
        else:
            if debug:
                print(f"[PDF] No embedded text, running OCR...")

            # 2️⃣ OCR on scanned page / handwriting
            try:
                # Low-res grayscale image for speed
                pix = page.get_pixmap(matrix=fitz.Matrix(1,1), colorspace=fitz.csGRAY)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(image, lang=lang)
            except Exception as e:
                if debug:
                    print(f"[PDF] OCR failed on page {i+1}: {e}")
                text = ""

        # 3️⃣ Format Arabic text if needed
        formatted = format_arabic_text(text, lang)
        all_text.append(formatted)

    return "\n--- Page Break ---\n".join(all_text)
