#!/usr/bin/env python3
"""Прогон метазапроса через BYNARA router на модель deepseek-v4-pro"""
import os
import json
import httpx

BYNARA_KEY = os.environ.get('BYNARA_API_KEY', '')
ROUTER_URL = 'https://router.bynara.id/v1/chat/completions'

def main():
    if not BYNARA_KEY or '***' in BYNARA_KEY:
        print("ERROR: BYNARA_API_KEY not set")
        return
    
    # Read meta-prompt
    with open('/home/dataguru/Projects/mcp-gateway/docs/habr-meta-prompt.md') as f:
        prompt_text = f.read()
    
    print(f"📝 Reading prompt: {len(prompt_text)} chars")
    print(f"🔑 BYNARA key: {len(BYNARA_KEY)} chars")
    print(f"🌐 Target: {ROUTER_URL}")
    print("=" * 50)
    
    # Use deepseek-v4-pro for best results
    model = 'deepseek-v4-pro'
    
    headers = {
        'Authorization': f'Bearer {BYNARA_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You are an expert content strategist and literary editor for technical blogs. Respond ONLY in Russian.'},
            {'role': 'user', 'content': prompt_text}
        ],
        'max_tokens': 8000,
        'temperature': 0.7
    }
    
    with httpx.Client(timeout=120) as client:
        try:
            response = client.post(ROUTER_URL, headers=headers, json=payload)
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                result = data['choices'][0]['message']['content']
                print(f"\n✅ Response received ({len(result)} chars)")
                print("\n" + "=" * 50)
                print("OUTPUT:")
                print("=" * 50)
                print(result)
                
                # Save result
                output_path = '/home/dataguru/Projects/mcp-gateway/docs/habr-style-guide.md'
                with open(output_path, 'w') as f:
                    f.write(result)
                print(f"\n💾 Saved to: {output_path}")
            else:
                print(f"❌ Unexpected response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
