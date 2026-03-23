#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Model Test - ASCII Version
Test all available models with simple math question
"""

import os
import sys
import json
import time
from datetime import datetime
import requests

# Config
TEST_PROMPT = "What is 7 multiplied by 8? Reply with only the number."
EXPECTED = "56"
TIMEOUT = 30
OUTPUT_DIR = "outputs"
CONFIG_PATH = r"C:\Users\Haide\.openclaw\openclaw.json"

def load_all_models():
    """Extract all model IDs from config"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"ERROR: Cannot load config: {e}")
        sys.exit(1)
    
    models = set()
    
    # From providers
    providers = config.get('models', {}).get('providers', {})
    for provider_name, provider in providers.items():
        if 'models' in provider:
            for m in provider['models']:
                mid = m.get('id')
                if mid:
                    # Clean up model IDs
                    if mid.startswith('openrouter/'):
                        mid = mid.replace('openrouter/', '', 1)
                    models.add(mid)
    
    # From agents.defaults.models aliases
    agent_models = config.get('agents', {}).get('defaults', {}).get('models', {})
    for alias in agent_models.keys():
        if '/' in alias and not alias.startswith('openrouter/'):
            models.add(alias)
        elif alias.startswith('openrouter/'):
            models.add(alias.replace('openrouter/', '', 1))
    
    # Filter out problematic patterns
    filtered = []
    skip_keywords = ['reject', 'audio', 'image', 'extended', 'thinking', 'exacto', 'test', 'unknown']
    for m in sorted(models):
        if any(kw in m.lower() for kw in skip_keywords):
            continue
        if ':' in m and 'free' not in m.lower():
            # Skip versioned models unless free
            continue
        filtered.append(m)
    
    return filtered

def test_model(model_id, api_key):
    """Test single model"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "Model Test"
    }
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        "max_tokens": 10,
        "temperature": 0
    }
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        latency = int((time.time() - start) * 1000)
        
        if resp.status_code == 200:
            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"].strip()
                is_correct = EXPECTED in content
                return {
                    "model": model_id,
                    "status": "success",
                    "latency_ms": latency,
                    "answer": content,
                    "correct": is_correct,
                    "error": None
                }
            else:
                return {"model": model_id, "status": "no_choices", "latency_ms": latency, "answer": None, "correct": False, "error": "Empty response"}
        else:
            return {"model": model_id, "status": f"http_{resp.status_code}", "latency_ms": latency, "answer": None, "correct": False, "error": resp.text[:100]}
    except requests.Timeout:
        return {"model": model_id, "status": "timeout", "latency_ms": TIMEOUT*1000, "answer": None, "correct": False, "error": "Timeout"}
    except Exception as e:
        return {"model": model_id, "status": "error", "latency_ms": 0, "answer": None, "correct": False, "error": str(e)[:100]}

def main():
    print("="*60)
    print("FULL MODEL TEST - All Available Models")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)
    
    print("Loading models from config...")
    models = load_all_models()
    print(f"Found {len(models)} models to test")
    print(f"Estimated time: {len(models) * 15 // 60} minutes")
    print("="*60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"{OUTPUT_DIR}/full_test_{timestamp}.json"
    
    results = []
    correct_count = 0
    success_count = 0
    
    for i, model in enumerate(models, 1):
        print(f"[{i:3d}/{len(models)}] Testing {model}... ", end="", flush=True)
        result = test_model(model, api_key)
        results.append(result)
        
        if result["correct"]:
            print(f"CORRECT ({result['latency_ms']}ms)")
            correct_count += 1
            success_count += 1
        elif result["status"] == "success":
            print(f"WRONG: {result['answer'][:30]}")
            success_count += 1
        else:
            print(f"{result['status'].upper()}")
        
        # Save progress every 10 models
        if i % 10 == 0:
            with open(result_file, 'w') as f:
                json.dump({"partial": True, "completed": i, "total": len(models), "results": results}, f, indent=2)
    
    # Final report
    report = {
        "test_prompt": TEST_PROMPT,
        "expected_answer": EXPECTED,
        "total_models": len(models),
        "successful_requests": success_count,
        "correct_answers": correct_count,
        "accuracy_rate": round(correct_count / len(models) * 100, 1) if models else 0,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(result_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("="*60)
    print("TEST COMPLETE")
    print(f"Total: {len(models)}")
    print(f"Correct: {correct_count} ({report['accuracy_rate']}%)")
    print(f"Failed: {len(models) - success_count}")
    print(f"Results saved to: {result_file}")
    
    # Print usable models
    usable = [r["model"] for r in results if r["correct"]]
    if usable:
        print("\nUsable models for fallback:")
        for m in usable:
            print(f"  - {m}")

if __name__ == "__main__":
    main()
