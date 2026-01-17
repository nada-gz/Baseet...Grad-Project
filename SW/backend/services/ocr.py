import io
from PIL import Image
import pytesseract
import arabic_reshaper
from bidi.algorithm import get_display
import platform

# Set tesseract path for Windows (local dev only)
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Helper function to reshape Arabic text so it displays correctly (RTL)
def format_arabic_text(text, lang):
    if "ara" in lang:
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text
        except Exception:
            return text
    return text


# ---------------------------
# Image OCR
# ---------------------------

def process_image_for_ocr(image_content: bytes, lang: str):
    image = Image.open(io.BytesIO(image_content)).convert("RGB")
    try:
        text = pytesseract.image_to_string(image, lang=lang)
    except Exception as e:
        print(f"[Image OCR] Failed: {e}")
        text = ""
    return format_arabic_text(text, lang)


# ---------------------------
# PDF OCR (LAZY IMPORT)
# ---------------------------

def process_pdf_for_ocr(pdf_content: bytes, lang: str, debug=False):
    """
    Extract text from a PDF.
    Uses embedded text if available, otherwise OCR.
    """
    try:
        import fitz  # PyMuPDF (lazy import)
    except ImportError:
        raise RuntimeError("PDF OCR service not available (PyMuPDF not installed)")

    all_text = []

    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
    except Exception as e:
        if debug:
            print(f"[PDF] Failed to open PDF: {e}")
        return ""

    for i, page in enumerate(doc):
        if debug:
            print(f"[PDF] Processing page {i+1}/{len(doc)}")

        text = page.get_text("text")

        if not text.strip():
            try:
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(1, 1),
                    colorspace=fitz.csGRAY
                )
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(image, lang=lang)
            except Exception as e:
                if debug:
                    print(f"[PDF OCR] Failed on page {i+1}: {e}")
                text = ""

        all_text.append(format_arabic_text(text, lang))

    return "\n--- Page Break ---\n".join(all_text)
