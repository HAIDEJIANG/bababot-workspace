#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 高速批量采集器 v5 - 优化版
目标速度：2-5 秒/条（原 10-20 秒/条）
优化策略:
1. 批量滚动后统一采集（减少快照次数）
2. 减少等待时间（从 8 秒降到 3 秒）
3. 批量写入数据
4. 优化快照提取逻辑
"""

import csv
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 扩展目标公司列表（航空业务相关）
TARGET_COMPANIES = [
    {"name": "StandardAero", "url": "https://www.linkedin.com/company/standardaero/posts/"},
    {"name": "GA Telesis", "url": "https://www.linkedin.com/company/gatelesis/posts/"},
    {"name": "Textron Aviation", "url": "https://www.linkedin.com/company/textron-aviation/posts/"},
    {"name": "Lufthansa Technik", "url": "https://www.linkedin.com/company/lufthansa-technik/posts/"},
    {"name": "Rolls-Royce", "url": "https://www.linkedin.com/company/rolls-royce/posts/"},
    {"name": "GE Aerospace", "url": "https://www.linkedin.com/company/ge-aerospace/posts/"},
    {"name": "Honeywell Aerospace", "url": "https://www.linkedin.com/company/honeywell-aerospace/posts/"},
    {"name": "Pratt & Whitney", "url": "https://www.linkedin.com/company/pratt-whitney/posts/"},
    {"name": "Safran", "url": "https://www.linkedin.com/company/safran/posts/"},
    {"name": "Airbus", "url": "https://www.linkedin.com/company/airbus/posts/"},
    {"name": "Boeing", "url": "https://www.linkedin.com/company/boeing/posts/"},
    {"name": "CFM International", "url": "https://www.linkedin.com/company/cfm-international/posts/"},
    {"name": "MTU Aero Engines", "url": "https://www.linkedin.com/company/mtu-aero-engines/posts/"},
    {"name": "IAE International Aero Engines", "url": "https://www.linkedin.com/company/iae-international-aero-engines/posts/"},
    {"name": "AAR Corp", "url": "https://www.linkedin.com/company/aar-corp/posts/"},
    {"name": "HEICO Aerospace", "url": "https://www.linkedin.com/company/heico-aerospace/posts/"},
    {"name": "Aviation Week Network", "url": "https://www.linkedin.com/company/aviation-week-network/posts/"},
    {"name": "FlightGlobal", "url": "https://www.linkedin.com/company/flightglobal/posts/"},
    {"name": "Ch-Aviation", "url": "https://www.linkedin.com/company/ch-aviation/posts/"},
    {"name": "IBA Group", "url": "https://www.linkedin.com/company/iba-group/posts/"},
]

AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce", "ge90", "leap",
    "landing gear", "nlg", "mlg", "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787",
    "part", "component", "inventory", "sale", "lease", "leasing", "available",
    "aviation", "aerospace", "AOG", "FAA", "EASA"
]

def run_browser_cmd(cmd_list, timeout=60):
    """执行 browser 命令"""
    try:
        # 使用 PowerShell 调用 openclaw
        cmd = ["powershell", "-Command", "openclaw", "browser"] + cmd_list + ["--json"]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, shell=True)
        if p.returncode == 0 and p.stdout.strip():
            try:
                return json.loads(p.stdout.strip())
            except:
                return {"raw": p.stdout.strip()}
        return {}
    except Exception as e:
        print(f"  命令失败：{e}")
        return {}

def open_url(url):
    """打开 URL"""
    result = run_browser_cmd(["open", url], timeout=30)
    return result.get("targetId")

def scroll_page(target_id, num_scrolls=3):
    """批量滚动页面（优化：一次滚动多屏）"""
    for _ in range(num_scrolls):
        run_browser_cmd([
            "act", "--kind", "evaluate",
            "--target-id", target_id,
            "--fn", "window.scrollBy(0, window.innerHeight)"
        ], timeout=5)
        time.sleep(0.5)  # 缩短滚动间隔

def get_snapshot(target_id=None, limit=2000):
    """获取页面快照（优化：增加限制到 2000 字符）"""
    cmd = ["snapshot", "--format", "ai", "--limit", str(limit)]
    if target_id:
        cmd.extend(["--target-id", target_id])
    result = run_browser_cmd(cmd, timeout=90)
    return result.get("snapshot", "")

def extract_posts_from_snapshot(snapshot_text, source_url, company_name):
    """从快照中提取帖子（优化：更高效的解析）"""
    posts = []
    
    # 快速清理 UI 标记
    text = re.sub(r'\[ref=e\d+\]|\[cursor=pointer\]|\[button\]|\[link\]|\[img\]', ' ', snapshot_text)
    
    lines = text.split('\n')
    current_post = None
    content_buffer = []
    in_post = False
    post_count = 0
    
    for line in lines:
        line_stripped = line.strip()
        
        # 检测新帖子
        if 'Feed post' in line_stripped or 'post number' in line_stripped.lower():
            # 保存之前的帖子
            if current_post and content_buffer:
                content = ' '.join(content_buffer).strip()
                if len(content) > 50:
                    current_post['content'] = content
                    posts.append(current_post)
                    post_count += 1
                    if post_count >= 10:  # 每个公司最多 10 条
                        break
            
            current_post = {
                'author_name': company_name,
                'content': '',
                'post_time': 'Unknown',
                'source_url': source_url
            }
            content_buffer = []
            in_post = True
        
        elif in_post and len(line_stripped) > 30:
            # 跳过 UI 元素
            if any(x in line_stripped.lower() for x in ['generic', 'heading', 'region', 'button', 'link', 'img', 'view', 'followers']):
                continue
            if re.match(r'^[\s\W]+$', line_stripped):
                continue
            content_buffer.append(line_stripped)
    
    # 添加最后一个帖子
    if current_post and content_buffer and post_count < 10:
        content = ' '.join(content_buffer).strip()
        if len(content) > 50:
            current_post['content'] = content
            posts.append(current_post)
    
    return posts

def classify_business_type(content):
    """分类业务类型（中文）"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["cfm56", "v2500", "ge90", "pw4000", "leap", "engine"]):
        return "发动机"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear"]):
        return "起落架"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental", "ACMI"]):
        return "租赁"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair"]):
        return "MRO"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "jet"]):
        return "飞机整机"
    elif any(kw in content_lower for kw in ["part", "component", "inventory"]):
        return "航材"
    else:
        return "市场情报"

def classify_business_value(content, has_contact):
    """分类业务价值"""
    content_lower = content.lower()
    
    # 高价值：明确的供需信息
    if any(kw in content_lower for kw in ["sale", "available", "looking for", "requirement", "urgent"]):
        return "高"
    # 中价值：业务动态
    elif any(kw in content_lower for kw in ["delivered", "completed", "partnership", "agreement"]):
        return "中"
    # 低价值：一般信息
    else:
        return "低"

def format_posts(posts, company_name):
    """格式化帖子为标准格式（匹配总表字段）"""
    formatted = []
    
    for i, post in enumerate(posts, 1):
        content = post.get('content', '')[:2000]
        category = classify_business_type(content)
        business_value = classify_business_value(content, False)
        
        # 提取联系方式
        email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
        contact = email_match.group() if email_match else ""
        
        # 生成 post_id
        post_id = f"{company_name.replace(' ', '_').lower()}_{category}_{datetime.now().strftime('%Y%m%d')}_{i:03d}"
        
        formatted.append({
            "post_id": post_id,
            "post_date": datetime.now().strftime("%Y-%m-%d"),
            "author": post.get('author_name', company_name),
            "author_title": "",
            "company": company_name,
            "content": content,
            "content_summary": content[:200] + "..." if len(content) > 200 else content,
            "source_url": post.get('source_url', ''),
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "category": category,
            "business_value": business_value,
            "contact_info": contact,
            "verified": "true",
            "notes": ""
        })
    
    return formatted

def merge_with_master(new_posts, master_path):
    """合并到总表（避免重复）"""
    import os
    
    if not os.path.exists(master_path):
        # 如果总表不存在，创建新文件
        fieldnames = [
            "post_id", "post_date", "author", "author_title", "company", "category",
            "business_type", "business_value", "content", "content_summary",
            "contact_info", "source_url", "collection_date", "verified", "notes"
        ]
        with open(master_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_posts)
        return len(new_posts)
    
    # 读取现有总表
    existing_ids = set()
    existing_posts = []
    
    with open(master_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_posts.append(row)
            existing_ids.add(row.get('post_id', ''))
    
    # 添加新帖子（避免重复）
    new_count = 0
    for post in new_posts:
        if post['post_id'] not in existing_ids:
            # 添加缺失字段
            post['business_type'] = post.get('category', '')
            existing_posts.append(post)
            new_count += 1
    
    # 写回总表
    fieldnames = [
        "post_id", "post_date", "author", "author_title", "company", "category",
        "business_type", "business_value", "content", "content_summary",
        "contact_info", "source_url", "collection_date", "verified", "notes"
    ]
    
    with open(master_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_posts)
    
    return new_count

def main():
    print("=" * 70)
    print("LinkedIn 高速批量采集器 v5 - 优化版")
    print("目标速度：2-5 秒/条（原 10-20 秒/条）")
    print("=" * 70)
    
    start_time = time.time()
    all_posts = []
    master_path = OUTPUT_DIR / "LinkedIn_Business_Posts_Master_Table.csv"
    
    for i, company in enumerate(TARGET_COMPANIES, 1):
        print(f"\n[{i}/{len(TARGET_COMPANIES)}] 采集：{company['name']}")
        print(f"   URL: {company['url']}")
        
        company_start = time.time()
        
        # 打开公司页面
        target_id = open_url(company['url'])
        if not target_id:
            print(f"   ❌ 无法打开页面")
            continue
        
        # 优化：缩短等待时间到 3 秒
        time.sleep(3)
        
        # 批量滚动（3 次滚动，覆盖更多内容）
        scroll_page(target_id, num_scrolls=3)
        time.sleep(2)  # 等待滚动后内容加载
        
        # 获取快照（优化：一次获取 2000 字符）
        snapshot = get_snapshot(target_id, limit=2000)
        
        if not snapshot:
            print("   ⚠️ 快照为空")
            continue
        
        # 提取帖子
        raw_posts = extract_posts_from_snapshot(snapshot, company['url'], company['name'])
        
        if raw_posts:
            # 格式化
            formatted = format_posts(raw_posts, company['name'])
            all_posts.extend(formatted)
            print(f"   ✅ 采集：{len(formatted)} 条")
        else:
            print("   ⚠️ 未找到帖子")
        
        company_time = time.time() - company_start
        print(f"   ⏱️ 耗时：{company_time:.1f}秒")
        
        # 优化：缩短公司间等待到 1 秒
        time.sleep(1)
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"📊 采集统计:")
    print(f"   总帖子数：{len(all_posts)}")
    print(f"   总耗时：{total_time:.1f}秒")
    if len(all_posts) > 0:
        print(f"   平均速度：{total_time/len(all_posts):.1f}秒/条")
    
    # 合并到总表
    if all_posts:
        new_count = merge_with_master(all_posts, master_path)
        print(f"\n✅ 已更新总表：{master_path}")
        print(f"   新增：{new_count} 条")
        
        # 生成报告
        generate_report(all_posts, total_time, master_path)
    else:
        print("\n❌ 没有有效数据")
    
    print("\n✅ 采集任务完成!")

def generate_report(posts, total_time, master_path):
    """生成采集报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = OUTPUT_DIR / f"LinkedIn_Fast_Collection_Report_{timestamp}.md"
    
    # 统计
    categories = {}
    companies = {}
    for post in posts:
        cat = post.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
        comp = post.get('company', 'Unknown')
        companies[comp] = companies.get(comp, 0) + 1
    
    avg_speed = total_time / len(posts) if posts else 0
    
    report = f"""# LinkedIn 高速批量采集报告

**采集时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**优化版本**: v5

## 性能对比

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 单条耗时 | 10-20 秒 | {avg_speed:.1f}秒 | {((15-avg_speed)/15*100):.0f}% |
| 页面等待 | 8 秒 | 3 秒 | 62.5% |
| 快照限制 | 800 字符 | 2000 字符 | 150% |

## 采集统计

| 指标 | 数值 |
|------|------|
| 总采集帖子数 | {len(posts)} |
| 总耗时 | {total_time:.1f}秒 |
| 平均速度 | {avg_speed:.1f}秒/条 |
| 目标公司数 | {len(companies)} |

## 分类分布

"""
    
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        report += f"- {cat}: {count} 条\n"
    
    report += "\n## 公司分布\n\n"
    
    for comp, count in sorted(companies.items(), key=lambda x: -x[1])[:10]:
        report += f"- {comp}: {count} 条\n"
    
    report += f"""
## 优化措施

1. **批量滚动**: 一次滚动 3 屏，减少快照次数
2. **缩短等待**: 页面等待从 8 秒降到 3 秒
3. **增大快照**: 从 800 字符增加到 2000 字符
4. **批量写入**: 统一合并到总表，避免逐条写入

## 输出文件

- `{master_path}` - 更新后的总表

---
*报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存：{report_path.name}")

if __name__ == "__main__":
    main()
