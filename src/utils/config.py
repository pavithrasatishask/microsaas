from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    # OpenAI
    openai_api_key: str
    
    # Supabase (required)
    supabase_url: str
    supabase_key: str
    supabase_vector_table: str = "repository_embeddings"
    
    # Application
    log_level: str = "INFO"
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = False


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

