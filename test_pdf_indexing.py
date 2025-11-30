#!/usr/bin/env python3
"""
Test script to debug PDF indexing issues
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.repository_service import RepositoryService
from utils.logger import get_logger

logger = get_logger()

def test_pdf_indexing(pdf_path: str):
    """Test PDF indexing directly"""
    print(f"Testing PDF indexing: {pdf_path}")
    print("=" * 60)
    
    service = RepositoryService()
    
    try:
        # Check if file exists
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"✗ File does not exist: {pdf_path}")
            return False
        
        print(f"✓ File exists: {pdf_path}")
        print(f"  Size: {pdf_file.stat().st_size / 1024:.2f} KB")
        
        # Try to index
        print("\nAttempting to index...")
        success = service.index_repository(str(pdf_path), cleanup=False)
        
        if success:
            print("✓ PDF indexed successfully!")
            return True
        else:
            print("✗ Failed to index PDF")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with the PDF path
    pdf_path = r"C:\Users\pavithra.krishnan\Downloads\US HealthCare Knowledge Base.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    test_pdf_indexing(pdf_path)

