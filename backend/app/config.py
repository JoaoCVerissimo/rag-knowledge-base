from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ragkb:ragkb_dev@localhost:5432/ragkb"
    DATABASE_URL_SYNC: str = "postgresql://ragkb:ragkb_dev@localhost:5432/ragkb"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Embedding
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # LLM
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "ollama/llama3.2"
    OLLAMA_API_BASE: str = "http://ollama:11434"
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""

    # Upload
    UPLOAD_DIR: str = "/app/uploads"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW: int = 60

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
