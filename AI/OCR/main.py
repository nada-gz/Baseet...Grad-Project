import io
import fitz  # PyMuPDF
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
import pytesseract
import arabic_reshaper
from bidi.algorithm import get_display

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI(title="OCR API")

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
    try:
        image = Image.open(io.BytesIO(image_content)).convert("RGB")
        text = pytesseract.image_to_string(image, lang=lang)
        return format_arabic_text(text, lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

# Function to handle PDFs
def process_pdf_for_ocr(pdf_content: bytes, lang: str):
    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open PDF: {e}")

    all_text = []
    for i, page in enumerate(doc):
        # First try to extract embedded text
        text = page.get_text("text")
        
        # If page is empty (scanned PDF), use OCR on the page image
        if not text.strip():
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image, lang=lang)
        
        formatted = format_arabic_text(text, lang)
        all_text.append(formatted)
    
    return "\n--- Page Break ---\n".join(all_text)

# API Endpoint to Upload File
@app.post("/ocr/file/")
async def ocr_upload(file: UploadFile = File(...), language: str = "ara+eng"):
    try:
        content = await file.read()
        
        # Check file type and process accordingly
        if file.filename.lower().endswith(".pdf"):
            extracted = process_pdf_for_ocr(content, language)
        else:
            extracted = process_image_for_ocr(content, language)

        # Return result directly (No database saving)
        return {
            "extracted_text": extracted.strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {e}")

@app.get("/")
def root():
    return {"message": "OCR API running"}