"""
YandexGPT Client for MCP Gateway
"""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime


class YandexGPTClient:
    """Клиент для работы с YandexGPT API"""
    
    BASE_URL = "https://llm.api.cloud.yandex.net/v1"
    
    def __init__(self, api_key: str, folder_id: str = ""):
        self.api_key = api_key
        self.folder_id = folder_id
        self._models: Optional[List[Dict[str, Any]]] = None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Получить список доступных моделей"""
        if self._models is not None:
            return self._models
        
        headers = {
            "Authorization": f"Api-key {self.api_key}",
            "X-folder-id": self.folder_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/models",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            self._models = data.get("data", [])
            return self._models
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """Отправить запрос к YandexGPT (OpenAI-compatible format)"""
        # Get first available model if not specified
        if not model:
            models = await self.list_models()
            if models:
                model = models[0].get("id")
            else:
                raise ValueError("No models available")
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        headers = {
            "Authorization": f"Api-key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.folder_id:
            headers["X-folder-id"] = self.folder_id
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": model,
                "usage": data.get("usage", {}),
                "provider": "yandexgpt"
            }
    
    async def health_check(self) -> bool:
        """Проверка доступности API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/models",
                    headers={
                        "Authorization": f"Api-key {self.api_key}",
                        "X-folder-id": self.folder_id
                    }
                )
                return response.status_code == 200
        except Exception:
            return False
