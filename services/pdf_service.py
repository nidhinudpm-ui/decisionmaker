import pdfplumber
import os

def extract_text_from_pdf(file_path):
    """
    Extracts all text from a PDF file.
    """
    if not os.path.exists(file_path):
        return None
        
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return None
        
    return text.strip()
