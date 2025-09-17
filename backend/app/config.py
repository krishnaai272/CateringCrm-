from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings): 
    # --- General Settings ---
    # This variable helps distinguish between environments but is not needed for the env_file logic.
    # It's set by an environment variable on Render, defaults to "development" locally.
    ENVIRONMENT: str = "development"

    # --- Database Settings ---
    # This is the primary setting that will be loaded from either the .env file or Render's environment variables.
    DATABASE_URL: str

    # --- Rate Limiting Settings ---
    RATE_LIMIT: str = "5/minute"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # --- JWT Authentication Settings ---
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # This is the corrected way to handle the .env file.
        # It tells pydantic to load variables from a file named ".env".
        # If the file doesn't exist (like in production on Render),
        # pydantic will ignore this line and only use the real environment variables.
        # This removes the "Config file not found" warning in a clean way.
        env_file = ".env"
                    
# Create a single instance of the settings to be used throughout the application
settings = Settings()