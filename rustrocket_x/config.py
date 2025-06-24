"""Configuration settings for rustrocket_x"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for X (Twitter) API access"""

    # X (Twitter) API credentials - Read Access (Free Plan)
    x_api_key: str = ""
    x_api_secret: str = ""
    x_bearer_token: str = ""

    # X (Twitter) API credentials - Write Access (Basic Plan)
    x_access_token: str = ""
    x_access_token_secret: str = ""

    # Future credentials for ads functionality
    x_client_id: str = ""
    x_client_secret: str = ""

    model_config = SettingsConfigDict(env_file=".env_config", env_file_encoding="utf-8")


# Global settings instance
settings = Settings()
