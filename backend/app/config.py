from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Rate limiting settings
    RATE_LIMIT: str = "5/minute"
    ALLOWED_ORIGINS: List[str] = ["*"] 

    # --- ADD THESE LINES for JWT Authentication ---
    SECRET_KEY: str = "a_very_secret_key_that_should_be_changed"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()