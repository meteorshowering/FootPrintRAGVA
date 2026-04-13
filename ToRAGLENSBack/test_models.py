import requests

GEMINI_API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
url = "http://38.147.105.35:3030/v1/models"
headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
try:
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        models = resp.json().get("data", [])
        qwen_models = [m["id"] for m in models if "qwen" in m["id"].lower()]
        deepseek_models = [m["id"] for m in models if "deepseek" in m["id"].lower()]
        print("Qwen models:")
        for q in qwen_models:
            print(f"  - {q}")
        print("DeepSeek models:")
        for d in deepseek_models:
            print(f"  - {d}")
        print("Total models:", len(models))
    else:
        print("Failed", resp.status_code, resp.text)
except Exception as e:
    print(e)
