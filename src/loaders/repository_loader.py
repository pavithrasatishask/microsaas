import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_community.document_loaders import (
    TextLoader,
    PythonLoader,
    JSONLoader,
    UnstructuredMarkdownLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback for older versions
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger()


class RepositoryLoader:
    """Loads and chunks repository files for embedding"""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.settings = get_settings()
        
        # Better text splitter for PDFs with page-aware chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.max_chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""]  # Better separators for PDFs
        )
        
        # Special splitter for PDFs that preserves page context
        self.pdf_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.max_chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
    def _get_file_loader(self, file_path: Path):
        """Get appropriate loader for file type"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.py':
            return PythonLoader(str(file_path))
        elif suffix == '.json':
            return JSONLoader(str(file_path), jq_schema='.')
        elif suffix in ['.md', '.markdown']:
            return UnstructuredMarkdownLoader(str(file_path))
        elif suffix == '.pdf':
            return PyPDFLoader(str(file_path))
        elif suffix in ['.txt', '.yml', '.yaml', '.toml', '.ini', '.cfg']:
            return TextLoader(str(file_path))
        else:
            return TextLoader(str(file_path))
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'node_modules',
            '.pytest_cache',
            '.mypy_cache',
            'chroma_db',
            '.env',
            '.DS_Store',
            '*.pyc',
            '*.pyo',
            '*.pyd',
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    def load_repository(self) -> List[Document]:
        """Load all repository files and split into chunks"""
        documents = []
        
        if not self.repository_path.exists():
            logger.warning(f"Repository path does not exist: {self.repository_path}")
            return documents
        
        # Check if it's a single file (e.g., PDF)
        if self.repository_path.is_file():
            logger.info(f"Loading single file: {self.repository_path}")
            return self._load_single_file(self.repository_path)
        
        logger.info(f"Loading repository from: {self.repository_path}")
        
        # Walk through repository
        for root, dirs, files in os.walk(self.repository_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                
                if self._should_ignore(file_path):
                    continue
                
                try:
                    loader = self._get_file_loader(file_path)
                    loaded_docs = loader.load()
                    
                    # Add metadata
                    for doc in loaded_docs:
                        doc.metadata.update({
                            'file_path': str(file_path.relative_to(self.repository_path)),
                            'file_name': file_path.name,
                            'file_type': file_path.suffix,
                        })
                    
                    documents.extend(loaded_docs)
                    logger.debug(f"Loaded: {file_path.relative_to(self.repository_path)}")
                    
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")
                    continue
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        
        return chunks
    
    def _load_single_file(self, file_path: Path) -> List[Document]:
        """Load and chunk a single file (e.g., PDF)"""
        try:
            logger.info(f"Loading single file: {file_path.name}")
            loader = self._get_file_loader(file_path)
            loaded_docs = loader.load()
            
            logger.info(f"Loaded {len(loaded_docs)} pages/sections from {file_path.name}")
            
            # Add metadata to each document
            for i, doc in enumerate(loaded_docs):
                # Preserve page number if available
                page_num = doc.metadata.get('page', i + 1)
                doc.metadata.update({
                    'file_path': file_path.name,
                    'file_name': file_path.name,
                    'file_type': file_path.suffix,
                    'page': page_num,
                    'source': str(file_path)
                })
            
            # Use PDF-specific splitter for better chunking
            if file_path.suffix.lower() == '.pdf':
                logger.info("Using PDF-optimized chunking")
                chunks = self.pdf_splitter.split_documents(loaded_docs)
            else:
                chunks = self.text_splitter.split_documents(loaded_docs)
            
            logger.info(f"Split {file_path.name} into {len(chunks)} chunks")
            
            # Add chunk index to metadata for better tracking
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_index'] = i
                chunk.metadata['total_chunks'] = len(chunks)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to load single file {file_path}: {e}", exc_info=True)
            raise

