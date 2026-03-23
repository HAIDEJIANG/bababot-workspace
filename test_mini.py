import requests
import os
import time

API_KEY = os.environ.get('OPENROUTER_API_KEY')
print(f"API Key exists: {bool(API_KEY)}")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openclaw.ai",
    "X-Title": "OpenClaw Test"
}

# 测试一个模型
model = "anthropic/claude-3.5-sonnet"
print(f"Testing model: {model}")

payload = {
    "model": model,
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 1
}

try:
    start = time.time()
    response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
    end = time.time()
    
    print(f"Status: {response.status_code}")
    print(f"Time: {(end-start)*1000:.2f}ms")
    
    if response.status_code == 200:
        print("Success!")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")