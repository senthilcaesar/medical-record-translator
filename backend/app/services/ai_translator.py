from openai import OpenAI
from typing import Dict, Optional
import json
import re
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
                max_tokens=4096,  # Appropriate for gpt-4o-2024-08-06 model
                top_p=0.95,  # Slightly more focused sampling for medical content
                presence_penalty=0.0,  # Neutral presence penalty
                frequency_penalty=0.1  # Slight penalty to reduce repetition
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
                "First, the good news about your results",
                "Here's what we need to keep an eye on",
                "Should you be worried?",
                "What this means for your daily life",
                "Your next steps"
            ]
            
            # For conversational format, we don't need structured test data
            # The content will be displayed as flowing text sections
            sections['conversational_format'] = True
            
        elif doc_type == 'prescription':
            section_headers = [
                "Here's what your doctor has prescribed for you",
                "What each medicine does for your health",
                "How to take your medications properly",
                "What to expect and side effects to know about",
                "Important things to remember",
                "Questions to ask your pharmacist"
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
                # More flexible header matching for conversational format
                if header.lower() in line.lower() and (line.startswith('**') or line.startswith('#') or line.startswith('##')):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section - create key from header
                    if "good news" in header.lower():
                        current_section = "good_news"
                    elif "keep an eye on" in header.lower():
                        current_section = "keep_eye_on"
                    elif "should you be worried" in header.lower():
                        current_section = "should_worry"
                    elif "daily life" in header.lower():
                        current_section = "daily_life"
                    elif "next steps" in header.lower():
                        current_section = "next_steps"
                    # Prescription section mappings
                    elif "doctor has prescribed" in header.lower():
                        current_section = "prescribed_medications"
                    elif "what each medicine does" in header.lower():
                        current_section = "medicine_purposes"
                    elif "how to take your medications" in header.lower():
                        current_section = "medication_instructions"
                    elif "what to expect and side effects" in header.lower():
                        current_section = "side_effects"
                    elif "important things to remember" in header.lower():
                        current_section = "important_warnings"
                    elif "questions to ask your pharmacist" in header.lower():
                        current_section = "pharmacist_questions"
                    else:
                        current_section = header.lower().replace(' ', '_').replace(',', '').replace('?', '').replace('...', '')
                    
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
    
    def _extract_test_data_from_markdown(self, translation: str) -> Optional[list]:
        """
        Extract test data from markdown format in the translation.
        
        Args:
            translation: The translated text containing markdown formatted test results
            
        Returns:
            List of test data dictionaries or None if not found
        """
        try:
            test_data = []
            
            # Look for test sections directly (they start with ### and are separated by ---)
            # Split the entire translation by horizontal lines to find test blocks
            test_blocks = re.split(r'\n---\n', translation)
            
            for block in test_blocks:
                if not block.strip():
                    continue
                    
                # Extract test name from ### header
                test_name_match = re.search(r'###\s*(.+)', block)
                if not test_name_match:
                    continue
                    
                test_name = test_name_match.group(1).strip()
                
                # Extract each field
                test_dict = {
                    "test_name": test_name,
                    "category": self._categorize_test(test_name),
                    "purpose": self._extract_field(block, "Test Name & Purpose"),
                    "your_result": self._extract_field(block, "Your Result"),
                    "normal_range": self._extract_field(block, "Normal Range"),
                    "status": self._extract_status(block),
                    "status_emoji": self._extract_status_emoji(block),
                    "what_this_means": self._extract_field(block, "What This Means"),
                    "health_impact": self._extract_field(block, "Health Impact"),
                    "medical_significance": self._extract_field(block, "Medical Significance")
                }
                
                test_data.append(test_dict)
            
            return test_data if test_data else None
            
        except Exception as e:
            print(f"Error parsing test data from markdown: {e}")
            return None
    
    def _extract_field(self, block: str, field_name: str) -> str:
        """Extract a specific field from a test block."""
        # Try the standard format first
        pattern = rf'\*\*{re.escape(field_name)}\*\*:?\s*(.+?)(?=\n\s*-|\n\s*\*\*|\n\s*$|\Z)'
        match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Try alternative format (without the colon)
        alt_pattern = rf'\*\*{re.escape(field_name)}\*\*\s*(.+?)(?=\n\s*-|\n\s*\*\*|\n\s*$|\Z)'
        alt_match = re.search(alt_pattern, block, re.DOTALL | re.IGNORECASE)
        
        if alt_match:
            return alt_match.group(1).strip()
            
        # If field is still not found, provide a default value based on field name
        if field_name == "What This Means":
            return "This test result provides information about your metabolic health."
        elif field_name == "Health Impact":
            return "This measurement helps assess your overall metabolic function."
        elif field_name == "Medical Significance":
            return "Doctors use this to evaluate your metabolic health status."
        
        return ""
    
    def _extract_status(self, block: str) -> str:
        """Extract status from the Status field."""
        status_text = self._extract_field(block, "Status")
        if "normal" in status_text.lower():
            return "normal"
        elif "high" in status_text.lower():
            return "high"
        elif "low" in status_text.lower():
            return "low"
        elif "borderline" in status_text.lower():
            return "borderline"
        elif "desirable" in status_text.lower():
            return "desirable"
        return "normal"
    
    def _extract_status_emoji(self, block: str) -> str:
        """Extract emoji from the Status field."""
        status_text = self._extract_field(block, "Status")
        if "🟢" in status_text:
            return "🟢"
        elif "🔴" in status_text:
            return "🔴"
        elif "🟡" in status_text:
            return "🟡"
        return "🟢"
    
    def _categorize_test(self, test_name: str) -> str:
        """Categorize test based on test name."""
        test_name_lower = test_name.lower()
        
        if any(term in test_name_lower for term in ["hemoglobin", "hematocrit", "rbc", "mcv", "mch", "mchc"]):
            return "Blood Count"
        elif any(term in test_name_lower for term in ["wbc", "neutrophil", "lymphocyte", "eosinophil", "monocyte", "basophil", "platelet"]):
            return "Immune System"
        elif any(term in test_name_lower for term in ["glucose", "sugar", "urea", "creatinine", "uric acid", "calcium"]):
            return "Metabolic"
        elif any(term in test_name_lower for term in ["cholesterol", "triglyceride", "hdl", "ldl", "vldl"]):
            return "Cardiovascular"
        else:
            return "Other"
    
    def _create_sample_test_data(self) -> list:
        """Create sample structured test data for demonstration purposes."""
        return [
            {
                "test_name": "Hemoglobin",
                "category": "Blood Count",
                "purpose": "Measures the amount of hemoglobin in your blood, which carries oxygen",
                "your_result": "14.0 g/dL",
                "normal_range": "13.5-18.0 g/dL for males",
                "status": "normal",
                "status_emoji": "🟢",
                "what_this_means": "Your blood is carrying oxygen effectively",
                "health_impact": "Good oxygen transport in your body",
                "medical_significance": "Ensures your body gets enough oxygen"
            },
            {
                "test_name": "RBC Count",
                "category": "Blood Count",
                "purpose": "Counts the number of red blood cells, which carry oxygen",
                "your_result": "6.52 Million/cmm",
                "normal_range": "3.5-5.0 Million/cmm",
                "status": "high",
                "status_emoji": "🔴",
                "what_this_means": "You have more red blood cells than usual",
                "health_impact": "Could indicate dehydration or other conditions",
                "medical_significance": "Important for diagnosing conditions affecting blood"
            },
            {
                "test_name": "Total WBC Count",
                "category": "Immune System",
                "purpose": "Counts the number of white blood cells, which fight infection",
                "your_result": "8,200 cells/cmm",
                "normal_range": "4,500-11,000 cells/cmm",
                "status": "normal",
                "status_emoji": "🟢",
                "what_this_means": "Your immune system is functioning normally",
                "health_impact": "Good defense against infections",
                "medical_significance": "Indicates immune system health"
            },
            {
                "test_name": "Blood Sugar (Fasting)",
                "category": "Metabolic",
                "purpose": "Measures the sugar level in your blood after fasting",
                "your_result": "110 mg/dL",
                "normal_range": "70-110 mg/dL",
                "status": "borderline",
                "status_emoji": "🟡",
                "what_this_means": "Your blood sugar is at the upper limit of normal",
                "health_impact": "Could indicate a risk for diabetes if consistently high",
                "medical_significance": "Important for diagnosing diabetes"
            },
            {
                "test_name": "Total Cholesterol",
                "category": "Cardiovascular",
                "purpose": "Measures cholesterol levels, important for heart health",
                "your_result": "180 mg/dL",
                "normal_range": "Less than 200 mg/dL",
                "status": "desirable",
                "status_emoji": "🟢",
                "what_this_means": "Your cholesterol is at a healthy level",
                "health_impact": "Lower risk for heart disease",
                "medical_significance": "Key indicator of heart health"
            }
        ]
    
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
                max_tokens=200,  # Appropriate for summaries with gpt-4o-2024-08-06
                top_p=0.95,  # Slightly more focused sampling for medical content
                presence_penalty=0.0,  # Neutral presence penalty
                frequency_penalty=0.1  # Slight penalty to reduce repetition
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Summary unavailable: {str(e)}"
