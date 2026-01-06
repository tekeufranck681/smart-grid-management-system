import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# detect environment
env = os.getenv("ENV", "development")  # default to development

# choose the right env file
env_file = f".env.{env}"


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str  # added Redis URL setting
    FRONTEND_URL: str
    SENTRY_DSN: str
    AUTH_SERVICE_URL: str
    WORKSPACE_SERVICE_URL: str

    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")


# initialize settings
settings = Settings()

print(f"Loaded configuration from {env_file}")
