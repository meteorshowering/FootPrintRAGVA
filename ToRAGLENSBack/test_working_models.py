import requests

GEMINI_API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
url = "http://38.147.105.35:3030/v1/chat/completions"
headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}

models_to_test = [
    "gemini-3-pro-image-preview",
    "gemini-3.1-pro-preview",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gpt-4o",
    "gpt-4o-mini",
    "gemini-exp-1206",
    "gemini-2.5-pro",
    "gemini-2.0-flash"
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
    except Exception as e:
        print(f"{model}: {e}")
