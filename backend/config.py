from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://geollm:geollm_secret@localhost:5432/geollm"
    reader_database_url: str = "postgresql://geollm_reader:geollm_reader_secret@localhost:5432/geollm"
    
    # Langchain / LLM
    groq_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
