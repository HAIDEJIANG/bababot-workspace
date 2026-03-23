#!/usr/bin/env python3
"""
Second Round Test - Logic Reasoning
Test models that passed first round (7x8=56) with logic problem
"""

import os
import sys
import json
import time
from datetime import datetime
import requests

# Models that passed first round (math test)
ROUND1_PASS = [
    "ai21/jamba-large-1.7",
    "allenai/olmo-3.1-32b-instruct",
    "amazon/nova-2-lite-v1",
    "amazon/nova-lite-v1",
    "amazon/nova-micro-v1",
    "amazon/nova-premier-v1",
    "amazon/nova-pro-v1",
    "anthropic/claude-3-haiku",
    "anthropic/claude-3.5-haiku",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-haiku-4.5",
    "anthropic/claude-opus-4.5",
    "anthropic/claude-opus-4.6",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-sonnet-4.6",
    "arcee-ai/trinity-large-preview:free",
    "auto",
    "baidu/ernie-4.5-21b-a3b",
    "bytedance-seed/seed-1.6",
    "bytedance-seed/seed-1.6-flash",
    "cohere/command-r-08-2024",
    "cohere/command-r-plus-08-2024",
    "deepseek/deepseek-chat",
    "deepseek/deepseek-chat-v3-0324",
    "deepseek/deepseek-chat-v3.1",
    "deepseek/deepseek-r1",
    "deepseek/deepseek-v3.1-terminus",
    "deepseek/deepseek-v3.2",
    "deepseek/deepseek-v3.2-exp",
    "google/gemini-2.0-flash-001",
    "google/gemini-2.0-flash-lite-001",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-flash-lite",
    "google/gemini-2.5-flash-lite-preview-09-2025",
    "google/gemini-3-flash-preview",
    "google/gemma-3-27b-it",
    "inception/mercury",
    "inception/mercury-coder",
    "kwaipilot/kat-coder-pro",
    "meituan/longcat-flash-chat",
    "meta-llama/llama-3-8b-instruct",
    "meta-llama/llama-3.1-70b-instruct",
    "meta-llama/llama-3.1-8b-instruct",
    "meta-llama/llama-3.3-70b-instruct",
    "meta-llama/llama-4-maverick",
    "meta-llama/llama-4-scout"
]

TEST_PROMPT = "John is taller than Mary. Mary is taller than Bob. Is John taller than Bob? Answer with only Yes or No."
EXPECTED_ANSWERS = ["yes", "true", "correct", "是", "对"]
TIMEOUT = 30
OUTPUT_DIR = "outputs"

def test_logic(model_id, api_key):
    """Test logic reasoning"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "Logic Test"
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
                content = data["choices"][0]["message"]["content"].strip().lower()
                # Check if answer contains yes/true/correct
                is_correct = any(ans in content for ans in EXPECTED_ANSWERS)
                return {
                    "model": model_id,
                    "status": "success",
                    "latency_ms": latency,
                    "answer": content,
                    "correct": is_correct,
                    "error": None
                }
            else:
                return {"model": model_id, "status": "no_choices", "latency_ms": latency, "answer": None, "correct": False, "error": "Empty"}
        else:
            return {"model": model_id, "status": f"http_{resp.status_code}", "latency_ms": latency, "answer": None, "correct": False, "error": resp.text[:50]}
    except Exception as e:
        return {"model": model_id, "status": "error", "latency_ms": 0, "answer": None, "correct": False, "error": str(e)[:50]}

def main():
    print("="*60)
    print("SECOND ROUND TEST - Logic Reasoning")
    print("="*60)
    print(f"Models from Round 1: {len(ROUND1_PASS)}")
    print(f"Question: {TEST_PROMPT}")
    print(f"Expected: Yes/True/Correct")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"{OUTPUT_DIR}/round2_logic_test_{timestamp}.json"
    
    results = []
    passed_both = []
    
    for i, model in enumerate(ROUND1_PASS, 1):
        print(f"[{i:2d}/{len(ROUND1_PASS)}] Testing {model}... ", end="", flush=True)
        result = test_logic(model, api_key)
        results.append(result)
        
        if result["correct"]:
            print(f"CORRECT ({result['latency_ms']}ms) - PASSED BOTH ROUNDS")
            passed_both.append(model)
        elif result["status"] == "success":
            print(f"WRONG: {result['answer'][:30]}")
        else:
            print(f"{result['status'].upper()}")
    
    # Save results
    report = {
        "round": 2,
        "test_prompt": TEST_PROMPT,
        "expected": EXPECTED_ANSWERS,
        "total_tested": len(ROUND1_PASS),
        "passed_both": len(passed_both),
        "pass_rate": round(len(passed_both)/len(ROUND1_PASS)*100, 1),
        "timestamp": datetime.now().isoformat(),
        "qualified_models": passed_both,
        "all_results": results
    }
    
    with open(result_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("="*60)
    print("ROUND 2 COMPLETE")
    print(f"Models tested: {len(ROUND1_PASS)}")
    print(f"Passed both rounds: {len(passed_both)} ({report['pass_rate']}%)")
    print(f"Results saved: {result_file}")
    print("="*60)
    print("\nQUALIFIED MODELS FOR FALLBACK LIST:")
    for i, m in enumerate(passed_both, 1):
        print(f"{i:2d}. {m}")

if __name__ == "__main__":
    main()
