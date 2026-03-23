#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 核心要素采集脚本 - 简化版
从当前 Browser 快照中提取 5 个核心要素：
1. content - 干净的业务文本
2. author_name - 真实人名
3. company - 公司名称
4. position - 职位信息
5. post_time - 相对时间（如"4h", "1d"）
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 设置 UTF-8 编码
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce",
    "landing gear", "nlg", "mlg",
    "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "b737",
    "part", "component", "inventory", "sale", "lease",
    "aviation", "aerospace", "piston", "turbine", "fleet", "brake", "wheel"
]

def run_command(cmd: list, timeout: int = 30) -> dict:
    """执行 openclaw 命令"""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True, encoding='utf-8', errors='replace')
        if p.returncode == 0 and p.stdout.strip():
            return json.loads(p.stdout)
        return {}
    except Exception as e:
        print(f"命令失败：{e}")
        return {}

def is_aviation_related(text: str) -> bool:
    """判断是否与航空业务相关"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in AVIATION_KEYWORDS)

def extract_posts_from_snapshot(snapshot_text: str) -> list:
    """从快照中提取帖子"""
    posts = []
    
    # 分割文章区域
    articles = re.split(r'article \[ref=\w+\]:', snapshot_text)
    
    for article in articles[1:]:  # 跳过第一个空元素
        try:
            # 提取作者信息
            author_match = re.search(r'link "View: ([^"]+?) \d+(?:st|nd|rd|th)', article)
            if not author_match:
                # 尝试公司帖子
                author_match = re.search(r'link "View: ([^"]+?) \d+', article)
            
            if not author_match:
                continue
            
            author_name = author_match.group(1).strip()
            
            # 跳过 "Skip to" 等 UI 元素
            if author_name.startswith("Skip") or author_name == "Unknown":
                continue
            
            # 提取公司/职位
            company_match = re.search(r'generic \[ref=\w+\]: ([A-Z][^,\n•]+)', article)
            company = company_match.group(1).strip() if company_match else ""
            
            # 提取发帖时间
            post_time_match = re.search(r'text: (\d+[hdm])\s*•', article)
            if not post_time_match:
                post_time_match = re.search(r'(\d+)\s*(minute|hour|day|week)s?\s*ago', article, re.IGNORECASE)
                if post_time_match:
                    num = post_time_match.group(1)
                    unit = post_time_match.group(2)[0].lower()
                    post_time = f"{num}{unit}"
                else:
                    post_time = "Unknown"
            else:
                post_time = post_time_match.group(1)
            
            # 提取内容（所有 text: 行）
            texts = re.findall(r'text: (.+?)(?:\n|$)', article)
            content = ' '.join([t.strip().strip('"') for t in texts if len(t.strip()) > 10])
            
            # 过滤内容太短
            if len(content) < 50:
                continue
            
            # 检查是否与航空相关
            if not is_aviation_related(content):
                continue
            
            # 创建帖子记录
            post = {
                "post_id": f"LI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(posts)+1:03d}",
                "content": content[:2000],
                "author_name": author_name,
                "company": company,
                "position": "",
                "post_time": post_time,
                "source_url": "https://www.linkedin.com/feed/",
                "collected_at": datetime.now().isoformat()
            }
            
            posts.append(post)
            print(f"✅ 采集：{author_name} @ {company} - {post_time} - {len(content)} 字符")
            
        except Exception as e:
            print(f"解析失败：{e}")
            continue
    
    return posts

def save_to_csv(posts: list, filename: str):
    """保存到 CSV"""
    import csv
    
    csv_path = OUTPUT_DIR / filename
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['post_id', 'content', 'author_name', 'company', 'position', 'post_time', 'source_url', 'collected_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    return csv_path

def main():
    print("="*60)
    print("🔍 LinkedIn 核心要素采集 - 简化版")
    print("="*60)
    
    # 获取当前 tab
    tabs_result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = tabs_result.get("tabs", [])
    
    if not tabs:
        print("❌ 没有打开的标签页")
        return
    
    # 找到 LinkedIn Feed 标签
    target_tab = None
    for tab in tabs:
        if "linkedin.com/feed" in tab.get("url", ""):
            target_tab = tab
            break
    
    if not target_tab:
        print("❌ 未找到 LinkedIn Feed 标签页")
        print(f"可用标签页：{[t.get('title', '') for t in tabs]}")
        return
    
    target_id = target_tab.get("targetId")
    print(f"✅ 找到 Feed 页面：{target_id}")
    
    # 获取快照
    print("\n📸 获取快照...")
    snap = run_command([
        "openclaw", "browser", "snapshot",
        "--target-id", target_id,
        "--json",
        "--limit", "500",
        "--refs", "aria"
    ])
    
    snapshot_text = snap.get("snapshot", "")
    
    if not snapshot_text:
        print("❌ 快照为空")
        return
    
    print(f"📊 快照大小：{len(snapshot_text)} 字符\n")
    
    # 提取帖子
    print("🔍 提取帖子...")
    posts = extract_posts_from_snapshot(snapshot_text)
    
    if not posts:
        print("❌ 未找到符合条件的帖子")
        return
    
    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = save_to_csv(posts, f"LinkedIn_Core_Collection_{timestamp}.csv")
    
    print(f"\n✅ 已保存：{csv_file}")
    print(f"📊 共 {len(posts)} 条帖子")
    
    # 显示摘要
    print("\n" + "="*60)
    print("采集摘要:")
    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. {post['author_name']} @ {post['company']} ({post['post_time']})")
        print(f"   {post['content'][:100]}...")
    
    if len(posts) > 5:
        print(f"... 还有 {len(posts)-5} 条")

if __name__ == "__main__":
    main()
