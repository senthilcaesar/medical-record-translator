from openai import OpenAI
from typing import Dict, Optional
import json
from app.config import settings
from app.prompts.lab_results import LAB_RESULTS_SYSTEM_PROMPT, LAB_RESULTS_USER_PROMPT
from app.prompts.prescriptions import PRESCRIPTION_SYSTEM_PROMPT, PRESCRIPTION_USER_PROMPT

class AITranslator:
    """Service for translating medical documents using OpenAI."""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def translate_document(self, content: str, doc_type: str) -> Dict:
        """
        Translate medical document content to plain English.
        
        Args:
            content: Extracted text content from the document
            doc_type: Type of document ('lab_results' or 'prescription')
            
        Returns:
            Dictionary containing the translation and metadata
        """
        try:
            # Select appropriate prompts based on document type
            if doc_type == 'lab_results':
                system_prompt = LAB_RESULTS_SYSTEM_PROMPT
                user_prompt = LAB_RESULTS_USER_PROMPT.format(content=content)
            elif doc_type == 'prescription':
                system_prompt = PRESCRIPTION_SYSTEM_PROMPT
                user_prompt = PRESCRIPTION_USER_PROMPT.format(content=content)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000
            )
            
            # Extract the translation
            translation = response.choices[0].message.content
            
            # Parse the translation into sections
            sections = self._parse_translation_sections(translation, doc_type)
            
            return {
                "success": True,
                "document_type": doc_type,
                "translation": translation,
                "sections": sections,
                "model_used": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_type": doc_type
            }
    
    def _parse_translation_sections(self, translation: str, doc_type: str) -> Dict:
        """
        Parse the translation into structured sections.
        
        Args:
            translation: The translated text
            doc_type: Type of document
            
        Returns:
            Dictionary of parsed sections
        """
        sections = {}
        
        if doc_type == 'lab_results':
            section_headers = [
                "Summary",
                "Test Results Explained",
                "What This Means",
                "Important Notes",
                "Next Steps"
            ]
        elif doc_type == 'prescription':
            section_headers = [
                "Medications Summary",
                "What Each Medicine Does",
                "How to Take Your Medicine",
                "Possible Side Effects",
                "Important Warnings",
                "Questions for Your Pharmacist"
            ]
        else:
            return {"full_text": translation}
        
        # Parse sections based on headers
        current_section = None
        current_content = []
        
        lines = translation.split('\n')
        for line in lines:
            # Check if line is a section header
            is_header = False
            for header in section_headers:
                if header.lower() in line.lower() and (line.startswith('**') or line.startswith('#')):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = header.lower().replace(' ', '_')
                    current_content = []
                    is_header = True
                    break
            
            # Add line to current section if not a header
            if not is_header and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # If no sections were parsed, return the full text
        if not sections:
            sections = {"full_text": translation}
        
        return sections
    
    async def get_quick_summary(self, content: str, doc_type: str) -> str:
        """
        Generate a quick one-line summary of the document.
        
        Args:
            content: Document content
            doc_type: Type of document
            
        Returns:
            One-line summary
        """
        try:
            prompt = f"Summarize this {doc_type.replace('_', ' ')} in one simple sentence: {content[:500]}..."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical document summarizer. Provide brief, clear summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Summary unavailable: {str(e)}"
