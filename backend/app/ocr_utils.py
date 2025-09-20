# backend/app/ocr_utils.py
import io, os, tempfile
from pdf2image import convert_from_bytes
import pytesseract
import pdfplumber
from docx import Document

def extract_text_from_pdf_bytes(pdf_bytes):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for p in pdf.pages:
                page_text = p.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        text = ""
    # if no text extracted, do OCR
    if not text.strip():
        images = convert_from_bytes(pdf_bytes)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    return text

def extract_text_from_docx_bytes(docx_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(docx_bytes)
        tmp.flush()
        doc = Document(tmp.name)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
    try:
        os.unlink(tmp.name)
    except Exception:
        pass
    return "\n".join(fullText)

def extract_text(file_bytes, filename):
    fname = filename.lower()
    if fname.endswith(".pdf"):
        return extract_text_from_pdf_bytes(file_bytes)
    elif fname.endswith(".docx") or fname.endswith(".doc"):
        return extract_text_from_docx_bytes(file_bytes)
    else:
        # try pdf as default
        return extract_text_from_pdf_bytes(file_bytes)