#!/usr/bin/env python3
"""
全面测试所有模型的功能性
测试目标：对所有可用模型进行 "7×8=?" 数学推理测试
输出：可解析的JSON报告，包含每个模型的响应、状态、延迟
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
import requests

# === 配置 ===
TEST_PROMPT = "What is 7 multiplied by 8? Reply with only the number."
EXPECTED_ANSWER = "56"
TIMEOUT_SECONDS = 30
OUTPUT_DIR = "outputs"
TEST_RESULT_FILE = f"{OUTPUT_DIR}/full_model_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
MODEL_CONFIG_PATH = "C:\\Users\\Haide\\.openclaw\\openclaw.json"

# 从 openclaw.json 提取所有模型列表
def load_models_from_config():
    try:
        with open(MODEL_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ 未找到模型配置文件: ", MODEL_CONFIG_PATH)
        sys.exit(1)
    
    models = []
    
    # 1. 检查 providers （直接模型）
    providers = config.get('models', {}).get('providers', {})
    for provider_name, provider in providers.items():
        if 'models' in provider:
            for model in provider['models']:
                model_id = model.get('id')
                if model_id and model_id not in models:
                    models.append(model_id)
    
    # 2. 检查 agents.defaults.models 中的 alias 列表（包含别名和直接名称）
    models_from_agents = config.get('agents', {}).get('defaults', {}).get('models', {})
    for alias, model_config in models_from_agents.items():
        if isinstance(model_config, dict):
            # 如果是别名映射，生成直接模型ID
            model_id = alias  # 别名本身可直接用于 API 调用
            if model_id not in models:
                models.append(model_id)
        else:
            # 如果是简单字符串，忽略（可能是占位）
            pass
    
    # 3. 忽略已知禁用或没必要测试的模型（如图像模型、特殊路由等）
    excluded_keywords = [
        'reject', 'audio', 'image', 'extended', 'thinking', 'exacto',
        'free', 'free:free', 'devstral', 'test', 'unknown'
    ]
    filtered_models = []
    for model_id in models:
        if any(kw in model_id.lower() for kw in excluded_keywords):
            continue
        # 过滤掉带路径的签名：如 "openrouter/openai/gpt-4o" 只保留 "openai/gpt-4o"
        if model_id.startswith("openrouter/"):
            clean_model_id = model_id.replace("openrouter/", "", 1)
            if clean_model_id not in filtered_models:
                filtered_models.append(clean_model_id)
        else:
            if model_id not in filtered_models:
                filtered_models.append(model_id)
    
    return sorted(list(set(filtered_models)))

# 测试单个模型
def test_model(model_id, api_key):
    """测试单个模型是否能正确计算 7*8"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "OpenClaw Full Model Test"
    }
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        "max_tokens": 10,
        "temperature": 0.0,
        "top_p": 1
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
        latency_ms = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"].strip().replace(" ", "")
                # 检查是否包含正确答案
                is_correct = any(str(n) in content for n in ["56", "fifty-six"])
                return {
                    "model": model_id,
                    "status": "success",
                    "latency_ms": latency_ms,
                    "answer": content,
                    "correct": is_correct,
                    "error": None,
                    "http_code": 200
                }
            else:
                return {
                    "model": model_id,
                    "status": "error",
                    "latency_ms": latency_ms,
                    "answer": None,
                    "correct": False,
                    "error": "No choices in response",
                    "http_code": 200
                }
        else:
            error_msg = response.text[:200]
            return {
                "model": model_id,
                "status": "http_error",
                "latency_ms": latency_ms,
                "answer": None,
                "correct": False,
                "error": f"HTTP {response.status_code}: {error_msg}",
                "http_code": response.status_code
            }
    except requests.Timeout:
        return {
            "model": model_id,
            "status": "timeout",
            "latency_ms": TIMEOUT_SECONDS * 1000,
            "answer": None,
            "correct": False,
            "error": f"Timeout after {TIMEOUT_SECONDS}s",
            "http_code": None
        }
    except requests.RequestException as e:
        return {
            "model": model_id,
            "status": "request_error",
            "latency_ms": 0,
            "answer": None,
            "correct": False,
            "error": str(e)[:300],
            "http_code": None
        }
    except Exception as e:
        return {
            "model": model_id,
            "status": "unknown_error",
            "latency_ms": 0,
            "answer": None,
            "correct": False,
            "error": str(e)[:300],
            "http_code": None
        }

# 主程序
def main():
    print("🧪 正在加载全部可用模型... (这可能会花费一分钟)")
    models = load_models_from_config()
    print(f"✅ 找到 {len(models)} 个候选模型")
    
    # 检查 API Key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ 未设置 OPENROUTER_API_KEY")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 测试每个模型
    print(f"\n🚀 开始测试 {len(models)} 个模型... 这将需要约 {len(models)*15} 秒 (约 {len(models)*15//60} 分钟)")
    results = []
    total = len(models)
    
    for i, model in enumerate(models, 1):
        print(f"[{i}/{total}] 测试 {model}...", end=" ", flush=True)
        result = test_model(model, api_key)
        results.append(result)
        
        status_emoji = "✅" if result["correct"] else "❌" if result["status"] == "success" else "⚠️"
        print(f"{status_emoji} {result['status']} ({result['latency_ms']}ms)")
        
        # 每10个模型保存一次，防止中断丢失
        if i % 10 == 0:
            with open(TEST_RESULT_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_prompt": TEST_PROMPT,
                    "expected_answer": EXPECTED_ANSWER,
                    "total_models": len(models),
                    "completed_at": datetime.now().isoformat(),
                    "results": results
                }, f, indent=2, ensure_ascii=False)
    
    # 最终结果
    correct_count = sum(1 for r in results if r["correct"])
    successful_count = sum(1 for r in results if r["status"] == "success")
    
    final_report = {
        "test_prompt": TEST_PROMPT,
        "expected_answer": EXPECTED_ANSWER,
        "total_models": len(models),
        "correct_models": correct_count,
        "successful_models": successful_count,
        "completed_at": datetime.now().isoformat(),
        "results": results
    }
    
    with open(TEST_RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n✨ 测试完成！")
    print(f"✅ 正确回答模型数: {correct_count}/{len(models)} ({correct_count/len(models)*100:.1f}%)")
    print(f"💾 结果保存至: {TEST_RESULT_FILE}")
    
    # 输出可用模型列表（仅成功且正确的）
    available_models = [r["model"] for r in results if r["correct"]]
    if available_models:
        print("\n📥 生成可用模型列表（用于 fallback）:")
        for m in available_models:
            print(f"- {m}")
            
if __name__ == "__main__":
    main()
