import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings(BaseSettings):
    # Використовуємо SQLite для розробки, PostgreSQL для production
    DATABASE_URL: str = "sqlite:///./contacts_dev.db"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # Email verification settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    
    # Rate limiting settings
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_PER_HOUR: int = 100
    
    # Cloudinary settings
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()