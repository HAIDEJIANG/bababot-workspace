#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 批量采集器 v6 - 使用 browser 工具
目标：采集 50-100 条真实航空业务帖子
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 目标公司列表
TARGET_COMPANIES = [
    {"name": "StandardAero", "url": "https://www.linkedin.com/company/standardaero/posts/"},
    {"name": "GA Telesis", "url": "https://www.linkedin.com/company/gatelesis/posts/"},
    {"name": "Lufthansa Technik", "url": "https://www.linkedin.com/company/lufthansa-technik/posts/"},
    {"name": "Rolls-Royce", "url": "https://www.linkedin.com/company/rolls-royce/posts/"},
    {"name": "GE Aerospace", "url": "https://www.linkedin.com/company/ge-aerospace/posts/"},
    {"name": "Pratt & Whitney", "url": "https://www.linkedin.com/company/pratt-whitney/posts/"},
    {"name": "Safran", "url": "https://www.linkedin.com/company/safran/posts/"},
    {"name": "Airbus", "url": "https://www.linkedin.com/company/airbus/posts/"},
    {"name": "Boeing", "url": "https://www.linkedin.com/company/boeing/posts/"},
    {"name": "CFM International", "url": "https://www.linkedin.com/company/cfm-international/posts/"},
    {"name": "MTU Aero Engines", "url": "https://www.linkedin.com/company/mtu-aero-engines/posts/"},
    {"name": "AAR Corp", "url": "https://www.linkedin.com/company/aar-corp/posts/"},
    {"name": "HEICO Aerospace", "url": "https://www.linkedin.com/company/heico-aerospace/posts/"},
    {"name": "Textron Aviation", "url": "https://www.linkedin.com/company/textron-aviation/posts/"},
    {"name": "Honeywell Aerospace", "url": "https://www.linkedin.com/company/honeywell-aerospace/posts/"},
]

def classify_category(content):
    """分类业务类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["cfm56", "v2500", "ge90", "pw4000", "leap", "engine", "rolls-royce"]):
        return "发动机"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear"]):
        return "起落架"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental", "ACMI"]):
        return "租赁"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair", "certified"]):
        return "MRO"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "jet", "helicopter"]):
        return "飞机整机"
    elif any(kw in content_lower for kw in ["part", "component", "inventory", "rotable", "component"]):
        return "航材"
    else:
        return "市场情报"

def classify_value(content):
    """分类业务价值"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["sale", "available", "looking for", "requirement", "urgent", "offer"]):
        return "高"
    elif any(kw in content_lower for kw in ["delivered", "completed", "partnership", "agreement", "selected", "recognized"]):
        return "中"
    else:
        return "低"

def extract_contact(content):
    """提取联系方式"""
    email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
    if email_match:
        return email_match.group()
    return ""

def parse_posts_from_snapshot(snapshot_text, company_name, company_url):
    """从快照中解析帖子"""
    posts = []
    
    # 查找所有 Feed post
    post_pattern = r'Feed post number (\d+)'
    post_matches = list(re.finditer(post_pattern, snapshot_text))
    
    for i, match in enumerate(post_matches[:5]):  # 每个公司最多 5 条
        start_idx = match.end()
        end_idx = post_matches[i+1].start() if i+1 < len(post_matches) else len(snapshot_text)
        post_text = snapshot_text[start_idx:end_idx]
        
        # 提取时间
        time_match = re.search(r'(\d+\s*[hdwm]\s*ago|\d+\s*days?\s*ago|\d+\s*weeks?\s*ago)', post_text, re.IGNORECASE)
        post_time = time_match.group(0) if time_match else "Unknown"
        
        # 提取内容（跳过 UI 元素）
        content_lines = []
        for line in post_text.split('\n'):
            line = line.strip()
            if len(line) > 30:
                # 跳过 UI 元素
                if any(x in line.lower() for x in ['generic', 'button', 'link', 'img', 'heading', 'region', 'followers', 'see more', 'activate']):
                    continue
                # 跳过纯符号
                if re.match(r'^[\s\W]+$', line):
                    continue
                content_lines.append(line)
        
        content = ' '.join(content_lines).strip()
        
        if len(content) > 50:  # 内容长度要求
            # 清理 URL 标记
            content = re.sub(r'\[ref=e\d+\]|\[cursor=pointer\]|\[button\]|\[link\]|\[img\]', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            category = classify_category(content)
            business_value = classify_value(content)
            contact = extract_contact(content)
            
            post_id = f"{company_name.replace(' ', '_').lower()}_{category}_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
            
            posts.append({
                "post_id": post_id,
                "post_date": datetime.now().strftime("%Y-%m-%d"),
                "author": company_name,
                "author_title": "",
                "company": company_name,
                "content": content[:2000],
                "content_summary": content[:200] + "..." if len(content) > 200 else content,
                "source_url": company_url,
                "collection_date": datetime.now().strftime("%Y-%m-%d"),
                "category": category,
                "business_value": business_value,
                "contact_info": contact,
                "verified": "true",
                "notes": ""
            })
    
    return posts

def merge_to_master(new_posts, master_path):
    """合并到总表"""
    import os
    
    fieldnames = [
        "post_id", "post_date", "author", "author_title", "company", "category",
        "business_type", "business_value", "content", "content_summary",
        "contact_info", "source_url", "collection_date", "verified", "notes"
    ]
    
    if not os.path.exists(master_path):
        with open(master_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_posts)
        return len(new_posts)
    
    # 读取现有数据
    existing_ids = set()
    existing_posts = []
    
    with open(master_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_posts.append(row)
            existing_ids.add(row.get('post_id', ''))
    
    # 添加新帖子
    new_count = 0
    for post in new_posts:
        if post['post_id'] not in existing_ids:
            post['business_type'] = post.get('category', '')
            existing_posts.append(post)
            new_count += 1
    
    # 写回
    with open(master_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_posts)
    
    return new_count

def main():
    print("=" * 70)
    print("LinkedIn 批量采集器 v6")
    print("目标：50-100 条真实航空业务帖子")
    print("=" * 70)
    
    master_path = OUTPUT_DIR / "LinkedIn_Business_Posts_Master_Table.csv"
    all_posts = []
    
    print(f"\n📋 目标公司：{len(TARGET_COMPANIES)} 家")
    print(f"📁 总表路径：{master_path}")
    print("\n请手动访问以下公司页面并粘贴快照内容...")
    print("或者使用 browser 工具批量采集\n")
    
    for i, company in enumerate(TARGET_COMPANIES, 1):
        print(f"\n[{i}/{len(TARGET_COMPANIES)}] {company['name']}")
        print(f"   URL: {company['url']}")
    
    print(f"\n{'='*70}")
    print("✅ 配置完成！")
    print(f"\n下一步:")
    print("1. 使用 browser 工具打开每个公司页面")
    print("2. 获取快照 (snapshot)")
    print("3. 调用 parse_posts_from_snapshot 解析数据")
    print("4. 合并到总表")

if __name__ == "__main__":
    main()
