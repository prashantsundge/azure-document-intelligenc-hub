from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    cors_origins: str = "http://localhost:5173"
    max_question_length: int = 500

    azure_storage_connection_string: str | None = None
    azure_storage_container_name: str = "source-documents"

    document_intelligence_endpoint: str | None = None
    document_intelligence_key: str | None = None

    language_endpoint: str | None = None
    language_key: str | None = None

    azure_search_endpoint: str | None = None
    azure_search_admin_key: str | None = None
    azure_search_index_name: str = "document-chunks-dev"

    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_chat_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None
    content_safety_endpoint: str | None = None
    content_safety_key: str | None = None

    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()