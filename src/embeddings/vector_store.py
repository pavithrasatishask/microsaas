from typing import List, Optional
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.supabase import SupabaseVectorStore
from supabase import create_client, Client

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger()


class VectorStore:
    """Manages vector storage for repository embeddings using Supabase"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.settings.openai_api_key)
        self.store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize Supabase Vector Store"""
        if not self.settings.supabase_url or not self.settings.supabase_key:
            raise ValueError(
                "Supabase configuration is required. Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
            )
        
        logger.info("Initializing Supabase Vector Store")
        supabase: Client = create_client(
            self.settings.supabase_url,
            self.settings.supabase_key
        )
        self.store = SupabaseVectorStore(
            client=supabase,
            embedding=self.embeddings,
            table_name=self.settings.supabase_vector_table,
        )
        logger.info(f"Supabase Vector Store initialized with table: {self.settings.supabase_vector_table}")
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        if not documents:
            logger.warning("No documents to add")
            return
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        self.store.add_documents(documents)
        logger.info("Documents added successfully")
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """Search for similar documents"""
        logger.debug(f"Searching for: {query} (k={k})")
        
        results = self.store.similarity_search(
            query,
            k=k,
            filter=filter
        )
        
        logger.debug(f"Found {len(results)} results")
        return results
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """Search with similarity scores"""
        logger.debug(f"Searching with scores for: {query} (k={k})")
        
        results = self.store.similarity_search_with_score(
            query,
            k=k,
            filter=filter
        )
        
        logger.debug(f"Found {len(results)} results")
        return results


_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get vector store instance (singleton)"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

