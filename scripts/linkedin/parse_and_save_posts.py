#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析并保存已采集的 LinkedIn 帖子数据
"""

import csv
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# StandardAero 帖子数据（从快照解析）
STANDARDAERO_POSTS = [
    {
        "content": "StandardAero has been recognized by Rolls-Royce during its annual FIRST Network Quality Awards ceremony. Our Fleetlands, Hampshire (UK) facility received the Outstanding Partnership Award, recognizing facilities that serve as enabling partners and contribute to the continued success of the FIRST Network. The recognition reflects our team's commitment to developing innovative, cost-effective capabilities that support operators, the FIRST Network, and Rolls-Royce.",
        "post_time": "3d ago",
        "url": "https://www.linkedin.com/company/standardaero/posts/"
    },
    {
        "content": "Big News from VERTICON2026: StandardAero has been selected by Robinson Helicopter Company to support their global fleet of Robinson R66 helicopters powered by the Rolls-Royce RR300. This partnership provides R66 owners and operators with a Robinson Helicopter Company-recommended solution for faster turnarounds and reduced costs.",
        "post_time": "4d ago",
        "url": "https://www.linkedin.com/company/standardaero/posts/"
    },
    {
        "content": "Today at VERTICON2026, we're announcing our Authorized Autopilot installer (AAI) network supporting StableLight, the fully integrated 4-axis autopilot for the Airbus H125 / Eurocopter AS350 series. The expanded network helps broaden installation access and support operators worldwide.",
        "post_time": "5d ago",
        "url": "https://www.linkedin.com/company/standardaero/posts/"
    }
]

# GA Telesis 帖子数据
GATELESIS_POSTS = [
    {
        "content": "You know who to call for your engine's REPAIR & OVERHAUL - GA Telesis! EMAIL gates@gatelesis.com and visit our website: https://ow.ly/n0HY50Ys1jb! #Aviation #Engineering #RepairandOverhaul #AircraftMaintenance #Airplane #Finland",
        "post_time": "43m ago",
        "url": "https://www.linkedin.com/company/gatelesis/posts/",
        "contact": "gates@gatelesis.com"
    },
    {
        "content": "Expertise that travels with you - helping customers across the global aviation community! Visit us: https://www.gatelesis.com/ #GATelesis #WorldWide #Aviation #Teamwork #AviationIndustry #Global #Aerospace",
        "post_time": "7h ago",
        "url": "https://www.linkedin.com/company/gatelesis/posts/"
    },
    {
        "content": "Next stop: Women in Aviation International Conference! Our team is ready to connect with you in Texas! Visit us: https://www.gatelesis.com/ #GATelesis #Tradeshows #Networking #Travel #Aviation #LinkedIn #AviationIndustry #Texas",
        "post_time": "9h ago",
        "url": "https://www.linkedin.com/company/gatelesis/posts/"
    }
]

def classify_category(content):
    """分类业务类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["cfm56", "v2500", "ge90", "pw4000", "leap", "engine", "rolls-royce", "rr300"]):
        return "发动机"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear"]):
        return "起落架"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental", "ACMI"]):
        return "租赁"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair", "certified", "installer"]):
        return "MRO"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "jet", "helicopter", "R66", "H125"]):
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
    elif any(kw in content_lower for kw in ["delivered", "completed", "partnership", "agreement", "selected", "recognized", "award"]):
        return "中"
    else:
        return "低"

def format_posts(posts, company_name):
    """格式化帖子"""
    formatted = []
    
    for i, post in enumerate(posts, 1):
        content = post.get('content', '')
        category = classify_category(content)
        business_value = classify_value(content)
        contact = post.get('contact', '')
        
        # 如果没有联系方式，尝试从内容中提取
        if not contact:
            email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
            if email_match:
                contact = email_match.group()
        
        post_id = f"{company_name.lower().replace(' ', '_')}_{category}_{datetime.now().strftime('%Y%m%d')}_{i:03d}"
        
        formatted.append({
            "post_id": post_id,
            "post_date": datetime.now().strftime("%Y-%m-%d"),
            "author": company_name,
            "author_title": "",
            "company": company_name,
            "content": content,
            "content_summary": content[:200] + "..." if len(content) > 200 else content,
            "source_url": post.get('url', ''),
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "category": category,
            "business_value": business_value,
            "contact_info": contact,
            "verified": "true",
            "notes": ""
        })
    
    return formatted

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
    print("LinkedIn 帖子数据解析与保存")
    print("=" * 70)
    
    master_path = OUTPUT_DIR / "LinkedIn_Business_Posts_Master_Table.csv"
    
    # 格式化帖子
    standardaero_formatted = format_posts(STANDARDAERO_POSTS, "StandardAero")
    gatelesis_formatted = format_posts(GATELESIS_POSTS, "GA Telesis")
    
    all_posts = standardaero_formatted + gatelesis_formatted
    
    print(f"\n[DATA] 数据概览:")
    print(f"   StandardAero: {len(standardaero_formatted)} 条")
    print(f"   GA Telesis: {len(gatelesis_formatted)} 条")
    print(f"   总计：{len(all_posts)} 条")
    
    # 合并到总表
    new_count = merge_to_master(all_posts, master_path)
    
    print(f"\n[OK] 已更新总表：{master_path}")
    print(f"   新增：{new_count} 条")
    
    # 显示分类统计
    categories = {}
    for post in all_posts:
        cat = post['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n[STATS] 分类分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count} 条")
    
    print(f"\n{'='*70}")
    print("[DONE] 数据保存完成!")

if __name__ == "__main__":
    main()
