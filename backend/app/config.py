from pydantic_settings import BaseSettings
from typing import Optional
import openai


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://art_buddy:password@localhost:5433/art_buddy_db"
    postgres_user: str = "art_buddy"
    postgres_password: str = "password"
    postgres_db: str = "art_buddy_db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI/Embeddings
    openai_api_key: Optional[str] = None
    embedding_model: str = "text-embedding-ada-002"
    
    # Vector Database
    vector_db_type: str = "pgvector"
    
    # n8n Integration
    n8n_webhook_url: str = "http://localhost:5678/webhook"
    n8n_api_key: Optional[str] = None
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env file


settings = Settings()


def get_openai_client():
    """Get OpenAI client instance."""
    if settings.openai_api_key:
        return openai.OpenAI(api_key=settings.openai_api_key)
    else:
        # Return a mock client or raise an error
        return openai.OpenAI(api_key="fake-key-for-development")
