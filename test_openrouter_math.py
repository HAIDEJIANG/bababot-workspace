#!/usr/bin/env python3
"""
OpenRouter Model Math Test
Tests if models can correctly answer simple math problems
"""

import os
import sys
import json
import time
from datetime import datetime

TEST_PROMPT = "What is 7 multiplied by 8? Please provide only the numerical answer."
EXPECTED_ANSWER = "56"
TIMEOUT = 30
OUTPUT_DIR = "outputs"

# Hardcoded list of 29 curated models (as per user's request to test the ~30 models)
FALLBACK_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-5",
    "openai/gpt-5-codex",
    "openai/gpt-5.2-codex",
    "openai-codex/gpt-5.3-codex",
    "openai-codex/gpt-5.3-codex-spark",
    "openai/o1",
    "openai/o3",
    "openai/o3-deep-research",
    "anthropic/claude-3.5-haiku",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-opus-4",
    "anthropic/claude-3.7-sonnet",
    "google/gemini-2.0-flash-001",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "deepseek/deepseek-chat",
    "deepseek/deepseek-reasoner",
    "moonshot/kimi-k2.5",
    "mistralai/mistral-large",
    "mistralai/codestral-2508",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen-portal/qwen3-235b-a22b",
    "qwen-portal/qwen3-30b-a3b",
    "cohere/command-r-plus-08-2024",
    "alibaba/tongyi-deepresearch-30b-a3b",
    "x-ai/grok-3-mini",
    "x-ai/grok-4-mini"
]

def test_model_math(model_id, api_key):
    import requests
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "OpenClaw Model Math Test"
    }
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        "max_tokens": 50,
        "temperature": 0
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        latency = (time.time() - start_time) * 1000
        
        if response.status_code != 200:
            return {
                "model": model_id,
                "status": "error",
                "error": f"HTTP {response.status_code}: {response.text[:100]}",
                "latency_ms": latency,
                "answer": None,
                "correct": False
            }
        
        data = response.json()
        if "choices" not in data or len(data["choices"]) == 0:
            return {
                "model": model_id,
                "status": "error",
                "error": "No choices in response",
                "latency_ms": latency,
                "answer": None,
                "correct": False
            }
        
        answer = data["choices"][0]["message"]["content"].strip()
        is_correct = EXPECTED_ANSWER in answer
        
        return {
            "model": model_id,
            "status": "success",
            "error": None,
            "latency_ms": round(latency, 2),
            "answer": answer,
            "correct": is_correct
        }
        
    except requests.Timeout:
        return {
            "model": model_id,
            "status": "timeout",
            "error": f"Timeout after {TIMEOUT}s",
            "latency_ms": TIMEOUT * 1000,
            "answer": None,
            "correct": False
        }
    except Exception as e:
        return {
            "model": model_id,
            "status": "exception",
            "error": str(e),
            "latency_ms": 0,
            "answer": None,
            "correct": False
        }

def generate_report(results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = f"{OUTPUT_DIR}/openrouter_math_test_{timestamp}.md"
    json_file = f"{OUTPUT_DIR}/openrouter_math_test_{timestamp}.json"
    
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    errors = sum(1 for r in results if r["status"] != "success")
    success_rate = (correct / total * 100) if total > 0 else 0
    
    correct_models = [r for r in results if r["correct"]]
    wrong_models = [r for r in results if r["status"] == "success" and not r["correct"]]
    error_models = [r for r in results if r["status"] != "success"]
    
    # Ensure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_prompt": TEST_PROMPT,
            "expected_answer": EXPECTED_ANSWER,
            "total_models": total,
            "correct_count": correct,
            "error_count": errors,
            "success_rate": success_rate,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    md = f"""# OpenRouter Model Math Test Report

Test Time: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
Test Question: {TEST_PROMPT}  
Expected Answer: {EXPECTED_ANSWER}  
Total Models: {total}  
Correct: {correct} ({success_rate:.1f}%)  
Errors/Timeout: {errors}

---

## Summary

| Metric | Value |
|--------|-------|
| Total Models | {total} |
| Correct | {correct} |
| Wrong | {len(wrong_models)} |
| Failed | {len(error_models)} |
| Accuracy | {success_rate:.1f}% |

---

## Correct Models ({len(correct_models)})

| Rank | Model | Latency(ms) | Answer |
|------|-------|-------------|--------|
"""
    
    for i, r in enumerate(sorted(correct_models, key=lambda x: x["latency_ms"]), 1):
        answer_short = r['answer'][:50] + '...' if len(r['answer']) > 50 else r['answer']
        md += f"| {i} | `{r['model']}` | {r['latency_ms']} | {answer_short} |\n"
    
    md += f"""

---

## Wrong Answer Models ({len(wrong_models)})

| Model | Latency(ms) | Answer |
|-------|-------------|--------|
"""
    
    for r in sorted(wrong_models, key=lambda x: x["latency_ms"]):
        answer_short = r['answer'][:50] + '...' if len(r['answer']) > 50 else r['answer']
        md += f"| `{r['model']}` | {r['latency_ms']} | {answer_short} |\n"
    
    md += f"""

---

## Failed Models ({len(error_models)})

| Model | Status | Error |
|-------|--------|-------|
"""
    
    for r in error_models:
        error_msg = r['error'][:40] + '...' if r['error'] and len(r['error']) > 40 else (r['error'] or '')
        md += f"| `{r['model']}` | {r['status']} | {error_msg} |\n"
    
    md += f"""

---

## Raw Data

JSON saved to: `{json_file}`

---

## Recommendations

**Top Reliable Models** (correct + fast):
"""
    
    top_models = sorted(correct_models, key=lambda x: x["latency_ms"])[:10]
    for i, r in enumerate(top_models, 1):
        md += f"{i}. `{r['model']}` ({r['latency_ms']}ms)\n"
    
    md += f"""
**Avoid These** (wrong or failed):
"""
    
    for r in wrong_models[:5]:
        md += f"- `{r['model']}`: wrong answer\n"
    for r in error_models[:5]:
        md += f"- `{r['model']}`: {r['status']}\n"
    
    md += """
---

*Generated by OpenClaw*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    return report_file, json_file

def main():
    print("=" * 60)
    print("OpenRouter Model Math Test")
    print("=" * 60)
    print(f"Question: {TEST_PROMPT}")
    print(f"Expected: {EXPECTED_ANSWER}")
    print("=" * 60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)
    
    models = FALLBACK_MODELS
    print(f"\n[1/3] Loaded {len(models)} models from curated list")
    
    print(f"\n[2/3] Testing each model...")
    print("-" * 60)
    
    results = []
    for i, model in enumerate(models, 1):
        print(f"[{i}/{len(models)}] Testing {model}... ", end="", flush=True)
        result = test_model_math(model, api_key)
        results.append(result)
        
        if result["correct"]:
            print(f"CORRECT ({result['latency_ms']:.0f}ms)")
        elif result["status"] == "success":
            print(f"WRONG: {result['answer'][:40]}")
        else:
            print(f"{result['status'].upper()}: {result['error'][:30]}")
    
    print("\n" + "=" * 60)
    print("[3/3] Generating report...")
    report_file, json_file = generate_report(results)
    
    print(f"\nDONE!")
    print(f"Report: {report_file}")
    print(f"Data: {json_file}")
    
    correct_count = sum(1 for r in results if r["correct"])
    error_count = sum(1 for r in results if r["status"] != "success")
    print(f"\nSummary:")
    print(f"  - Total: {len(results)}")
    print(f"  - Correct: {correct_count} ({correct_count/len(results)*100:.1f}%)")
    print(f"  - Wrong: {len(results) - correct_count - error_count}")
    print(f"  - Failed: {error_count}")

if __name__ == "__main__":
    main()
