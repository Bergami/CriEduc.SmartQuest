#!/usr/bin/env python3
import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def quick_test():
    try:
        from app.services.analyze_service import AnalyzeService
        
        print("Testing AnalyzeService.process_document_mock...")
        result = await AnalyzeService.process_document_mock("test@test.com")
        
        print("✅ SUCCESS!")
        print(f"Keys: {list(result.keys())}")
        print(f"Questions: {len(result.get('questions', []))}")
        print(f"Context blocks: {len(result.get('context_blocks', []))}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())
