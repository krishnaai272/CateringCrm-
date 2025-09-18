from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # These are the variables your app needs.
    # Pydantic will automatically read them from environment variables
    # or from the .env file.
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # This tells pydantic to look for a .env file.
        # It's okay if the file doesn't exist (like on Render).
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a single instance to be used by the rest of the app
settings = Settings()