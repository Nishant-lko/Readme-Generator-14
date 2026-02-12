"""Application configuration — loads settings from .env file."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    google_api_key: str = Field(..., description="Google Gemini API key")
    github_token: str = Field(default="", description="GitHub personal access token (optional)")
    gemini_model: str = Field(default="models/gemini-2.0-flash", description="Gemini model name")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings instance
settings = Settings()
