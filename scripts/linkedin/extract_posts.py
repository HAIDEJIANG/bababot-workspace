#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 帖子数据提取器
从 browser snapshot 文本中提取帖子数据
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce", "ge90", "leap",
    "landing gear", "nlg", "mlg", "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787",
    "part", "component", "inventory", "sale", "lease", "leasing", "available",
    "aviation", "aerospace", "AOG", "FAA", "EASA"
]

def extract_posts_from_snapshot(snapshot_text, source_url, company_name):
    """从快照中提取帖子"""
    posts = []
    
    lines = snapshot_text.split('\n')
    current_post = None
    content_buffer = []
    in_post = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # 检测新帖子开始
        if 'Feed post number' in line_stripped:
            # 保存之前的帖子
            if current_post and content_buffer:
                current_post['content'] = ' '.join(content_buffer).strip()
                if len(current_post['content']) > 50:
                    posts.append(current_post)
            
            # 开始新帖子
            current_post = {
                'author_name': company_name,
                'content': '',
                'post_time': 'Unknown',
                'source_url': source_url
            }
            content_buffer = []
            in_post = True
        
        elif in_post:
            # 提取时间信息
            time_match = re.search(r'(\d+\s*[hdwm]\s*ago|\d+\s*[小时天周月]\s*前)', line_stripped, re.IGNORECASE)
            if time_match:
                current_post['post_time'] = time_match.group(1).replace(' ', '')
            
            # 累积内容（跳过 UI 元素）
            if len(line_stripped) > 30:
                # 跳过 UI 元素行
                skip_patterns = ['generic', 'heading', 'region', 'button', 'link', 'img', 'view.*followers', 
                               'See all', 'Show more', 'ref=e', 'cursor=pointer', 'aria-', 'targetId']
                if any(x in line_stripped.lower() for x in skip_patterns):
                    continue
                
                # 跳过空行或纯符号
                if re.match(r'^[\s\W]+$', line_stripped):
                    continue
                
                # 跳过导航/页脚内容
                if any(x in line_stripped.lower() for x in ['about linkedin', 'accessibility', 'help center', 
                                                            'privacy & terms', 'ad choices', 'linkedin corporation']):
                    continue
                
                # 添加有效内容
                content_buffer.append(line_stripped)
    
    # 添加最后一个帖子
    if current_post and content_buffer:
        current_post['content'] = ' '.join(content_buffer).strip()
        if len(current_post['content']) > 50:
            posts.append(current_post)
    
    return posts

def classify_business_type(content):
    """分类业务类型（中文）"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["cfm56", "v2500", "ge90", "pw4000", "leap", "engine", "engineer"]):
        return "航材供应 - 发动机组件/LLP/消耗件"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear", "起落架"]):
        return "起落架销售/租赁"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental", "ACMI", "租赁"]):
        return "飞机/发动机租赁"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair", "EASA", "FAA", "维修"]):
        return "MRO 服务"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "citation", "jet", "飞机"]):
        return "飞机整机销售/租赁"
    elif any(kw in content_lower for kw in ["part", "component", "inventory", "rotable", "航材"]):
        return "航材销售"
    elif any(kw in content_lower for kw in ["charter", "evacuation", "cargo", "freighter", "货运"]):
        return "包机/货运服务"
    elif any(kw in content_lower for kw in ["conference", "event", "ISTAT", "expo", "展会"]):
        return "航空展会/会议"
    elif any(kw in content_lower for kw in ["flight", "suspended", "cancelled", "route", "航班"]):
        return "航班动态"
    else:
        return "航空相关"

def format_posts(posts, batch_id, company_name):
    """格式化帖子为标准格式"""
    formatted = []
    
    for i, post in enumerate(posts, 1):
        content = post.get('content', '')[:2000]
        business_type = classify_business_type(content)
        
        # 提取联系方式
        email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
        contact = email_match.group() if email_match else ""
        
        formatted.append({
            "post_id": f"LI_REAL_{batch_id}_{company_name.replace(' ', '_').replace('&', 'and')}_{i:03d}",
            "timestamp": datetime.now().isoformat(),
            "author_name": post.get('author_name', company_name),
            "author_url": "",
            "company": company_name,
            "position": "",
            "content": content,
            "business_type": business_type,
            "business_value_score": 7 if contact else 5,
            "urgency": "高" if contact else "中",
            "has_contact": bool(contact),
            "contact_info": contact,
            "post_time": post.get('post_time', 'Unknown'),
            "reactions": 0,
            "comments": 0,
            "reposts": 0,
            "has_image": False,
            "image_content": "",
            "source_url": post.get('source_url', ''),
            "batch_id": batch_id,
            "collected_at": datetime.now().isoformat(),
            "content_type": "text",
            "tags": ",".join([kw for kw in AVIATION_KEYWORDS[:10] if kw.lower() in content.lower()])
        })
    
    return formatted

def save_posts(posts, batch_id):
    """保存帖子到 CSV"""
    if not posts:
        print("⚠️ 没有数据可保存")
        return 0
    
    fieldnames = [
        "post_id", "timestamp", "author_name", "author_url", "company", "position",
        "content", "business_type", "business_value_score", "urgency", "has_contact",
        "contact_info", "post_time", "reactions", "comments", "reposts", "has_image",
        "image_content", "source_url", "batch_id", "collected_at", "content_type", "tags"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUTPUT_DIR / f"LinkedIn_Business_Posts_真实采集_{timestamp}.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    print(f"✅ 保存成功：{csv_path.name}")
    print(f"   总计：{len(posts)} 条帖子")
    
    return len(posts)

def main():
    """从标准输入读取 JSON 数据"""
    import sys
    
    # 读取输入
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        print("❌ 没有输入数据")
        return
    
    try:
        data = json.loads(input_data)
    except:
        print("❌ 无效的 JSON 数据")
        return
    
    company_name = data.get('company', 'Unknown')
    source_url = data.get('url', '')
    snapshot = data.get('snapshot', '')
    batch_id = data.get('batch_id', datetime.now().strftime("%Y%m%d_%H%M"))
    
    print(f"\n处理：{company_name}")
    
    # 提取帖子
    raw_posts = extract_posts_from_snapshot(snapshot, source_url, company_name)
    print(f"  原始帖子数：{len(raw_posts)}")
    
    if raw_posts:
        # 格式化
        formatted = format_posts(raw_posts, batch_id, company_name)
        print(f"  格式化后：{len(formatted)} 条")
        
        # 打印预览
        for post in formatted[:2]:
            print(f"\n  帖子预览:")
            print(f"    作者：{post['author_name']}")
            print(f"    时间：{post['post_time']}")
            print(f"    业务类型：{post['business_type']}")
            print(f"    内容：{post['content'][:200]}...")
        
        return formatted
    else:
        print("  ⚠️ 未找到有效帖子")
        return []

if __name__ == "__main__":
    posts = main()
    if posts:
        save_posts(posts, "test")
