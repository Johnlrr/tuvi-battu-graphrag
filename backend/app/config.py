from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://test:test@localhost:5432/test"
    GEMINI_API_KEY: str = "test-key"

    NEXT_PUBLIC_SUPABASE_URL: str = "http://localhost:54321"
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str = "test-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "test-service-role-key"

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "test-password"
    NEO4J_DATABASE: str = "neo4j"

    LANGFUSE_SECRET_KEY: str = "test-secret-key"
    LANGFUSE_PUBLIC_KEY: str = "test-public-key"
    LANGFUSE_BASE_URL: str = "http://localhost:3000"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
