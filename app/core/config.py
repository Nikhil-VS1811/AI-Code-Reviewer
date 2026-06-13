from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Code Review System"
    APP_ENV: str = "development"
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AI_PROVIDER: str = "mock"
    OLLAMA_MODEL: str = "qwen3:4b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT_SECONDS: int = 60
    CORS_ORIGINS: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if value == "change-this-secret-key-in-production":
            return value

        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")

        return value

    @field_validator("AI_PROVIDER")
    @classmethod
    def validate_ai_provider(cls, value: str) -> str:
        normalized_value = value.lower()
        if normalized_value not in {"mock", "ollama"}:
            raise ValueError("AI_PROVIDER must be either 'mock' or 'ollama'.")

        return normalized_value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if (
            self.APP_ENV.lower() == "production"
            and self.SECRET_KEY == "change-this-secret-key-in-production"
        ):
            raise ValueError("SECRET_KEY must be changed in production.")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
