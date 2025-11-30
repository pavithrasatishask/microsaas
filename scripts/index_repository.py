#!/usr/bin/env python3
"""
Script to index a repository for analysis
Usage: python scripts/index_repository.py <repository_path>
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.repository_service import RepositoryService
from utils.logger import get_logger

logger = get_logger()


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/index_repository.py <repository_path>")
        sys.exit(1)
    
    repository_path = sys.argv[1]
    
    logger.info(f"Starting repository indexing: {repository_path}")
    
    service = RepositoryService()
    success = service.index_repository(repository_path)
    
    if success:
        logger.info("Repository indexing completed successfully!")
        print("✓ Repository indexed successfully")
    else:
        logger.error("Repository indexing failed")
        print("✗ Repository indexing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

