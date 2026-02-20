from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # LLM Configuration (supports OpenAI, Grok, and Groq)
    openai_api_key: str
    openai_model: str = "llama-3.3-70b-versatile"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3
    llm_provider: str = "groq"
    grok_base_url: str = "https://api.x.ai/v1"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    
    # Database Configuration
    database_url: str
    
    # API Configuration
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    log_level: str = "INFO"
    
    # Security
    secret_key: str
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Rate Limiting
    max_requests_per_minute: int = 10
    
    # Application Settings
    app_name: str = "Healthcare Symptom Assessment Agent"
    app_version: str = "1.0.0"
    
    # Token Budget
    token_budget: int = 200000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins into a list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.log_level.upper() == "DEBUG"


# Create global settings instance
settings = Settings()
