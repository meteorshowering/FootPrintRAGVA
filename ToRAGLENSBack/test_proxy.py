"""
【功能】向代理网关发 Gemini generateContent 测试请求（Hello）。
【长期价值】连通性探测脚本；可删或并入 CI 外部检查。
"""
import requests
import json

GEMINI_API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
GEMINI_MODEL_NAME = "gemini-3-pro-image-preview"
API_ENDPOINT = f"http://38.147.105.35:3030/v1/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

request_payload = {
    "contents": [
        {
            "role": "user",
            "parts": [{"text": "Hello!"}]
        }
    ],
    "generationConfig": {
        "temperature": 0.2,
        "response_mime_type": "application/json"
    }
}

try:
    response = requests.post(
        API_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json=request_payload,
        timeout=120
    )
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(e)
