#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 核心要素采集 - 直接处理快照数据
从已保存的快照文件中提取 5 个核心要素
"""

import json
import re
import csv
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce",
    "landing gear", "nlg", "mlg",
    "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "b737",
    "part", "component", "inventory", "sale", "lease",
    "aviation", "aerospace", "piston", "turbine", "fleet", "brake", "wheel",
    "rotable", "landing", "gear", "aviation", "ceo", "airline"
]

def is_aviation_related(text: str) -> bool:
    """判断是否与航空业务相关"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in AVIATION_KEYWORDS)

def extract_posts_from_snapshot(snapshot_text: str) -> list:
    """从快照中提取帖子"""
    posts = []
    
    # 分割文章区域 - 使用 article 标记
    articles = re.split(r'article \[ref=\w+\]:', snapshot_text)
    
    print(f"找到 {len(articles)-1} 个文章区域")
    
    for article in articles[1:]:  # 跳过第一个空元素
        try:
            # 提取作者信息 - 查找 "View: Name" 模式
            author_match = re.search(r'link "View: ([^"]+?) (?:\d+(?:st|nd|rd|th)|Premium|followers)', article)
            
            if not author_match:
                continue
            
            author_name = author_match.group(1).strip()
            
            # 跳过 UI 元素
            if author_name.startswith("Skip") or author_name == "Unknown" or len(author_name) < 2:
                continue
            
            # 提取公司/职位信息
            # 查找作者名后面的公司信息
            company_match = re.search(rf'{re.escape(author_name)}.*?generic \[ref=\w+\]: ([A-Z][^,\n•]+?)(?:\n|$)', article)
            if not company_match:
                # 尝试另一种模式
                company_match = re.search(r'generic \[ref=\w+\]: ([A-Z][A-Za-z\s&,]+?(?:Inc|Company|Corp|LLC|Ltd|CEO|Director|Manager))', article)
            
            company = company_match.group(1).strip() if company_match else ""
            
            # 提取发帖时间
            post_time = "Unknown"
            time_match = re.search(r'text: (\d+[hdm])\s*•', article)
            if time_match:
                post_time = time_match.group(1)
            else:
                # 尝试完整时间描述
                full_time = re.search(r'generic \[ref=\w+\]: (\d+ minutes? ago|\d+ hours? ago|\d+ days? ago)', article)
                if full_time:
                    time_str = full_time.group(1)
                    if 'minute' in time_str:
                        post_time = f"{time_str.split()[0]}m"
                    elif 'hour' in time_str:
                        post_time = f"{time_str.split()[0]}h"
                    elif 'day' in time_str:
                        post_time = f"{time_str.split()[0]}d"
            
            # 提取内容（所有 text: 行）
            texts = re.findall(r'text: (.+?)(?:\n|$)', article)
            content_lines = []
            for t in texts:
                cleaned = t.strip().strip('"').strip()
                if len(cleaned) > 10:  # 过滤太短的行
                    content_lines.append(cleaned)
            
            content = ' '.join(content_lines)
            
            # 过滤内容太短
            if len(content) < 50:
                continue
            
            # 检查是否与航空相关
            if not is_aviation_related(content):
                print(f"  ⚠️ 跳过 (非航空): {author_name}")
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
            print(f"✅ {author_name} @ {company[:30] if company else 'N/A'} - {post_time} - {len(content)} 字符")
            
        except Exception as e:
            print(f"解析失败：{e}")
            continue
    
    return posts

def save_to_csv(posts: list, filename: str):
    """保存到 CSV"""
    csv_path = OUTPUT_DIR / filename
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['post_id', 'content', 'author_name', 'company', 'position', 'post_time', 'source_url', 'collected_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    return csv_path

def main():
    print("="*60)
    print("🔍 LinkedIn 核心要素采集 - 快照处理版")
    print("="*60)
    
    # 读取快照文件
    snapshot_file = Path(__file__).parent / "linkedin_snapshot.txt"
    
    if not snapshot_file.exists():
        print(f"❌ 快照文件不存在：{snapshot_file}")
        return
    
    print(f"📄 读取快照：{snapshot_file}")
    snapshot_text = snapshot_file.read_text(encoding='utf-8')
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
        print(f"{i}. {post['author_name']} @ {post['company'][:30] if post['company'] else 'N/A'} ({post['post_time']})")
        print(f"   {post['content'][:100]}...")
    
    if len(posts) > 5:
        print(f"... 还有 {len(posts)-5} 条")

if __name__ == "__main__":
    main()
