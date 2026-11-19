"""Central application settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables and an optional .env file."""

    app_name: str = "LocalLens AI"
    app_env: str = "development"
    api_v1_prefix: str = "/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
