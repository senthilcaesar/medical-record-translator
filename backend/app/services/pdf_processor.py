import fitz  # PyMuPDF
import os
from typing import Dict, List, Optional
import re
from pathlib import Path

class PDFProcessor:
    """Service for extracting and processing text from PDF files."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            # Open the PDF file
            pdf_document = fitz.open(file_path)
            text_content = []
            
            # Extract text from each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text = page.get_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            
            pdf_document.close()
            
            # Join all pages
            full_text = "\n\n".join(text_content)
            
            # Clean up the text
            full_text = self._clean_text(full_text)
            
            return full_text
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR issues
        text = text.replace('|', 'I')  # Common OCR mistake
        
        # Remove page numbers and headers/footers if they follow a pattern
        text = re.sub(r'Page \d+ of \d+', '', text)
        
        # Ensure proper spacing after periods
        text = re.sub(r'\.(?=[A-Z])', '. ', text)
        
        return text.strip()
    
    def identify_document_type(self, text: str) -> str:
        """
        Identify whether the document is a lab result or prescription.
        
        Args:
            text: Extracted text content
            
        Returns:
            Document type: 'lab_results' or 'prescription'
        """
        text_lower = text.lower()
        
        # Keywords for lab results
        lab_keywords = [
            'laboratory', 'lab results', 'test results', 'blood test',
            'urinalysis', 'hemoglobin', 'glucose', 'cholesterol',
            'white blood cell', 'red blood cell', 'platelet',
            'reference range', 'normal range', 'specimen'
        ]
        
        # Keywords for prescriptions
        prescription_keywords = [
            'prescription', 'rx', 'medication', 'drug name',
            'dosage', 'sig:', 'dispense', 'refills',
            'take', 'tablet', 'capsule', 'daily',
            'prescriber', 'pharmacy'
        ]
        
        lab_score = sum(1 for keyword in lab_keywords if keyword in text_lower)
        prescription_score = sum(1 for keyword in prescription_keywords if keyword in text_lower)
        
        if lab_score > prescription_score:
            return 'lab_results'
        elif prescription_score > lab_score:
            return 'prescription'
        else:
            # Default to lab results if unclear
            return 'lab_results'
    
    def extract_structured_data(self, text: str, doc_type: str) -> Dict:
        """
        Extract structured data based on document type.
        
        Args:
            text: Extracted text
            doc_type: Type of document
            
        Returns:
            Structured data dictionary
        """
        if doc_type == 'lab_results':
            return self._extract_lab_data(text)
        elif doc_type == 'prescription':
            return self._extract_prescription_data(text)
        else:
            return {'raw_text': text}
    
    def _extract_lab_data(self, text: str) -> Dict:
        """Extract structured data from lab results."""
        data = {
            'patient_info': {},
            'tests': [],
            'raw_text': text
        }
        
        # Extract patient information (simplified example)
        patient_pattern = r'Patient Name:?\s*([^\n]+)'
        match = re.search(patient_pattern, text, re.IGNORECASE)
        if match:
            data['patient_info']['name'] = match.group(1).strip()
        
        # Extract date
        date_pattern = r'Date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        match = re.search(date_pattern, text, re.IGNORECASE)
        if match:
            data['patient_info']['date'] = match.group(1).strip()
        
        return data
    
    def _extract_prescription_data(self, text: str) -> Dict:
        """Extract structured data from prescriptions."""
        data = {
            'patient_info': {},
            'medications': [],
            'raw_text': text
        }
        
        # Extract medications (simplified example)
        # This would need more sophisticated parsing in production
        med_pattern = r'(?:Rx|Drug|Medication):?\s*([^\n]+)'
        matches = re.findall(med_pattern, text, re.IGNORECASE)
        for match in matches:
            data['medications'].append({'name': match.strip()})
        
        return data
    
    def validate_file(self, file_path: str, max_size: int) -> bool:
        """
        Validate PDF file.
        
        Args:
            file_path: Path to the file
            max_size: Maximum allowed file size in bytes
            
        Returns:
            True if valid, raises exception otherwise
        """
        if not os.path.exists(file_path):
            raise ValueError("File does not exist")
        
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        # Check if it's a valid PDF
        try:
            pdf_document = fitz.open(file_path)
            pdf_document.close()
        except:
            raise ValueError("Invalid PDF file")
        
        return True
