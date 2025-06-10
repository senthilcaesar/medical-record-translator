import asyncio
import sys
import os
sys.path.append('backend')

from backend.app.services.ai_translator import AITranslator
from backend.app.config import settings

async def debug_translation():
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
        
        if result['success']:
            print("=== FULL TRANSLATION ===")
            print(result['translation'])
            print("\n=== DETAILED TEST RESULTS SECTION ===")
            
            # Try to find the detailed test results section
            translation = result['translation']
            import re
            detailed_section_match = re.search(r'\*\*Detailed Test Results\*\*:?(.*?)(?=\*\*[^*]+\*\*:|$)', translation, re.DOTALL | re.IGNORECASE)
            if detailed_section_match:
                print("Found detailed section:")
                print(detailed_section_match.group(1)[:500])
            else:
                print("No detailed section found")
                
            # Test the parsing method directly
            test_data = translator._extract_test_data_from_markdown(translation)
            print(f"\n=== PARSED TEST DATA ===")
            print(f"Test data: {test_data}")
            
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_translation())