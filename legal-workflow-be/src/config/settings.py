"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Legal Workflow API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # BigQuery
    BQ_PROJECT_ID: str = "fp-a-project"
    BQ_DATASET: str = "legal_workflow"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # JWT
    JWT_SECRET_KEY: str = "legal-workflow-dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 480  # 8 hours

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""

    # AI Review
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:3000", "https://lww-frontend-21672960606.asia-southeast1.run.app", "https://lww.mikai.tech"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
