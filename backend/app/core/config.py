"""
Application configuration
"""
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Decision Audit System"
    APP_VERSION: str = "1.0.0"
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "decision_audit"
    
    SECRET_KEY: str = "your-secret-key"
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()