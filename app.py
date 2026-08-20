from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI

from src.config import settings
from src.clients.gigachat import GigaChatClient
from src.clients.yandexgpt import YandexGPTClient
from src.anonymizer import Anonymizer

app = FastAPI(title="MCP Gateway", version="1.0.0")

# Initialize clients with API keys from settings
gigachat_api_key = settings.gigachat_api_key if hasattr(settings, 'gigachat_api_key') else None
yandexgpt_api_key = settings.yandexgpt_api_key if hasattr(settings, 'yandexgpt_api_key') else None

gigachat = GigaChatClient(api_key=gigachat_api_key) if gigachat_api_key else None
yandexgpt = YandexGPTClient(api_key=yandexgpt_api_key) if yandexgpt_api_key else None
anonymizer = Anonymizer()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "gigachat": "connected" if gigachat else "not configured",
        "yandexgpt": "connected" if yandexgpt else "not configured",
        "anonymizer": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=int(settings.port))
