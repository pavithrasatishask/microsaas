#!/usr/bin/env python3
"""Test QA chain directly to see the actual error"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chains.qa_chain import RepositoryQAChain
from models.schemas import QuestionRequest

print("Testing QA Chain directly...")
print("=" * 60)

try:
    qa = RepositoryQAChain()
    print("✓ QA Chain initialized")
    
    req = QuestionRequest(
        question="How does user authentication work?",
        max_results=3
    )
    
    print(f"\nAsking question: {req.question}")
    result = qa.answer_question(req)
    
    print("\n✓ Question answered successfully!")
    print(f"Answer: {result.answer[:200]}...")
    print(f"Files referenced: {len(result.repository_evidence.file_paths)}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

