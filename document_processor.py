# document_processor.py

import pytesseract
import fitz  
from PIL import Image
import numpy as np
import re
import os
from pathlib import Path

class PropertyDocumentProcessor:
    def __init__(self):
        self.ocr_engine = pytesseract

    def process_document(self, file_path):
        # Example processing function
        return f"Processing {file_path}..."

def create_sample_documents():
    return ["sample_doc_1.pdf", "sample_doc_2.pdf"]
