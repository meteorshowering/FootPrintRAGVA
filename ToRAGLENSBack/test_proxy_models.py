"""
【功能】列出 /v1/models 中 gemini/gpt-4/claude 相关 id。
【长期价值】一次性脚本；可删。
"""
import requests
GEMINI_API_KEY = "sk-xuKetsCRvjQRkRVhnFu4SSlqNvG7j0Cie0Cj8n7Y7SikUUM5"
url = "http://38.147.105.35:3030/v1/models"
headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
try:
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        models = resp.json().get("data", [])
        for m in models:
            if "gemini" in m["id"] or "gpt-4" in m["id"] or "claude" in m["id"]:
                print(m["id"])
        print("Total models:", len(models))
    else:
        print("Failed", resp.status_code, resp.text)
except Exception as e:
    print(e)
