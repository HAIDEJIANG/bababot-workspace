import requests
import os
import time
import json
from datetime import datetime

API_KEY = os.environ.get('OPENROUTER_API_KEY')
API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openclaw.ai",
    "X-Title": "OpenClaw Stability Test"
}

def test_model(model):
    """测试单个模型"""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 1
    }
    
    max_retries = 2
    retries = 0
    
    while retries <= max_retries:
        try:
            start_time = time.time()
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "model": model,
                    "success": True,
                    "response_time_ms": round(response_time_ms, 2),
                    "status_code": response.status_code,
                    "error": None
                }
            elif response.status_code in [429, 500, 502, 503, 504]:
                if retries < max_retries:
                    retries += 1
                    time.sleep(1)
                    continue
                else:
                    return {
                        "model": model,
                        "success": False,
                        "response_time_ms": round(response_time_ms, 2),
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}: {response.text[:100]}"
                    }
            else:
                return {
                    "model": model,
                    "success": False,
                    "response_time_ms": round(response_time_ms, 2),
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "model": model,
                "success": False,
                "response_time_ms": 10000,
                "status_code": 0,
                "error": "Timeout (10s)"
            }
        except Exception as e:
            return {
                "model": model,
                "success": False,
                "response_time_ms": 0,
                "status_code": 0,
                "error": str(e)[:100]
            }
    
    return {
        "model": model,
        "success": False,
        "response_time_ms": 0,
        "status_code": 0,
        "error": "Max retries exceeded"
    }

def main():
    # 读取模型列表
    with open('openrouter_models_fixed.txt', 'r', encoding='utf-8') as f:
        models = [line.strip() for line in f if line.strip()]
    
    total_models = len(models)
    print(f"开始测试 {total_models} 个模型...")
    print("使用顺序测试，每10个模型报告一次进度")
    print("=" * 60)
    
    start_time = time.time()
    results = []
    successful = []
    failed = []
    
    for i, model in enumerate(models, 1):
        # 每10个模型或每2分钟报告一次进度
        if i % 10 == 0 or i == 1:
            elapsed_minutes = (time.time() - start_time) / 60
            print(f"[进度] 已测试 {i}/{total_models} 个模型，已用时 {elapsed_minutes:.1f} 分钟")
        
        result = test_model(model)
        results.append(result)
        
        if result["success"]:
            successful.append(result)
            print(f"  {i:3}/{total_models}: {model} - OK ({result['response_time_ms']}ms)")
        else:
            failed.append(result)
            print(f"  {i:3}/{total_models}: {model} - FAIL: {result['error']}")
        
        # 避免速率限制
        time.sleep(0.1)
    
    end_time = time.time()
    total_duration_minutes = (end_time - start_time) / 60
    
    # 分析结果
    success_count = len(successful)
    fail_count = len(failed)
    success_rate = (success_count / total_models * 100) if total_models > 0 else 0
    
    # 计算平均延迟
    if success_count > 0:
        avg_latency = sum(r["response_time_ms"] for r in successful) / success_count
    else:
        avg_latency = 0
    
    # 按延迟排序
    successful_sorted = sorted(successful, key=lambda x: x["response_time_ms"])
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 生成报告
    report = f"""# OpenRouter 模型稳定性测试报告

## 测试概览
- **测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **总模型数**: {total_models}
- **成功数**: {success_count}
- **失败数**: {fail_count}
- **成功率**: {success_rate:.2f}%
- **平均延迟（成功模型）**: {avg_latency:.2f}ms
- **总测试时长**: {total_duration_minutes:.1f} 分钟

## 最快 10 个模型（按延迟排序）

| 排名 | 模型ID | 延迟(ms) | 状态码 |
|------|--------|----------|--------|
"""
    
    # 添加最快10个模型
    for i, result in enumerate(successful_sorted[:10], 1):
        report += f"| {i} | `{result['model']}` | {result['response_time_ms']}ms | {result['status_code']} |\n"
    
    report += f"""
## 失败模型列表 ({fail_count} 个)

| 模型ID | 状态码 | 错误信息 |
|--------|--------|----------|
"""
    
    # 添加失败模型
    for result in failed:
        error_msg = result['error'] or "Unknown error"
        status_code = result['status_code'] or "N/A"
        report += f"| `{result['model']}` | {status_code} | {error_msg} |\n"
    
    report += f"""
## 详细统计

### 成功率分布
- 成功: {success_count} 个 ({success_rate:.2f}%)
- 失败: {fail_count} 个 ({100 - success_rate:.2f}%)

### 延迟分布（成功模型）
"""
    
    if success_count > 0:
        latencies = [r["response_time_ms"] for r in successful]
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        latencies_sorted = sorted(latencies)
        p50 = latencies_sorted[int(len(latencies_sorted) * 0.5)]
        p90 = latencies_sorted[int(len(latencies_sorted) * 0.9)]
        p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
        
        report += f"""
- 最小延迟: {min_latency:.2f}ms
- 最大延迟: {max_latency:.2f}ms
- 平均延迟: {avg_latency:.2f}ms
- P50 (中位数): {p50:.2f}ms
- P90: {p90:.2f}ms
- P95: {p95:.2f}ms
"""
    
    report += f"""
## 建议

### 建议保留的模型（延迟低且稳定）
基于测试结果，建议优先使用以下模型（前20个低延迟）：
"""
    
    if len(successful_sorted) > 0:
        report += "\n1. " + "\n1. ".join([f"`{r['model']}` ({r['response_time_ms']}ms)" for r in successful_sorted[:20]])
    
    report += f"""

### 建议删除的模型（频繁失败或高延迟）
以下模型在测试中表现不佳，建议从 fallback 列表中移除：
"""
    
    # 找出常见的失败模式
    error_counts = {}
    for result in failed:
        error_key = result['error'] or "Unknown"
        error_counts[error_key] = error_counts.get(error_key, 0) + 1
    
    common_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    report += "\n**常见错误类型:**\n"
    for error, count in common_errors:
        report += f"- {error}: {count} 个模型\n"
    
    report += f"""
## 测试配置
- API端点: {API_URL}
- 请求超时: 10秒
- 重试策略: 429/5xx错误重试2次，每次间隔1秒
- 请求间隔: 100ms（避免速率限制）
- 测试消息: "Hi" (1个token)

## 原始数据
完整测试数据已保存到 `outputs/openrouter_test_results_{timestamp}.json`
"""
    
    # 保存报告
    os.makedirs("outputs", exist_ok=True)
    report_filename = f"outputs/openrouter_stability_report_{timestamp}.md"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到: {report_filename}")
    
    # 保存原始数据
    data_filename = f"outputs/openrouter_test_results_{timestamp}.json"
    with open(data_filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_models": total_models,
            "results": results,
            "statistics": {
                "success_count": success_count,
                "fail_count": fail_count,
                "success_rate": success_rate,
                "avg_latency": avg_latency,
                "total_duration_minutes": total_duration_minutes
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"原始数据已保存到: {data_filename}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("测试完成!")
    print(f"总模型: {total_models}, 成功: {success_count}, 失败: {fail_count}")
    print(f"成功率: {success_rate:.2f}%, 平均延迟: {avg_latency:.2f}ms")
    print(f"总用时: {total_duration_minutes:.1f} 分钟")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()