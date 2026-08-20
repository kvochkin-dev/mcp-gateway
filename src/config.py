"""
MCP Gateway Configuration
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Configuration for MCP Gateway"""
    
    # API Keys
    gigachat_api_key: str = ""
    yandexgpt_api_key: str = ""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    # Fallback settings
    fallback_enabled: bool = True
    fallback_order: List[str] = ["gigachat", "yandexgpt", "ollama"]
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600
    
    # LLM defaults
    default_model: str = "gigachat:latest"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()


settings = get_settings()
