from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Tutorix"
    ENV: str = "development"
    SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "postgresql+psycopg2://tutorix:tutorix@127.0.0.1:5432/tutorix"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    QDRANT_URL: str = "http://127.0.0.1:6333"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
