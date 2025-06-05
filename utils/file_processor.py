# utils/file_processor.py

import io
from typing import Union
import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_text_from_pdf(file_bytes: bytes) -> str | None:
    """Extracts text from PDF bytes."""
    text = ""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return None
    return text

def extract_text_from_epub(file_path: str) -> str | None:
    """Extracts text from an EPUB file path."""
    text = ""
    try:
        book = epub.read_epub(file_path)
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text() + "\n"
    except Exception as e:
        print(f"Error extracting EPUB: {e}")
        return None
    return text

def extract_text_from_txt(file_bytes: bytes) -> str | None:
    """Extracts text from TXT bytes."""
    try:
        return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error extracting TXT: {e}")
        return None