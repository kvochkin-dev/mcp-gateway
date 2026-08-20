#!/usr/bin/env python3
"""Прогон метазапроса через GigaChat API"""
import os
import json
import base64
import httpx
import ssl
from datetime import datetime

# Read config
GIGACHAT_API_KEY = os.environ.get('GIGACHAT_API_KEY', '')
if not GIGACHAT_API_KEY or '***' in GIGACHAT_API_KEY:
    # Try from .env
    dotenv_path = '/home/dataguru/Projects/mcp-gateway/.env'
    if os.path.exists(dotenv_path):
        with open(dotenv_path) as f:
            for line in f:
                if line.startswith('GIGACHAT_API_KEY='):
                    GIGACHAT_API_KEY = line.split('=', 1)[1].strip().strip('"\'')

print(f"GigaChat key set: {bool(GIGACHAT_API_KEY)}")

if not GIGACHAT_API_KEY:
    print("ERROR: No API key available")
    exit(1)

def decode_gigachat_key(api_key: str):
    """Decode base64 client_id:client_secret"""
    try:
        decoded = base64.b64decode(api_key).decode()
        parts = decoded.split(':', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
    except Exception:
        pass
    return api_key, ''

def get_oauth_token(client_id: str, client_secret: str) -> str:
    """Get OAuth token from GigaChat"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    credentials = f"{client_id}:{client_secret}"
    auth_bytes = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'RqUID': os.urandom(16).hex(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'scope': 'GIGACHAT_API_PERS'
    }
    
    with httpx.Client(verify=ssl_context, timeout=30) as client:
        resp = client.post(
            'https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
            headers=headers,
            data=data
        )
        
        if resp.status_code != 200:
            print(f"OAuth error: {resp.status_code} - {resp.text}")
            return None
        
        return resp.json().get('access_token')

def chat_completion(token: str, messages: list) -> str:
    """Get completion from GigaChat"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'GigaChat-2',
        'messages': messages,
        'max_tokens': 8000,
        'temperature': 0.7
    }
    
    with httpx.Client(verify=ssl_context, timeout=120) as client:
        resp = client.post(
            'https://api.giga.chat/v1/chat/completions',
            headers=headers,
            json=payload
        )
        
        if resp.status_code != 200:
            print(f"Chat error: {resp.status_code} - {resp.text}")
            return None
        
        return resp.json()['choices'][0]['message']['content']

def main():
    # Decode key
    client_id, client_secret = decode_gigachat_key(GIGACHAT_API_KEY)
    print(f"Client ID length: {len(client_id)}")
    print(f"Client Secret length: {len(client_secret)}")
    
    # Get token
    print("\n🔄 Getting OAuth token...")
    token = get_oauth_token(client_id, client_secret)
    if not token:
        print("Failed to get token")
        exit(1)
    print(f"✅ Token obtained ({len(token)} chars)")
    
    # Read prompt
    with open('/home/dataguru/Projects/mcp-gateway/docs/habr-meta-prompt.md') as f:
        prompt_text = f.read()
    print(f"\n📝 Prompt: {len(prompt_text)} chars")
    
    # Call GigaChat
    print("\n🔄 Calling GigaChat...")
    result = chat_completion(token, [
        {'role': 'system', 'content': 'Ты — эксперт по контент-стратегии и литературный редактор технических блогов на русском языке.'},
        {'role': 'user', 'content': prompt_text}
    ])
    
    if result:
        print(f"\n✅ Result: {len(result)} chars")
        output_path = '/home/dataguru/Projects/mcp-gateway/docs/habr-style-guide.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"💾 Saved to: {output_path}")
        
        # Print preview
        print("\n" + "=" * 50)
        print("PREVIEW:")
        print("=" * 50)
        print(result[:2000] + "\n...")
    else:
        print("Failed to get completion")

if __name__ == '__main__':
    main()
