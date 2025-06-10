import asyncio
import sys
import os
sys.path.append('backend')

from backend.app.services.ai_translator import AITranslator
from backend.app.config import settings

async def test_translation():
    # Sample lab data
    sample_content = """
    HEMATOLOGY:
    Hemoglobin: 14.0 g/dL (Normal: 13.5-18.0)
    RBC Count: 6.52 Million/cmm (Normal: 3.5-5.0)
    Total WBC Count: 8,200 cells/cmm (Normal: 4,500-11,000)
    """
    
    try:
        translator = AITranslator()
        result = await translator.translate_document(sample_content, "lab_results")
        
        print("=== TRANSLATION RESULT ===")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"\nTranslation:\n{result['translation'][:500]}...")
            print(f"\nSections keys: {list(result['sections'].keys())}")
            
            if 'test_data' in result['sections']:
                print(f"\nTest data: {result['sections']['test_data']}")
            else:
                print("\nNo test_data found in sections")
                
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_translation())