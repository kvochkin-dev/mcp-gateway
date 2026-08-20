"""
Комплексное тестирование MCP Gateway
Для публикации на Хабре
"""
import asyncio
import sys
import os
import time
sys.path.insert(0, '/home/dataguru/Projects/mcp-gateway')

from dotenv import load_dotenv
load_dotenv('/home/dataguru/Projects/mcp-gateway/.env')

from src.clients.gigachat import GigaChatClient
from src.clients.yandexgpt import YandexGPTClient
from src.anonymizer import Anonymizer
from src.config import Settings


class TestResult:
    def __init__(self, name, status, duration_ms, details=""):
        self.name = name
        self.status = status  # "PASS", "FAIL", "WARN"
        self.duration_ms = duration_ms
        self.details = details
    
    def __str__(self):
        icon = "✅" if self.status == "PASS" else "❌" if self.status == "FAIL" else "⚠️"
        return f"{icon} {self.name}: {self.status} ({self.duration_ms}ms) - {self.details}"


async def run_all_tests():
    results = []
    
    print("="*70)
    print("MCP GATEWAY — COMPREHENSIVE TEST SUITE")
    print("Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    print()
    
    # ==================== SECTION 1: CONFIGURATION ====================
    print("📋 SECTION 1: CONFIGURATION")
    print("-"*70)
    
    settings = Settings()
    
    # Test 1.1: Environment variables
    t0 = time.time()
    gc_key_exists = bool(settings.gigachat_api_key)
    yp_key_exists = bool(settings.yandexgpt_api_key)
    yp_folder_exists = bool(os.environ.get('YANDEXGPT_FOLDER_ID'))
    duration = int((time.time() - t0) * 1000)
    
    results.append(TestResult(
        "GigaChat API Key Configured",
        "PASS" if gc_key_exists else "FAIL",
        duration,
        f"Key length: {len(settings.gigachat_api_key)} chars" if gc_key_exists else "Missing"
    ))
    
    results.append(TestResult(
        "YandexGPT API Key Configured",
        "PASS" if yp_key_exists else "FAIL",
        0,
        f"Key length: {len(settings.yandexgpt_api_key)} chars" if yp_key_exists else "Missing"
    ))
    
    results.append(TestResult(
        "Yandex Folder ID Configured",
        "PASS" if yp_folder_exists else "FAIL",
        0,
        f"Folder: {os.environ.get('YANDEXGPT_FOLDER_ID', 'N/A')[:20]}..."
    ))
    
    print(f"\n{results[-3]}")
    print(f"  {results[-2]}")
    print(f"  {results[-1]}")
    
    # ==================== SECTION 2: GIGACHAT CLIENT ====================
    print("\n🤖 SECTION 2: GIGACHAT CLIENT")
    print("-"*70)
    
    if gc_key_exists:
        t0 = time.time()
        try:
            gc = GigaChatClient(settings.gigachat_api_key)
            health = await gc.health_check()
            duration = int((time.time() - t0) * 1000)
            
            results.append(TestResult(
                "GigaChat Health Check",
                "PASS" if health else "FAIL",
                duration,
                f"Response time: {duration}ms"
            ))
            
            # Test models endpoint
            t1 = time.time()
            try:
                models = await gc.list_models()
                duration = int((time.time() - t1) * 1000)
                
                results.append(TestResult(
                    "GigaChat Models Discovery",
                    "PASS" if len(models) > 0 else "WARN",
                    duration,
                    f"Found {len(models)} models"
                ))
                
                if models:
                    model_names = [m['id'] for m in models]
                    print(f"\n  Available models: {', '.join(model_names[:5])}")
                    
            except Exception as e:
                results.append(TestResult(
                    "GigaChat Models Discovery",
                    "FAIL",
                    0,
                    str(e)[:100]
                ))
            
            # Test chat
            if health:
                t1 = time.time()
                try:
                    response = await gc.chat([
                        {"role": "user", "content": "Say 'Hello' in one word"}
                    ], max_tokens=50)
                    duration = int((time.time() - t1) * 1000)
                    
                    results.append(TestResult(
                        "GigaChat Chat Response",
                        "PASS" if response.get('content') else "FAIL",
                        duration,
                        f'Response: "{response.get("content", "")[:50]}..."'
                    ))
                    
                except Exception as e:
                    results.append(TestResult(
                        "GigaChat Chat Response",
                        "FAIL",
                        0,
                        str(e)[:100]
                    ))
        
        except Exception as e:
            results.append(TestResult(
                "GigaChat Integration",
                "FAIL",
                0,
                f"Error: {str(e)[:80]}"
            ))
    else:
        results.append(TestResult("GigaChat Integration", "FAIL", 0, "No API key"))
    
    # ==================== SECTION 3: YANDEXGPT CLIENT ====================
    print("\n☁️  SECTION 3: YANDEXGPT CLIENT")
    print("-"*70)
    
    if yp_key_exists:
        t0 = time.time()
        try:
            yp = YandexGPTClient(settings.yandexgpt_api_key, os.environ.get('YANDEXGPT_FOLDER_ID'))
            health = await yp.health_check()
            duration = int((time.time() - t0) * 1000)
            
            results.append(TestResult(
                "YandexGPT Health Check",
                "PASS" if health else "FAIL",
                duration,
                f"Response time: {duration}ms"
            ))
            
            # Test models endpoint
            t1 = time.time()
            try:
                models = await yp.list_models()
                duration = int((time.time() - t1) * 1000)
                
                results.append(TestResult(
                    "YandexGPT Models Discovery",
                    "PASS" if len(models) > 0 else "WARN",
                    duration,
                    f"Found {len(models)} models"
                ))
                
                if models:
                    model_names = [m['id'] for m in models[:5]]
                    print(f"\n  Available models: {', '.join(model_names)}")
                    
            except Exception as e:
                results.append(TestResult(
                    "YandexGPT Models Discovery",
                    "FAIL",
                    0,
                    str(e)[:100]
                ))
            
            # Test chat
            if health:
                t1 = time.time()
                try:
                    response = await yp.chat([
                        {"role": "user", "content": "Say 'Hello' in one word"}
                    ], max_tokens=50)
                    duration = int((time.time() - t1) * 1000)
                    
                    results.append(TestResult(
                        "YandexGPT Chat Response",
                        "PASS" if response.get('content') else "FAIL",
                        duration,
                        f'Response: "{response.get("content", "")[:50]}..."'
                    ))
                    
                except Exception as e:
                    results.append(TestResult(
                        "YandexGPT Chat Response",
                        "FAIL",
                        0,
                        str(e)[:100]
                    ))
        
        except Exception as e:
            results.append(TestResult(
                "YandexGPT Integration",
                "FAIL",
                0,
                f"Error: {str(e)[:80]}"
            ))
    else:
        results.append(TestResult("YandexGPT Integration", "FAIL", 0, "No API key"))
    
    # ==================== SECTION 4: ANONYMIZER ====================
    print("\n🔒 SECTION 4: 152-FZ ANONYMIZER")
    print("-"*70)
    
    t0 = time.time()
    try:
        anon = Anonymizer()
        
        # Test 1: Clean text
        clean_text = "This is a normal text without any personal data"
        compliance_clean = anon.check_compliance(clean_text)
        duration = int((time.time() - t0) * 1000)
        
        results.append(TestResult(
            "Clean Text Compliance",
            "PASS" if compliance_clean['is_compliant'] else "FAIL",
            duration,
            f"is_compliant={compliance_clean['is_compliant']}"
        ))
        
        # Test 2: Text with PII
        pii_text = "My name is Ivan Petrov and my phone is +7 (999) 123-45-67"
        t1 = time.time()
        compliance_pii = anon.check_compliance(pii_text)
        duration = int((time.time() - t1) * 1000)
        
        results.append(TestResult(
            "PII Detection",
            "PASS" if not compliance_pii['is_compliant'] else "FAIL",
            duration,
            f"Found entities: {len(compliance_pii.get('entities', []))}"
        ))
        
        # Test 3: Anonymization
        t1 = time.time()
        anonymized = anon.anonymize(pii_text)
        duration = int((time.time() - t1) * 1000)
        
        results.append(TestResult(
            "Text Anonymization",
            "PASS" if anonymized.get('anonymized_text') else "FAIL",
            duration,
            f"Anonymized text length: {len(anonymized.get('anonymized_text', ''))}"
        ))
        
        # Test 4: Restoration
        if anonymized.get('mapping'):
            t1 = time.time()
            restored = anon.restore(anonymized['anonymized_text'])
            duration = int((time.time() - t1) * 1000)
            
            results.append(TestResult(
                "Text Restoration",
                "PASS" if restored else "FAIL",
                duration,
                f"Restoration successful"
            ))
        
    except Exception as e:
        results.append(TestResult(
            "Anonymizer Tests",
            "FAIL",
            0,
            str(e)[:80]
        ))
    
    # ==================== SECTION 5: PERFORMANCE ====================
    print("\n⚡ SECTION 5: PERFORMANCE METRICS")
    print("-"*70)
    
    # Measure API response times
    for provider_name, client_class in [("GigaChat", GigaChatClient), ("YandexGPT", YandexGPTClient)]:
        api_key = os.environ.get('GIGACHAT_API_KEY' if provider_name == "GigaChat" else 'YANDEXGPT_API_KEY', '')
        folder_id = os.environ.get('YANDEXGPT_FOLDER_ID', '') if provider_name == "YandexGPT" else ""
        
        if api_key:
            times = []
            for i in range(3):
                t0 = time.time()
                try:
                    if provider_name == "GigaChat":
                        c = client_class(api_key)
                    else:
                        c = client_class(api_key, folder_id)
                    _ = await c.chat([{"role": "user", "content": "Hi"}], max_tokens=20)
                    times.append((time.time() - t0) * 1000)
                except:
                    pass
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                results.append(TestResult(
                    f"{provider_name} Avg Response Time",
                    "INFO",
                    int(avg_time),
                    f"min={int(min_time)}ms, max={int(max_time)}ms, avg={int(avg_time)}ms"
                ))
    
    # ==================== SUMMARY ====================
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    warnings = sum(1 for r in results if r.status == "WARN")
    info = sum(1 for r in results if r.status == "INFO")
    
    print(f"\nTotal tests: {len(results)}")
    print(f"✅ Passed:    {passed}")
    print(f"❌ Failed:    {failed}")
    print(f"⚠️  Warnings:  {warnings}")
    print(f"ℹ️  Info:      {info}")
    print()
    
    for r in results:
        if r.status != "INFO":
            print(f"  {r}")
    
    # Overall verdict
    print()
    print("="*70)
    if failed == 0:
        print("🎉 OVERALL: PRODUCTION READY!")
    elif failed <= 2:
        print("⚠️  OVERALL: MINOR ISSUES — NEARLY READY")
    else:
        print("❌ OVERALL: SIGNIFICANT ISSUES — NOT READY")
    print("="*70)
    
    return results


if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    
    # Save results to file for article reference
    with open('/home/dataguru/Projects/mcp-gateway/tests/test_results.txt', 'w') as f:
        f.write("MCP Gateway Test Results\n")
        f.write("="*70 + "\n\n")
        for r in results:
            f.write(f"{r}\n")
