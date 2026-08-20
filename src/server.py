"""
Server module for MCP Gateway
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

from src.clients.gigachat import GigaChatClient
from src.clients.yandexgpt import YandexGPTClient

logger = logging.getLogger(__name__)


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


settings = Settings(_env_file=None)

mcp = FastMCP("mcp-gateway")


@mcp.tool()
def chat(prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1024) -> Dict[str, Any]:
    """
    Generate a chat response using GigaChat or YandexGPT with automatic fallback.
    
    Args:
        prompt: User message to send to the LLM
        model: Model identifier (optional, uses default if not provided)
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
    
    Returns:
        Response dict with content, model used, usage stats, and fallback info
    """
    result = {
        "content": "",
        "model": model or settings.default_model,
        "usage": {},
        "fallback_used": False,
        "error": None
    }
    
    try:
        # Check which providers are configured
        providers = []
        if settings.gigachat_api_key:
            providers.append(("gigachat", GigaChatClient(settings.gigachat_api_key)))
        if settings.yandexgpt_api_key:
            providers.append(("yandexgpt", YandexGPTClient(settings.yandexgpt_api_key)))
        
        if not providers:
            result["content"] = "[Demo Mode] No LLM API keys configured. Set GIGACHAT_API_KEY or YANDEXGPT_API_KEY in .env file."
            result["fallback_used"] = True
            return result
        
        # Try providers in order
        for provider_name, client in providers:
            try:
                messages = [{"role": "user", "content": prompt}]
                response = asyncio.run(client.chat(messages, temperature=temperature, max_tokens=max_tokens))
                
                result.update(response)
                result["model"] = f"{provider_name}:{response.get('model', 'default')}"
                break
            except Exception as e:
                logger.warning(f"{provider_name} failed: {e}")
                result["fallback_used"] = True
                continue
        
        if not result["content"]:
            result["error"] = "All providers failed"
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        result["error"] = str(e)
    
    return result


@mcp.tool()
def check_152fz(text: str) -> Dict[str, Any]:
    """
    Check text for personal data compliance with Russian Federal Law 152-FZ.
    
    Args:
        text: Text to analyze for PII
    
    Returns:
        Compliance report
    """
    from src.anonymizer import Anonymizer
    
    anonymizer = Anonymizer()
    result = anonymizer.check_compliance(text)
    
    if not result["is_compliant"]:
        result["recommendations"] = [
            "Anonymize name entities before sending to external LLM",
            "Hash passport numbers using irreversible algorithm",
            "Replace phone numbers with placeholders"
        ]
    else:
        result["recommendations"] = ["Text is compliant with 152-FZ"]
    
    return result


@mcp.tool()
def anonymize_text(text: str) -> Dict[str, Any]:
    """
    Anonymize personal data in text according to 152-FZ requirements.
    
    WARNING: This should only be used in authorized environments.
    
    Args:
        text: Input text containing potential PII
    
    Returns:
        Dict with anonymized_text, found_entities, mapping
    """
    from src.anonymizer import Anonymizer
    
    anonymizer = Anonymizer()
    return anonymizer.anonymize(text)


@mcp.tool()
def restore_text(anonymized_text: str) -> str:
    """
    Restore original text from anonymized version (authorized access only).
    
    Args:
        anonymized_text: Previously anonymized text
    
    Returns:
        Restored original text
    """
    from src.anonymizer import Anonymizer
    
    anonymizer = Anonymizer()
    return anonymizer.restore(anonymized_text)


@mcp.tool()
def get_models_status() -> Dict[str, Any]:
    """
    Get status of all configured LLM providers.
    
    Returns:
        Status dict with availability and cost estimates
    """
    status = {
        "gigachat": "Unconfigured" if not settings.gigachat_api_key else "Available",
        "yandexgpt": "Unconfigured" if not settings.yandexgpt_api_key else "Available",
        "ollama": "Unconfigured",
        "recommended_provider": None,
        "cost_estimate": {}
    }
    
    # Cost estimation (rubles per M tokens)
    costs = []
    if settings.gigachat_api_key:
        costs.append(("gigachat", 200))
    if settings.yandexgpt_api_key:
        costs.append(("yandexgpt", 1455))
    
    if costs:
        best = min(costs, key=lambda x: x[1])
        status["recommended_provider"] = best[0]
        status["cost_estimate"] = {"per_m_tokens": best[1], "currency": "RUB"}
    
    return status


async def main():
    """Main entry point"""
    logger.info(f"Starting MCP Gateway on {settings.host}:{settings.port}")
    logger.info(f"Fallback enabled: {settings.fallback_enabled}")
    logger.info(f"Cache enabled: {settings.cache_enabled}")
    
    await mcp.run_async(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())
