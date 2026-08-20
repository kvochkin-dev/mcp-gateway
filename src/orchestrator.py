"""
Модуль для оркестрации LLM с fallback логикой
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.clients.gigachat import GigaChatClient
from src.clients.yandexgpt import YandexGPTClient
from src.config import get_settings

logger = logging.getLogger(__name__)


class LLMOrrchestrator:
    """Оркестратор для вызова LLM с fallback и кешированием"""
    
    def __init__(self):
        self.settings = get_settings()
        self.gigachat_client: Optional[GigaChatClient] = None
        self.yandexgpt_client: Optional[YandexGPTClient] = None
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Инициализация клиентов
        if self.settings.gigachat_api_key:
            self.gigachat_client = GigaChatClient(self.settings.gigachat_api_key)
        if self.settings.yandexgpt_api_key:
            self.yandexgpt_client = YandexGPTClient(self.settings.yandexgpt_api_key)
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Генерация ключа кэша"""
        return f"{model}:{prompt[:100]}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Получение из кэша"""
        if not self.settings.cache_enabled:
            return None
        return self._cache.get(cache_key)
    
    def _set_cache(self, cache_key: str, response: Dict[str, Any]):
        """Сохранение в кэш"""
        if not self.settings.cache_enabled:
            return
        self._cache[cache_key] = {
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def call_with_fallback(
        self,
        prompt: str,
        primary: str = None,
        secondary: str = None,
        tertiary: str = None
    ) -> Dict[str, Any]:
        """
        Вызов LLM с каскадным fallback
        
        Args:
            prompt: Текст запроса
            primary: Основная модель (gigachat | yandexgpt)
            secondary: Резервная модель
            tertiary: Третий резерв (ollama)
        
        Returns:
            Dict с результатом вызова
        """
        if primary is None:
            primary = self.settings.primary_model
        if secondary is None:
            secondary = self.settings.secondary_model
        if tertiary is None:
            tertiary = self.settings.tertiary_model
        
        models_to_try: List[str] = []
        if primary in ["gigachat", "yandexgpt"]:
            models_to_try.append(primary)
        if secondary in ["gigachat", "yandexgpt"]:
            models_to_try.append(secondary)
        if tertiary == "ollama":
            models_to_try.append("ollama")
        
        cache_key = self._get_cache_key(prompt, primary)
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info(f"Cache hit for {primary}")
            return cached["response"]
        
        errors = []
        
        for model in models_to_try:
            try:
                logger.info(f"Trying {model}...")
                
                if model == "gigachat":
                    if not self.gigachat_client:
                        raise ValueError("GigaChat not configured")
                    result = await self.gigachat_client.chat_completion(prompt)
                    
                elif model == "yandexgpt":
                    if not self.yandexgpt_client:
                        raise ValueError("YandexGPT not configured")
                    result = await self.yandexgpt_client.chat_completion(prompt)
                    
                elif model == "ollama":
                    # TODO: Добавить клиента Ollama
                    result = {
                        "text": "[TODO] Ollama integration pending",
                        "model": "ollama",
                        "latency_ms": 0,
                        "provider": "ollama"
                    }
                
                else:
                    continue
                
                result["used_model"] = model
                result["fallback_chain"] = models_to_try[:models_to_try.index(model) + 1]
                result["timestamp"] = datetime.utcnow().isoformat()
                
                self._set_cache(cache_key, result)
                return result
                
            except Exception as e:
                error_msg = f"{model}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"Model {model} failed: {error_msg}")
                continue
        
        return {
            "error": "All LLM providers failed",
            "prompt": prompt,
            "errors": errors,
            "tried_models": models_to_try,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка состояния всех провайдеров"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "providers": {
                "gigachat": {
                    "configured": bool(self.settings.gigachat_api_key),
                    "status": "ready" if self.settings.gigachat_api_key else "missing_config"
                },
                "yandexgpt": {
                    "configured": bool(self.settings.yandexgpt_api_key),
                    "status": "ready" if self.settings.yandexgpt_api_key else "missing_config"
                },
                "ollama": {
                    "configured": True,
                    "status": "ready"
                }
            },
            "config": {
                "fallback_enabled": self.settings.fallback_enabled,
                "cache_enabled": self.settings.cache_enabled,
                "primary_model": self.settings.primary_model,
                "secondary_model": self.settings.secondary_model,
                "tertiary_model": self.settings.tertiary_model
            }
        }
