import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# detect environment
env = os.getenv("ENV", "development")  # default to development

# choose the right env file
env_file = f".env.{env}"


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str  # added Redis URL setting
    BREVO_API_KEY: str
    BREVO_FROM_EMAIL: str
    BREVO_FROM_NAME: str
    FRONTEND_URL: str
    EMAIL_VERIFICATION_TTL_HOURS: int
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    PASSWORD_RESET_TTL_HOURS: int
    SENTRY_DSN: str

    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")


# initialize settings
settings = Settings()

print(f"Loaded configuration from {env_file}")
