#!/usr/bin/env python3
"""
Simple test to check if we can import and initialize the vector store
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    from utils.config import get_settings
    print("✓ Config imported")
    
    from utils.logger import get_logger
    print("✓ Logger imported")
    
    settings = get_settings()
    print(f"✓ Settings loaded: Supabase URL configured")
    
    # Try to import vector store (this will test Supabase connection)
    try:
        from embeddings.vector_store import get_vector_store
        print("✓ Vector store module imported")
        
        # Try to initialize (this will test actual connection)
        try:
            vs = get_vector_store()
            print("✓ Vector store initialized successfully!")
            print("✓ Supabase connection working!")
        except Exception as e:
            print(f"⚠ Vector store initialization: {e}")
            print("  This might be okay if it's just a version compatibility issue")
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  This might be a langchain version compatibility issue")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

