from pathlib import Path
from typing import Optional
import tempfile
import shutil

from src.loaders.repository_loader import RepositoryLoader
from src.embeddings.vector_store import get_vector_store
from src.utils.logger import get_logger
from src.utils.github_clone import clone_github_repo, is_github_url

logger = get_logger()


class RepositoryService:
    """Service for managing repository embeddings"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self._is_indexed = False
        self._temp_dirs = []  # Track temp directories for cleanup
    
    def index_repository(self, repository_path: str, cleanup: bool = True) -> bool:
        """
        Index a repository by loading and embedding all files
        
        Args:
            repository_path: Path to local repository, GitHub URL, or file path
            cleanup: Whether to cleanup temporary directories after indexing
        
        Returns:
            True if indexing was successful
        """
        temp_dir = None
        try:
            logger.info(f"Starting repository indexing: {repository_path}")
            
            # Check if it's a GitHub URL
            if is_github_url(repository_path):
                logger.info("Detected GitHub URL, cloning repository...")
                temp_dir = clone_github_repo(repository_path)
                actual_path = temp_dir
                self._temp_dirs.append(temp_dir)
            else:
                actual_path = Path(repository_path)
                if not actual_path.exists():
                    logger.error(f"Path does not exist: {repository_path}")
                    return False
                
                # If it's a single file, use it directly
                if actual_path.is_file():
                    logger.info(f"Detected single file: {actual_path.name}")
            
            # Load repository or file
            try:
                loader = RepositoryLoader(str(actual_path))
                documents = loader.load_repository()
            except Exception as e:
                logger.error(f"Error loading documents: {e}", exc_info=True)
                if cleanup and temp_dir:
                    self._cleanup_temp_dir(temp_dir)
                return False
            
            if not documents:
                logger.warning("No documents found to index")
                if cleanup and temp_dir:
                    self._cleanup_temp_dir(temp_dir)
                return False
            
            # Add to vector store
            self.vector_store.add_documents(documents)
            
            self._is_indexed = True
            logger.info("Repository indexing completed successfully")
            
            # Cleanup temp directory if requested
            if cleanup and temp_dir:
                self._cleanup_temp_dir(temp_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index repository: {e}")
            if cleanup and temp_dir:
                self._cleanup_temp_dir(temp_dir)
            return False
    
    def _cleanup_temp_dir(self, temp_dir: Path):
        """Clean up temporary directory"""
        try:
            if temp_dir and temp_dir.exists():
                logger.info(f"Cleaning up temporary directory: {temp_dir}")
                shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def is_indexed(self) -> bool:
        """Check if repository is indexed"""
        return self._is_indexed

