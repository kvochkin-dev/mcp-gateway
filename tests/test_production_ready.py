#!/usr/bin/env python3
"""Production readiness test for MCP Gateway"""
import asyncio
import sys
import os
sys.path.insert(0, '/home/dataguru/Projects/mcp-gateway')

from dotenv import load_dotenv
load_dotenv('/home/dataguru/Projects/mcp-gateway/.env')

from src.clients.gigachat import GigaChatClient
from src.clients.yandexgpt import YandexGPTClient
from src.anonymizer import Anonymizer


async def run_tests():
    results = {}
    
    # Get keys from env
    gc_key = os.environ.get('GIGACHAT_API_KEY', '')
    yp_key = os.environ.get('YANDEXGPT_API_KEY', '')
    yp_folder = os.environ.get('YANDEXGPT_FOLDER_ID', '')
    
    print(f"Keys loaded: GigaChat={len(gc_key)}>0, YandexGPT={len(yp_key)}>0")
    
    # Test 1: GigaChat connection
    print("\n=== Test 1: GigaChat Connection ===")
    try:
        if not gc_key:
            print("❌ FAIL - No GIGACHAT_API_KEY in environment")
            results['gigachat'] = 'FAIL'
        else:
            gc = GigaChatClient(gc_key)
            health = await gc.health_check()
            models = await gc.list_models()
            
            if health and len(models) > 0:
                print(f"✅ PASS - GigaChat operational")
                print(f"   Available models: {[m['id'] for m in models]}")
                results['gigachat'] = 'PASS'
            else:
                print(f"❌ FAIL - GigaChat not operational (health={health}, models={len(models)})")
                results['gigachat'] = 'FAIL'
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results['gigachat'] = 'FAIL'
    
    # Test 2: YandexGPT connection
    print("\n=== Test 2: YandexGPT Connection ===")
    try:
        if not yp_key:
            print("❌ FAIL - No YANDEXGPT_API_KEY in environment")
            results['yandexgpt'] = 'FAIL'
        else:
            yp = YandexGPTClient(yp_key, yp_folder)
            health = await yp.health_check()
            models = await yp.list_models()
            
            if health and len(models) > 0:
                print(f"✅ PASS - YandexGPT operational")
                print(f"   Available models: {[m['id'] for m in models[:3]]}")
                results['yandexgpt'] = 'PASS'
            else:
                print(f"❌ FAIL - YandexGPT not operational (health={health}, models={len(models)})")
                results['yandexgpt'] = 'FAIL'
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results['yandexgpt'] = 'FAIL'
    
    # Test 3: Chat with GigaChat
    print("\n=== Test 3: GigaChat Chat ===")
    try:
        if not gc_key:
            print("❌ FAIL - No GigaChat key configured")
            results['gigachat_chat'] = 'FAIL'
        else:
            gc = GigaChatClient(gc_key)
            response = await gc.chat([{"role": "user", "content": "Say hello in one word"}])
            
            if response.get('content'):
                print(f"✅ PASS - Chat works")
                print(f"   Response: {response['content'][:50]}...")
                results['gigachat_chat'] = 'PASS'
            else:
                print(f"❌ FAIL - No content returned")
                results['gigachat_chat'] = 'FAIL'
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results['gigachat_chat'] = 'FAIL'
    
    # Test 4: Chat with YandexGPT
    print("\n=== Test 4: YandexGPT Chat ===")
    try:
        if not yp_key:
            print("❌ FAIL - No YandexGPT key configured")
            results['yandexgpt_chat'] = 'FAIL'
        else:
            yp = YandexGPTClient(yp_key, yp_folder)
            response = await yp.chat([{"role": "user", "content": "Say hello in one word"}])
            
            if response.get('content'):
                print(f"✅ PASS - Chat works")
                print(f"   Response: {response['content'][:50]}...")
                results['yandexgpt_chat'] = 'PASS'
            else:
                print(f"❌ FAIL - No content returned")
                results['yandexgpt_chat'] = 'FAIL'
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results['yandexgpt_chat'] = 'FAIL'
    
    # Test 5: Anonymizer
    print("\n=== Test 5: 152-FZ Anonymizer ===")
    try:
        anon = Anonymizer()
        
        # Test compliance check
        text_with_pii = "My name is Ivan Petrov, my phone is +7 (999) 123-45-67"
        compliance = anon.check_compliance(text_with_pii)
        
        if not compliance['is_compliant']:
            print(f"✅ PASS - PII detection works")
            print(f"   Found entities: {compliance.get('entities', [])}")
            results['anonymizer'] = 'PASS'
        else:
            print(f"❌ FAIL - Should detect PII")
            results['anonymizer'] = 'FAIL'
            
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results['anonymizer'] = 'FAIL'
    
    # Summary
    print("\n" + "="*50)
    print("PRODUCTION READINESS SUMMARY")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v == 'PASS')
    total = len(results)
    
    for test, status in results.items():
        icon = "✅" if status == 'PASS' else "❌"
        print(f"{icon} {test}: {status}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - PRODUCTION READY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed - NOT production ready")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
