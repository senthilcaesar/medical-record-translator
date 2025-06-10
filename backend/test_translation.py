#!/usr/bin/env python3
"""
Test script to debug translation issues
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_processor import PDFProcessor
from app.services.ai_translator import AITranslator
from app.config import settings

async def test_translation():
    """Test the translation process with a sample text"""
    
    print("=== Medical Record Translator Debug Test ===")
    print(f"OpenAI API Key configured: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    print()
    
    # Test PDF processor
    print("Testing PDF processor...")
    pdf_processor = PDFProcessor()
    
    # Test with comprehensive sample medical text
    sample_text = """
    COMPREHENSIVE METABOLIC PANEL & COMPLETE BLOOD COUNT

    Patient: John Doe
    Date: 2024-01-15
    Lab ID: 12345

    COMPLETE BLOOD COUNT (CBC)
    Hemoglobin: 14.0 g/dL (Normal: 13.5-18.0)
    RBC Count: 6.52 million cells/cmm (Normal: 3.5-5.0)
    Hematocrit (HCT): 56.3% (Normal: 40-65%)
    MCV: 86.5 fL (Normal: 76-96)
    MCH: 24.5 pg (Normal: 27-32)
    MCHC: 28.4 g% (Normal: 30-35)
    WBC Count: 8,200 cells/cmm (Normal: 4,500-11,000)
    Neutrophils: 65% (Normal: 50-70%)
    Lymphocytes: 30% (Normal: 20-40%)
    Monocytes: 4% (Normal: 2-8%)
    Eosinophils: 0% (Normal: 1-4%)
    Basophils: 1% (Normal: 0-2%)
    Platelet Count: 188,000/cmm (Normal: 150,000-450,000)

    BIOCHEMISTRY
    Blood Sugar (Fasting): 110 mg/dL (Normal: 70-110)
    Urea: 24 mg/dL (Normal: 10-40)
    Creatinine: 0.7 mg/dL (Normal: 0.9-1.4)
    Uric Acid: 5.4 mg/dL (Normal: 3.5-7.2)

    LIPID PROFILE
    Total Cholesterol: 180 mg/dL (Normal: <200)
    Triglycerides: 152 mg/dL (Normal: <150)
    HDL Cholesterol: 45 mg/dL (Normal: 45-60)
    LDL Cholesterol: 104.6 mg/dL (Normal: 70-165)
    VLDL: 30.4 mg/dL (Normal: 15-30)
    Total Cholesterol/HDL Ratio: 4.0 (Normal: <4.5)
    """
    
    print("Identifying document type...")
    doc_type = pdf_processor.identify_document_type(sample_text)
    print(f"Document type: {doc_type}")
    print()
    
    # Test AI translator
    print("Testing AI translator...")
    try:
        ai_translator = AITranslator()
        print("AI Translator initialized successfully")
        
        print("Starting translation...")
        result = await ai_translator.translate_document(sample_text, doc_type)
        
        if result["success"]:
            print("✅ Translation successful!")
            print(f"Translation length: {len(result['translation'])} characters")
            print(f"Sections found: {list(result['sections'].keys())}")
            print(f"Model used: {result['model_used']}")
            print(f"Tokens used: {result['usage']['total_tokens']}")
            print("\n" + "="*80)
            print("ENHANCED TRANSLATION OUTPUT:")
            print("="*80)
            print(result['translation'])
            print("="*80)
        else:
            print("❌ Translation failed!")
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ AI Translator initialization failed: {e}")
        return False
    
    return result["success"] if 'result' in locals() else False

if __name__ == "__main__":
    success = asyncio.run(test_translation())
    sys.exit(0 if success else 1)