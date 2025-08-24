import tensorflow as tf
from transformers import BertTokenizer, TFBertForTokenClassification
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import re
from typing import Dict, List, Any
import json
import os
from pathlib import Path

class PropertyDocumentProcessor:
    def __init__(self):
        self.ocr_engine = pytesseract
        self.document_classes = ['lease', 'invoice', 'id_document', 'unknown']
        
        # Initialize models
        print("Loading BERT models...")
        self.classifier_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.classifier_model = TFBertForTokenClassification.from_pretrained(
            'bert-base-uncased', 
            num_labels=len(self.document_classes)
        )
        
        self.ner_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.ner_model = TFBertForTokenClassification.from_pretrained(
            'bert-base-uncased',
            num_labels=13
        )
        print("Models loaded successfully!")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(image_path)
            text = self.ocr_engine.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from any supported file type"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self.extract_text_from_image(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return ""
    
    def classify_document(self, text: str) -> str:
        """Classify document type using BERT"""
        try:
            if not text.strip():
                return "unknown"
                
            inputs = self.classifier_tokenizer(
                text[:512],  # Truncate to BERT's max length
                return_tensors='tf',
                truncation=True,
                padding=True,
                max_length=512
            )
            
            outputs = self.classifier_model(inputs)
            predictions = tf.argmax(outputs.logits, axis=-1)
            predicted_class = self.document_classes[predictions[0][0].numpy()]
            
            return predicted_class
        except Exception as e:
            print(f"Error in classification: {e}")
            return "unknown"
    
    def extract_entities(self, text: str, doc_type: str) -> Dict[str, str]:
        """Extract key entities based on document type"""
        entities = {}
        
        if doc_type == 'lease':
            entities = self._extract_lease_entities(text)
        elif doc_type == 'invoice':
            entities = self._extract_invoice_entities(text)
        elif doc_type == 'id_document':
            entities = self._extract_id_entities(text)
        else:
            # Try all patterns for unknown documents
            entities.update(self._extract_lease_entities(text))
            entities.update(self._extract_invoice_entities(text))
            entities.update(self._extract_id_entities(text))
        
        return entities
    
    def _extract_lease_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from lease documents"""
        patterns = {
            'tenant_name': r'(?:tenant|lessee)[:\s]+([A-Za-z\s\.]+)',
            'property_address': r'(?:property|address)[:\s]+([\d\w\s,]+)',
            'lease_term': r'(?:term|duration)[:\s]+(\d+\s*(?:months|years|month|year))',
            'rent_amount': r'(?:rent|monthly payment)[:\s]+(\$\d+(?:\.\d{2})?)',
            'security_deposit': r'(?:security deposit|deposit)[:\s]+(\$\d+(?:\.\d{2})?)',
            'start_date': r'(?:start date|commencement)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'end_date': r'(?:end date|termination)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        }
        
        return self._extract_with_patterns(text, patterns)
    
    def _extract_invoice_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from invoice documents"""
        patterns = {
            'invoice_number': r'(?:invoice\s*#|no\.)[:\s]+([A-Z0-9-]+)',
            'invoice_date': r'(?:date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'due_date': r'(?:due date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'total_amount': r'(?:total|amount due)[:\s]+(\$\d+(?:\.\d{2})?)',
            'vendor_name': r'(?:from|vendor)[:\s]+([A-Za-z\s&\.]+)',
            'property_unit': r'(?:property|unit)[:\s]+([A-Z0-9\s-]+)'
        }
        
        return self._extract_with_patterns(text, patterns)
    
    def _extract_id_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from ID documents"""
        patterns = {
            'full_name': r'([A-Z][a-z]+\s+[A-Z][a-z]+)',
            'date_of_birth': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'id_number': r'([A-Z0-9]{8,12})',
            'expiry_date': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'address': r'(\d+\s+[A-Za-z\s]+,?\s+[A-Za-z\s]+,?\s+[A-Z]{2})'
        }
        
        return self._extract_with_patterns(text, patterns)
    
    def _extract_with_patterns(self, text: str, patterns: Dict[str, str]) -> Dict[str, str]:
        """Helper method to extract entities using regex patterns"""
        entities = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first match and clean it up
                match = matches[0]
                if isinstance(match, tuple):
                    match = match[0]  # Take the first group if it's a tuple
                entities[key] = match.strip()
        return entities
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Main method to process any document"""
        print(f"Processing document: {file_path}")
        
        # Extract text
        text = self.extract_text_from_file(file_path)
        
        if not text.strip():
            return {
                "error": "No text could be extracted from document",
                "file_name": os.path.basename(file_path)
            }
        
        # Classify document
        doc_type = self.classify_document(text)
        
        # Extract entities
        entities = self.extract_entities(text, doc_type)
        
        return {
            'document_type': doc_type,
            'extracted_text': text[:1000] + "..." if len(text) > 1000 else text,
            'entities': entities,
            'processing_date': str(tf.timestamp().numpy()),
            'file_name': os.path.basename(file_path),
            'text_length': len(text)
        }

def create_sample_documents():
    """Create sample test documents"""
    documents_dir = Path("documents")
    documents_dir.mkdir(exist_ok=True)
    
    # Sample lease
    lease_content = """RESIDENTIAL LEASE AGREEMENT

Tenant: John Smith
Property Address: 123 Main Street, Apartment 4B, New York, NY 10001
Lease Term: 12 months
Monthly Rent: $2000.00
Security Deposit: $2000.00
Start Date: 01/01/2024
End Date: 12/31/2024"""

    # Sample invoice
    invoice_content = """INVOICE #INV-2024-001

Date: 01/15/2024
Due Date: 02/15/2024
From: Property Management Inc.
Property: Unit 4B - 123 Main Street
Total Amount Due: $2000.00"""

    with open(documents_dir / "sample_lease.txt", "w") as f:
        f.write(lease_content)
    
    with open(documents_dir / "sample_invoice.txt", "w") as f:
        f.write(invoice_content)
    
    print("Sample documents created")