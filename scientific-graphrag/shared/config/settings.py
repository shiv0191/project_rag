"""
Shared configuration and environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_TITLE: str = "Scientific GraphRAG Platform"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    TEMPERATURE: float = 0.7

    # Neo4j Configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # Qdrant Configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_TIMEOUT: float = 30.0
    VECTOR_SIZE: int = 1024

    # Embedding Configuration
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    RERANKER_MODEL: str = "BAAI/bge-reranker-large"

    # Service URLs
    API_SERVICE_URL: str = "http://localhost:8000"
    INGESTION_SERVICE_URL: str = "http://localhost:8001"
    GRAPH_SERVICE_URL: str = "http://localhost:8002"
    RETRIEVAL_SERVICE_URL: str = "http://localhost:8003"
    AGENT_SERVICE_URL: str = "http://localhost:8004"
    EVALUATION_SERVICE_URL: str = "http://localhost:8005"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"

    # Database Configuration
    DATABASE_URL: str = ""

    # LangSmith Configuration
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "scientific-graphrag"

    # Evaluation Configuration
    EVALUATION_ENABLED: bool = True
    EVALUATION_SAMPLE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
