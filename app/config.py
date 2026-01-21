from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Groq API Configuration
    groq_api_key: str
    groq_model: str = "mixtral-8x7b-32768"
    
    # Weaviate Configuration
    weaviate_url: str = "http://weaviate:8080"
    weaviate_api_key: Optional[str] = None
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Chunking Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Retrieval Configuration
    top_k: int = 5
    similarity_threshold: float = 0.7
    
    # LLM Generation Parameters
    llm_temperature: float = 0.1
    llm_max_tokens: int = 512
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
