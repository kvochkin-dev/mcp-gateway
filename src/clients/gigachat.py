"""
GigaChat Client for MCP Gateway
"""
import httpx
import ssl
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import base64
import os


class GigaChatClient:
    """Клиент для работы с GigaChat API"""
    
    BASE_URL = "https://ngw.devices.sberbank.ru:9443"
    OAUTH_URL = f"{BASE_URL}/api/v2/oauth"
    CHAT_URL = "https://api.giga.chat/v1/chat/completions"
    MODELS_URL = "https://api.giga.chat/v1/models"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        # Create SSL context that skips verification for Sber's self-signed cert
        self.ssl_context = self._create_ssl_context()
        
        # Decode API key: it's base64(client_id:client_secret)
        try:
            decoded = base64.b64decode(api_key).decode()
            parts = decoded.split(':', 1)
            if len(parts) == 2:
                self.client_id = parts[0]
                self.client_secret = parts[1]
            else:
                # Fallback: use whole key as client_id
                self.client_id = api_key
                self.client_secret = ""
        except Exception:
            # If decoding fails, treat as plain key
            self.client_id = api_key
            self.client_secret = ""
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Создать SSL контекст с отключенной проверкой сертификатов"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context
    
    def _get_http_client(self) -> httpx.AsyncClient:
        """Создать HTTP клиент без proxy для обхода SOCKS ограничений"""
        # Save and unset proxy env vars temporarily
        original_proxies = {
            'http_proxy': os.environ.get('HTTP_PROXY'),
            'https_proxy': os.environ.get('HTTPS_PROXY'),
            'all_proxy': os.environ.get('ALL_PROXY'),
        }
        
        # Remove proxy settings to avoid SOCKS issues
        for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']:
            os.environ.pop(key, None)
        
        client = httpx.AsyncClient(verify=self.ssl_context)
        
        # Restore proxy settings
        for key, value in original_proxies.items():
            if value:
                os.environ[key] = value
        
        return client
    
    async def _get_token(self) -> str:
        """Получить токен доступа через OAuth2 client credentials"""
        if self._token and self._token_expires_at and datetime.utcnow() < self._token_expires_at:
            return self._token
        
        try:
            async with self._get_http_client() as client:
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                }
                
                # Basic auth: base64(client_id:client_secret)
                auth_string = f"{self.client_id}:{self.client_secret}"
                auth_b64 = base64.b64encode(auth_string.encode()).decode()
                headers["Authorization"] = f"Basic {auth_b64}"
                headers["RqUID"] = self.client_id
                
                data = {"scope": "GIGACHAT_API_PERS"}
                
                response = await client.post(
                    self.OAUTH_URL,
                    headers=headers,
                    data=data
                )
                
                if response.status_code != 200:
                    raise Exception(f"OAuth failed: {response.status_code} - {response.text}")
                
                token_data = response.json()
                
                self._token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600) - 60
                self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                return self._token
        except Exception as e:
            raise Exception(f"GigaChat OAuth error: {e}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """Отправить запрос к GigaChat"""
        token = await self._get_token()
        
        models = await self.list_models()
        model_name = model or (models[0]["id"] if models else "GigaChat-2")
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        async with self._get_http_client() as client:
            response = await client.post(
                self.CHAT_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": model_name,
                "usage": data.get("usage", {}),
                "provider": "gigachat"
            }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Получить список доступных моделей"""
        token = await self._get_token()
        
        async with self._get_http_client() as client:
            response = await client.get(
                self.MODELS_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("data", [])
    
    async def health_check(self) -> bool:
        """Проверка доступности API"""
        try:
            await self._get_token()
            return True
        except Exception:
            return False
