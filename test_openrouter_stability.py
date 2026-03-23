import requests
import time
import json
import sys
from datetime import datetime
import os

# OpenRouter API Key
API_KEY = os.environ.get('OPENROUTER_API_KEY')
if not API_KEY:
    print("错误: OPENROUTER_API_KEY 环境变量未设置")
    sys.exit(1)

# API endpoint
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openclaw.ai",
    "X-Title": "OpenClaw Stability Test"
}

# 读取模型列表
def load_models():
    models = []
    try:
        # 首先尝试读取修复后的模型列表
        with open('openrouter_models_fixed.txt', 'r', encoding='utf-8') as f:
            for line in f:
                model = line.strip()
                if model:
                    models.append(model)
    except FileNotFoundError:
        # 如果修复后的文件不存在，使用原始文件
        try:
            with open('openrouter_models.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    model = line.strip()
                    if model:
                        models.append(model)
        except FileNotFoundError:
            print("错误: openrouter_models.txt 文件不存在")
            sys.exit(1)
    
    print(f"加载了 {len(models)} 个模型进行测试")
    return models

# 测试单个模型
def test_model(model_id, max_retries=2):
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": "Hi"}
        ],
        "max_tokens": 1
    }
    
    retries = 0
    while retries <= max_retries:
        try:
            start_time = time.time()
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=5
            )
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "model": model_id,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time_ms, 2),
                    "success": True,
                    "error": None
                }
            elif response.status_code in [429, 500, 502, 503, 504]:
                # 可重试错误
                if retries < max_retries:
                    retries += 1
                    time.sleep(1)  # 等待1秒后重试
                    continue
                else:
                    return {
                        "model": model_id,
                        "status_code": response.status_code,
                        "response_time_ms": round(response_time_ms, 2),
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text[:100]}"
                    }
            else:
                return {
                    "model": model_id,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time_ms, 2),
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "model": model_id,
                "status_code": 0,
                "response_time_ms": 5000,  # 超时时间
                "success": False,
                "error": "Timeout (5s)"
            }
        except requests.exceptions.ConnectionError:
            return {
                "model": model_id,
                "status_code": 0,
                "response_time_ms": 0,
                "success": False,
                "error": "Connection Error"
            }
        except Exception as e:
            return {
                "model": model_id,
                "status_code": 0,
                "response_time_ms": 0,
                "success": False,
                "error": str(e)[:100]
            }
    
    return {
        "model": model_id,
        "status_code": 0,
        "response_time_ms": 0,
        "success": False,
        "error": "Max retries exceeded"
    }

# 主测试函数
def main():
    models = load_models()
    total_models = len(models)
    
    results = []
    successful = []
    failed = []
    
    print(f"开始测试 {total_models} 个模型...")
    print("=" * 60)
    
    start_time = time.time()
    
    for i, model_id in enumerate(models, 1):
        # 每10分钟输出一次进度
        if i % 50 == 0 or i == 1:
            elapsed_minutes = (time.time() - start_time) / 60
            print(f"[进度] 已测试 {i}/{total_models} 个模型，已用时 {elapsed_minutes:.1f} 分钟")
        
        print(f"测试 {i}/{total_models}: {model_id}")
        
        result = test_model(model_id)
        results.append(result)
        
        if result["success"]:
            successful.append(result)
            print(f"  [OK] 成功: {result['response_time_ms']}ms")
        else:
            failed.append(result)
            print(f"  [FAIL] 失败: {result['error']}")
        
        # 避免速率限制
        time.sleep(0.1)
    
    end_time = time.time()
    total_duration_minutes = (end_time - start_time) / 60
    
    # 生成报告
    generate_report(results, successful, failed, total_duration_minutes)
    
    return results

# 生成报告
def generate_report(results, successful, failed, total_duration_minutes):
    # 计算统计数据
    total_models = len(results)
    success_count = len(successful)
    fail_count = len(failed)
    success_rate = (success_count / total_models * 100) if total_models > 0 else 0
    
    # 计算平均延迟（仅成功）
    if success_count > 0:
        avg_latency = sum(r["response_time_ms"] for r in successful) / success_count
    else:
        avg_latency = 0
    
    # 按延迟排序成功模型
    successful_sorted = sorted(successful, key=lambda x: x["response_time_ms"])
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 创建报告内容
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
        # 计算延迟分布
        latencies = [r["response_time_ms"] for r in successful]
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # 计算百分位数
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
基于测试结果，建议优先使用以下模型：
"""
    
    # 推荐前20个低延迟模型
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
    
    # 列出所有失败模型
    report += "\n**具体失败模型:**\n"
    for result in failed:
        report += f"- `{result['model']}`: {result['error']}\n"
    
    report += f"""
## 测试配置
- API端点: {API_URL}
- 请求超时: 5秒
- 重试策略: 429/5xx错误重试2次，每次间隔1秒
- 请求间隔: 100ms（避免速率限制）
- 测试消息: "Hi" (1个token)

## 原始数据
完整测试数据已保存到 `openrouter_test_results_{timestamp}.json`
"""
    
    # 保存报告
    report_filename = f"outputs/openrouter_stability_report_{timestamp}.md"
    os.makedirs("outputs", exist_ok=True)
    
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

if __name__ == "__main__":
    main()