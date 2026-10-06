from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "JobPilot"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://jobpilot:jobpilot_secret@localhost:5432/jobpilot_db"
    DATABASE_SYNC_URL: str = "postgresql://jobpilot:jobpilot_secret@localhost:5432/jobpilot_db"

    # Redis & Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # LLM (OpenAI / FreeLLMAPI)
    OPENAI_BASE_URL: str = "http://localhost:3001/v1"
    OPENAI_API_KEY: str = "dummy-local-key"
    LLM_MODEL: str = "auto"

    # Storage
    STORAGE_TYPE: str = "local"  # "local" ou "s3"
    STORAGE_LOCAL_DIR: str = "./uploads"
    S3_ENDPOINT_URL: Optional[str] = "http://localhost:9000"
    S3_ACCESS_KEY: Optional[str] = "minioadmin"
    S3_SECRET_KEY: Optional[str] = "minioadmin"
    S3_BUCKET_NAME: str = "jobpilot-resumes"
    S3_REGION: str = "us-east-1"

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE: Optional[str] = "credentials.json"
    GOOGLE_SHEET_NAME: str = "JobPilot_Vagas"


settings = Settings()
