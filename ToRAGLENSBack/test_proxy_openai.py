"""
【功能】向 /v1/chat/completions 发一条 Hello 测试 gemini-3-pro-image-preview。
【长期价值】一次性连通性脚本；可删。
"""
import requests

GEMINI_API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
url = "http://38.147.105.35:3030/v1/chat/completions"
headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
payload = {
    "model": "gemini-3-pro-image-preview",
    "messages": [{"role": "user", "content": "Hello!"}]
}

try:
    resp = requests.post(url, headers=headers, json=payload)
    print(resp.status_code)
    print(resp.text)
except Exception as e:
    print(e)
