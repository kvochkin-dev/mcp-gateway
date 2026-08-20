# YandexGPT API Integration Status

## Account Status
- **Account:** account-477
- **Balance:** 0.00 ₽
- **Grant:** 4,000 ₽ (60 days until 18.10.2026)
- **Status:** ✅ Free tier available for testing

## API Configuration
- **API Key:** AQVN***REDACTED***_wfc
- **Folder ID:** ajepemgfdqapklq02f45
- **Base URL:** https://llm.api.cloud.yandex.net

## Tested Endpoints

### Models (✅ Working)
```
GET /v1/models
Headers: Authorization: Api-key {key}, X-folder-id: {folder_id}
```
Returns available models with IDs like `gpt://b1gdj4u8tlg7e9q1co7c/aliceai-llm/latest`

### Chat (🔄 Testing)
Need to find correct endpoint format.

---

## Known Issues
- `/generativeLLMs/v1/models` returns 404
- `/generativeLLMs/v1/llm` returns 404
- `/v1/models` works correctly
- `/v1/chat/completions` needs testing

---

## Next Steps
1. Test chat completions endpoint
2. Verify model URI format for requests
3. Update YandexGPT client code
4. Test fallback orchestration
