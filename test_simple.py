import requests
import os
import time

API_KEY = os.environ.get('OPENROUTER_API_KEY')
API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openclaw.ai",
    "X-Title": "OpenClaw Test"
}

# 读取修复后的模型列表
with open('openrouter_models_fixed.txt', 'r', encoding='utf-8') as f:
    models = [line.strip() for line in f if line.strip()]

print(f"总共 {len(models)} 个模型需要测试")
print("测试前10个模型作为示例...")

results = []
for i, model in enumerate(models[:10], 1):
    print(f"\n测试 {i}/10: {model}")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 1
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            print(f"  [OK] 成功: {response_time_ms:.2f}ms")
            results.append({
                "model": model,
                "success": True,
                "response_time_ms": response_time_ms,
                "status_code": response.status_code
            })
        else:
            print(f"  [FAIL] 失败: HTTP {response.status_code} - {response.text[:100]}")
            results.append({
                "model": model,
                "success": False,
                "response_time_ms": response_time_ms,
                "status_code": response.status_code,
                "error": response.text[:200]
            })
    except Exception as e:
        print(f"  [ERROR] 异常: {str(e)[:100]}")
        results.append({
            "model": model,
            "success": False,
            "response_time_ms": 0,
            "status_code": 0,
            "error": str(e)[:200]
        })
    
    # 避免速率限制
    time.sleep(0.2)

print(f"\n测试完成!")
print(f"成功: {sum(1 for r in results if r['success'])}")
print(f"失败: {sum(1 for r in results if not r['success'])}")