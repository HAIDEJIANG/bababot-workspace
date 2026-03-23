import requests
import os
import json

API_KEY = os.environ.get('OPENROUTER_API_KEY')
API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openclaw.ai",
    "X-Title": "OpenClaw Test"
}

# 测试一些已知的模型格式
test_models = [
    "openrouter/auto",  # 这个已经成功了
    "openrouter/free",  # 这个也成功了
    "anthropic/claude-3.5-sonnet",  # 去掉 openrouter/ 前缀
    "google/gemini-2.0-flash-001",  # 去掉 openrouter/ 前缀
    "openai/gpt-4o-mini",  # 去掉 openrouter/ 前缀
    "mistralai/mistral-large",  # 去掉 openrouter/ 前缀
    "meta-llama/llama-3.3-70b-instruct",  # 去掉 openrouter/ 前缀
    "qwen/qwen-plus",  # 去掉 openrouter/ 前缀
]

for model in test_models:
    print(f"测试模型: {model}")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 1
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"  [OK] 成功: HTTP {response.status_code}")
        else:
            print(f"  [FAIL] 失败: HTTP {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] 异常: {str(e)[:100]}")
    
    print()