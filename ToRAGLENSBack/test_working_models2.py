"""
【功能】探测 qwen2.5-vl、deepseek-ocr、qwen3.5 等模型可用性。
【长期价值】一次性脚本；可删。
"""
import requests

GEMINI_API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
url = "http://38.147.105.35:3030/v1/chat/completions"
headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}

models_to_test = [
    "qwen2.5-vl:72b",
    "deepseek-ocr",
    "qwen3.5"
]

for model in models_to_test:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi!"}],
        "max_tokens": 5
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"{model}: {resp.status_code}")
        if resp.status_code == 200:
            print("  SUCCESS!")
        else:
            print("  ERROR:", resp.text)
    except Exception as e:
        print(f"{model}: {e}")
