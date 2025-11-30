#!/usr/bin/env python3
"""
Server startup script with better error handling
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("Starting Repository Intelligence Backend...")
print("=" * 60)

try:
    print("1. Loading configuration...")
    from src.utils.config import get_settings
    from src.utils.logger import get_logger
    
    logger = get_logger()
    print("✓ Configuration loaded")
    
    print("2. Initializing Flask app...")
    from src.main import app
    print("✓ Flask app created")
    
    print("3. Starting server on http://localhost:8000")
    print("=" * 60)
    print("Server is running! Press Ctrl+C to stop.")
    print("=" * 60)
    
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"✗ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

