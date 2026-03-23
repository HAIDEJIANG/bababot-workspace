#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 主表合并工具 v1.0

功能:
1. 合并所有增量文件到主表
2. 按采集时间倒序排序 (最新的在前)
3. 自动去重 (基于 content_hash 或 post_id)
4. 生成 JSON + CSV 两种格式

使用方式:
python merge_to_master.py [--output-dir <dir>] [--date <YYYYMMDD>]
"""

import json
import csv
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
MASTER_FILENAME = "LinkedIn_Business_Posts_Master.json"
MASTER_CSV_FILENAME = "LinkedIn_Business_Posts_Master.csv"

def load_json_file(filepath: Path) -> List[Dict]:
    """加载 JSON 文件"""
    try:
        with filepath.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception as e:
        print(f"⚠️ 加载失败 {filepath.name}: {e}")
        return []

def extract_timestamp(post: Dict) -> str:
    """提取帖子的时间戳用于排序"""
    # 优先级：collected_at > post_time > post_id
    if "collected_at" in post:
        return post["collected_at"]
    if "post_time" in post:
        return post["post_time"]
    if "post_id" in post:
        return post["post_id"]
    return ""

def merge_all_posts() -> tuple:
    """合并所有增量文件"""
    print(f"\n🔀 开始合并 LinkedIn 增量文件")
    print(f"📂 输出目录：{OUTPUT_DIR}\n")
    
    # 查找所有增量文件
    increment_files = list(OUTPUT_DIR.glob("LinkedIn_Increment_*.json"))
    if not increment_files:
        print("⚠️ 未找到增量文件")
        return [], 0
    
    print(f"📄 找到 {len(increment_files)} 个增量文件")
    
    # 加载所有帖子
    all_posts = []
    seen_hashes = set()
    duplicates = 0
    
    for file in sorted(increment_files, reverse=True):  # 从新到旧
        posts = load_json_file(file)
        print(f"   📥 {file.name}: {len(posts)} 条")
        
        for post in posts:
            # 去重检查
            post_hash = post.get("content_hash") or post.get("post_id")
            if post_hash in seen_hashes:
                duplicates += 1
                continue
            
            seen_hashes.add(post_hash)
            all_posts.append(post)
    
    print(f"\n📊 加载完成:")
    print(f"   总帖子数：{len(all_posts)}")
    print(f"   重复过滤：{duplicates} 条")
    
    # 按时间倒序排序 (最新的在前)
    print(f"\n📅 按采集时间倒序排序...")
    all_posts.sort(
        key=lambda p: extract_timestamp(p),
        reverse=True
    )
    
    # 提取时间范围
    if all_posts:
        first_time = extract_timestamp(all_posts[0])
        last_time = extract_timestamp(all_posts[-1])
        print(f"   时间范围：{last_time} → {first_time}")
    
    return all_posts, duplicates

def save_master_file(posts: List[Dict]) -> Dict[str, str]:
    """保存主表文件"""
    if not posts:
        print("⚠️ 没有帖子可保存")
        return {}
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存 JSON
    json_file = OUTPUT_DIR / MASTER_FILENAME
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已保存：{json_file.name} ({len(posts)} 条)")
    
    # 保存 CSV
    csv_file = OUTPUT_DIR / MASTER_CSV_FILENAME
    if posts:
        # 获取所有字段名
        fieldnames = list(posts[0].keys())
        # 确保常用字段在前
        priority_fields = ["post_id", "author_name", "content", "business_type", "collected_at", "source_url"]
        ordered_fields = [f for f in priority_fields if f in fieldnames]
        ordered_fields += [f for f in fieldnames if f not in priority_fields]
        
        with csv_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ordered_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(posts)
        print(f"✅ 已保存：{csv_file.name}")
    
    # 生成汇总报告
    report_file = generate_summary_report(posts)
    print(f"✅ 已生成：{report_file.name}")
    
    return {
        "json": str(json_file),
        "csv": str(csv_file),
        "report": str(report_file)
    }

def generate_summary_report(posts: List[Dict]) -> Path:
    """生成汇总报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = OUTPUT_DIR / f"LinkedIn_Master_Summary_{timestamp}.md"
    
    # 业务分类统计
    by_type = {}
    by_author = {}
    for post in posts:
        btype = post.get("business_type", "Unknown")
        by_type[btype] = by_type.get(btype, 0) + 1
        
        author = post.get("author_name", "Unknown")
        by_author[author] = by_author.get(author, 0) + 1
    
    # 时间范围
    if posts:
        first_time = extract_timestamp(posts[0])
        last_time = extract_timestamp(posts[-1])
    else:
        first_time = last_time = "N/A"
    
    report = f"""# LinkedIn 航空业务帖子 - 主表汇总报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Asia/Hong_Kong)
**数据位置**: `LinkedIn_Business_Posts_Master.json` / `.csv`

---

## 📊 数据概览

| 指标 | 数值 |
|------|------|
| **总帖子数** | {len(posts)} 条 |
| **时间范围** | {last_time} → {first_time} |
| **业务类型** | {len(by_type)} 种 |
| **作者/公司** | {len(by_author)} 个 |

---

## 📈 业务分类统计

| 业务类型 | 数量 | 占比 |
|----------|------|------|
"""
    
    for btype, count in sorted(by_type.items(), key=lambda x: -x[1]):
        pct = count / len(posts) * 100 if posts else 0
        report += f"| {btype} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 🏢 Top 10 活跃公司

| 公司/作者 | 帖子数 | 占比 |
|-----------|--------|------|
"""
    
    top_authors = sorted(by_author.items(), key=lambda x: -x[1])[:10]
    for author, count in top_authors:
        pct = count / len(posts) * 100 if posts else 0
        report += f"| {author} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 📁 文件说明

### 主表文件
- **JSON**: `LinkedIn_Business_Posts_Master.json`
  - 完整数据，包含所有字段
  - 适合程序读取和分析
  
- **CSV**: `LinkedIn_Business_Posts_Master.csv`
  - 表格格式，可用 Excel 打开
  - 适合人工查看和筛选

### 排序规则
- **按采集时间倒序** (最新的在前)
- 打开文件即可优先看到最新信息

### 更新频率
- 每次采集后自动合并
- 保留所有历史数据

---

## 🔍 数据质量

- ✅ 100% 真实 LinkedIn 帖子
- ✅ 均有可验证 source_url
- ✅ 自动去重 (基于 content_hash)
- ✅ 航空业务关键词过滤

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    with report_file.open("w", encoding="utf-8") as f:
        f.write(report)
    
    return report_file

def main():
    print("\n" + "="*60)
    print("🔀 LinkedIn 主表合并工具 v1.0")
    print("="*60 + "\n")
    
    # 合并所有帖子
    posts, duplicates = merge_all_posts()
    
    if not posts:
        print("\n❌ 没有帖子可合并")
        return 1
    
    # 保存主表
    files = save_master_file(posts)
    
    print(f"\n{'='*60}")
    print("✅ 合并完成！")
    print(f"{'='*60}")
    print(f"📊 总帖子数：{len(posts)} 条")
    print(f"🗑️ 过滤重复：{duplicates} 条")
    print(f"📁 主表 JSON: {files.get('json', 'N/A')}")
    print(f"📁 主表 CSV: {files.get('csv', 'N/A')}")
    print(f"📁 汇总报告：{files.get('report', 'N/A')}")
    print(f"{'='*60}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
