#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 快速采集脚本 - 使用已打开的 LinkedIn tab
直接采集真实帖子数据
"""

import csv
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 设置 UTF-8 输出
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce", "ge90", "leap",
    "landing gear", "nlg", "mlg", "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787",
    "part", "component", "inventory", "sale", "lease", "leasing", "available",
    "aviation", "aerospace", "AOG", "FAA", "EASA"
]

def run_cmd(cmd):
    """执行 openclaw 命令"""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace', timeout=60)
        if p.returncode == 0 and p.stdout.strip():
            try:
                return json.loads(p.stdout.strip())
            except:
                return {"raw": p.stdout.strip()}
        return {}
    except Exception as e:
        print(f"命令失败：{e}")
        return {}

def get_linkedin_tabs():
    """获取所有 LinkedIn tab"""
    result = run_cmd(["openclaw", "browser", "tabs", "--json"])
    tabs = result.get("tabs", [])
    linkedin_tabs = []
    for tab in tabs:
        url = tab.get("url", "")
        title = tab.get("title", "")
        if "linkedin.com" in url and "/posts" in url:
            linkedin_tabs.append(tab)
    return linkedin_tabs

def snapshot_tab(target_id):
    """获取 tab 快照"""
    result = run_cmd([
        "openclaw", "browser", "snapshot",
        "--target-id", target_id,
        "--format", "ai",
        "--json",
        "--limit", "600"
    ])
    return result

def extract_posts_from_snapshot(snapshot_text, source_url):
    """从快照文本中提取帖子"""
    posts = []
    
    # 清理 UI 元素
    text = snapshot_text
    # 移除 ref 标记
    text = re.sub(r'\[ref=e\d+\]', '', text)
    text = re.sub(r'\[cursor=pointer\]', '', text)
    
    # 查找帖子内容 - 基于常见模式
    # LinkedIn 帖子通常包含公司名/人名 + 内容 + 时间
    
    lines = text.split('\n')
    current_post = None
    content_buffer = []
    
    for line in lines:
        line = line.strip()
        
        # 检测新帖子开始（通常包含 "Feed post number"）
        if 'Feed post number' in line:
            if current_post and content_buffer:
                current_post['content'] = ' '.join(content_buffer)
                if len(current_post['content']) > 100 and is_aviation_related(current_post['content']):
                    posts.append(current_post)
            
            current_post = {
                'author': 'Unknown',
                'content': '',
                'time': 'Unknown',
                'source_url': source_url
            }
            content_buffer = []
        
        elif current_post is not None:
            # 提取作者名
            if 'View:' in line and 'followers' in line:
                match = re.search(r'View: ([^ ]+)', line)
                if match:
                    current_post['author'] = match.group(1)
            
            # 提取时间
            time_match = re.search(r'(\d+[hdwm] ago)', line, re.IGNORECASE)
            if time_match:
                current_post['time'] = time_match.group(1)
            
            # 累积内容（跳过 UI 元素）
            if len(line) > 50 and not any(x in line for x in ['button', 'link', 'generic', 'img', 'heading', 'region', 'ref=', 'cursor']):
                # 检查是否是实际内容
                if re.search(r'[A-Za-z]', line):
                    content_buffer.append(line)
    
    # 添加最后一个帖子
    if current_post and content_buffer:
        current_post['content'] = ' '.join(content_buffer)
        if len(current_post['content']) > 100 and is_aviation_related(current_post['content']):
            posts.append(current_post)
    
    return posts

def is_aviation_related(content):
    """判断是否与航空相关"""
    content_lower = content.lower()
    return any(kw in content_lower for kw in AVIATION_KEYWORDS)

def classify_business_type(content):
    """分类业务类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["cfm56", "v2500", "ge90", "pw4000", "leap", "engine"]):
        return "航材供应 - 发动机组件/LLP/消耗件"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear"]):
        return "起落架销售/租赁"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental", "ACMI"]):
        return "飞机/发动机租赁"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair", "EASA", "FAA"]):
        return "MRO 服务"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "citation", "jet"]):
        return "飞机整机销售/租赁"
    elif any(kw in content_lower for kw in ["part", "component", "inventory", "rotable"]):
        return "航材销售"
    elif any(kw in content_lower for kw in ["charter", "evacuation", "cargo", "freighter"]):
        return "包机/货运服务"
    elif any(kw in content_lower for kw in ["conference", "event", "ISTAT", "expo"]):
        return "航空展会/会议"
    elif any(kw in content_lower for kw in ["flight", "suspended", "cancelled", "route"]):
        return "航班动态"
    else:
        return "航空相关"

def format_posts(posts, batch_id):
    """格式化帖子为标准格式"""
    formatted = []
    
    for i, post in enumerate(posts, 1):
        content = post.get('content', '')[:2000]
        business_type = classify_business_type(content)
        
        # 提取联系方式
        email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
        contact = email_match.group() if email_match else ""
        
        formatted.append({
            "post_id": f"LI_REAL_{batch_id}_{i:03d}",
            "timestamp": datetime.now().isoformat(),
            "author_name": post.get('author', 'Unknown'),
            "author_url": post.get('source_url', ''),
            "company": post.get('author', ''),
            "position": "",
            "content": content,
            "business_type": business_type,
            "business_value_score": 7 if contact else 5,
            "urgency": "高" if contact else "中",
            "has_contact": bool(contact),
            "contact_info": contact,
            "post_time": post.get('time', 'Unknown'),
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
    """保存帖子到 CSV 和 JSON"""
    if not posts:
        print("⚠️ 没有数据可保存")
        return 0
    
    fieldnames = [
        "post_id", "timestamp", "author_name", "author_url", "company", "position",
        "content", "business_type", "business_value_score", "urgency", "has_contact",
        "contact_info", "post_time", "reactions", "comments", "reposts", "has_image",
        "image_content", "source_url", "batch_id", "collected_at", "content_type", "tags"
    ]
    
    # CSV
    csv_path = OUTPUT_DIR / f"LinkedIn_Business_Posts_真实采集_{batch_id}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    # JSON
    json_path = OUTPUT_DIR / f"LinkedIn_Business_Posts_真实采集_{batch_id}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 保存成功:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  总计：{len(posts)} 条帖子")
    
    return len(posts)

def main():
    print("=" * 60)
    print("LinkedIn 快速采集 - 真实数据")
    print("=" * 60)
    
    # 获取 LinkedIn tabs
    print("\n📑 查找 LinkedIn 页面...")
    tabs = get_linkedin_tabs()
    
    if not tabs:
        print("❌ 未找到 LinkedIn 帖子页面")
        print("请先在浏览器中打开 LinkedIn 公司/个人帖子页面")
        return
    
    print(f"✅ 找到 {len(tabs)} 个 LinkedIn 帖子页面")
    
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    all_posts = []
    
    for i, tab in enumerate(tabs[:10], 1):  # 最多处理 10 个 tab
        target_id = tab.get('targetId')
        url = tab.get('url', '')
        title = tab.get('title', '')
        
        print(f"\n[{i}/{len(tabs)}] {title[:60]}...")
        
        # 获取快照
        snapshot = snapshot_tab(target_id)
        snapshot_text = snapshot.get('snapshot', '')
        
        if not snapshot_text:
            print("  ⚠️ 快照为空")
            continue
        
        # 提取帖子
        raw_posts = extract_posts_from_snapshot(snapshot_text, url)
        
        if raw_posts:
            formatted = format_posts(raw_posts, batch_id)
            all_posts.extend(formatted)
            print(f"  ✅ 采集到 {len(formatted)} 条帖子")
        else:
            print("  ⚠️ 未找到航空业务帖子")
        
        time.sleep(1)
    
    # 去重
    seen = set()
    unique_posts = []
    for post in all_posts:
        key = post['content'][:100]
        if key not in seen:
            seen.add(key)
            unique_posts.append(post)
    
    print(f"\n📊 去重后：{len(unique_posts)} 条")
    
    # 保存
    save_posts(unique_posts, batch_id)
    
    print("\n✅ 采集完成!")

if __name__ == "__main__":
    main()
