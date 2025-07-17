"""
Configuration management for Neurologix Smart Search POV
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "neurologix-assessments"
    aws_rds_endpoint: str = ""
    aws_opensearch_endpoint: str = ""
    
    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "neurologix_db"
    db_user: str = ""
    db_password: str = ""
    
    # API Configuration
    api_base_url: str = "http://localhost:8000"
    api_version: str = "v1"
    
    # Frontend Configuration
    streamlit_server_port: int = 8501
    streamlit_server_address: str = "localhost"
    
    # Security
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # LLM Configuration
    openai_api_key: str = ""
    llm_model: str = "gpt-3.5-turbo"
    
    # Development Settings
    debug: bool = True
    testing: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

def get_database_url() -> str:
    """Get database connection URL"""
    settings = get_settings()
    return f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

def get_aws_config() -> dict:
    """Get AWS configuration dictionary"""
    settings = get_settings()
    return {
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
        "region_name": settings.aws_region
    }
