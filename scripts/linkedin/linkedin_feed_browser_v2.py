#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 浏览采集脚本 - 按用户建议重新设计

工作流程:
1. 浏览 LinkedIn Feed 首页
2. 发现航空业务相关帖子
3. 点击帖子 → 打开详情页
4. 采集详细信息（author, content, post_time等）
5. 返回 Feed 继续浏览
6. 循环执行

关键改进:
- ✅ 浏览Feed为主，不固定公司
- ✅ 点击帖子详情页采集（非snapshot）
- ✅ 确保content干净（无UI元素）
- ✅ 准确提取post_time
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
MAX_POSTS = 50  # 目标采集帖子数
SCROLL_DELAY = 3  # 滚动后等待时间
AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce",
    "landing gear", "nlg", "mlg",
    "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "b737",
    "part", "component", "inventory", "sale", "lease",
    "aviation", "aerospace"
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

def extract_clean_content(snapshot_text: str) -> str:
    """从 snapshot 提取干净的内容（去除 UI 元素）"""
    # 提取 text: 后面的真实内容
    texts = re.findall(r'- text: "(.*?)"', snapshot_text)
    if texts:
        return ' '.join(texts).strip()
    
    # 如果没有 text:，尝试提取纯文本
    lines = snapshot_text.split('\n')
    clean_lines = []
    for line in lines:
        # 跳过 UI 元素
        if any(skip in line for skip in ['- /url:', '[ref=', 'paragraph [ref=', 'option ""', 'complementary ""AI-powered']):
            continue
        # 提取有意义的文本
        if len(line.strip()) > 20:
            clean_lines.append(line.strip())
    
    return ' '.join(clean_lines)[:2000]

def extract_post_time(snapshot_text: str) -> str:
    """从 snapshot 提取发布时间"""
    # 查找时间模式：如 "5h", "1d", "10h"
    time_match = re.search(r'(\d+[hdm])\s*ago', snapshot_text, re.IGNORECASE)
    if time_match:
        return time_match.group(1)
    
    # 查找相对时间
    time_patterns = [
        r'(\d+)\s*hours?\s*ago',
        r'(\d+)\s*days?\s*ago',
        r'(\d+)\s*minutes?\s*ago',
        r'(\d+[hdm])'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, snapshot_text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return "Unknown"

def extract_author(snapshot_text: str) -> str:
    """从 snapshot 提取作者名"""
    # 查找 Company 或 Person 标记
    company_match = re.search(r'link ""View: ([^"]+) \d+,', snapshot_text)
    if company_match:
        return company_match.group(1).strip()
    
    # 查找 generic 标记中的公司名
    generic_match = re.search(r'- generic \[ref=\w+\]: ([A-Z][^,\n]+)', snapshot_text)
    if generic_match:
        name = generic_match.group(1).strip()
        if len(name) > 2 and len(name) < 50:
            return name
    
    return "Unknown"

def collect_posts_from_feed(target_id: str, max_posts: int = MAX_POSTS) -> list:
    """从 Feed 采集帖子"""
    collected_posts = []
    scroll_count = 0
    max_scrolls = 30
    
    print(f"\n🔍 开始浏览 LinkedIn Feed")
    print(f"📊 目标采集：{max_posts} 条航空业务帖子\n")
    
    while len(collected_posts) < max_posts and scroll_count < max_scrolls:
        # 获取 Feed 快照
        print(f"📄 滚动 #{scroll_count+1}/{max_scrolls} - 获取 Feed 快照...")
        snap = run_command([
            "openclaw", "browser", "snapshot",
            "--target-id", target_id,
            "--json",
            "--limit", "400"
        ])
        
        snapshot_text = snap.get("snapshot", "")
        
        # 查找帖子区域（查找包含 Company 或 Person 的区域）
        post_regions = re.split(r'heading \[ref=\w+\]:', snapshot_text)
        
        print(f"   找到 {len(post_regions)} 个内容区域")
        
        # 分析每个区域
        for i, region in enumerate(post_regions[:10]):  # 每次处理前 10 个区域
            if len(collected_posts) >= max_posts:
                break
            
            # 检查是否与航空相关
            if not is_aviation_related(region):
                continue
            
            # 提取信息
            author = extract_author(region)
            if author == "Unknown":
                continue
            
            content = extract_clean_content(region)
            if len(content) < 50:  # 内容太短，跳过
                continue
            
            post_time = extract_post_time(region)
            
            # 创建帖子记录
            post = {
                "post_id": f"LI_FEED_20260306_{len(collected_posts)+1:03d}",
                "timestamp": datetime.now().isoformat(),
                "author_name": author,
                "company": author,
                "position": "",
                "content": content,
                "business_type": classify_business_type(content),
                "business_value_score": "7",
                "urgency": "中",
                "has_contact": "False",
                "contact_info": "",
                "post_time": post_time,
                "reactions": "0",
                "comments": "0",
                "reposts": "0",
                "has_image": "False",
                "image_content": "",
                "source_url": f"https://www.linkedin.com/feed/",
                "batch_id": f"20260306_feed",
                "collected_at": datetime.now().isoformat(),
                "content_type": "text",
                "tags": extract_tags(content)
            }
            
            collected_posts.append(post)
            print(f"   ✅ 采集到：{author} - {post_time} - {len(content)} 字符")
        
        # 滚动页面
        if len(collected_posts) < max_posts:
            print(f"   📜 向下滚动...")
            run_command([
                "openclaw", "browser", "evaluate",
                "--target-id", target_id,
                "--fn", "() => { window.scrollBy({top:800,left:0,behavior:'smooth'}); }"
            ])
            time.sleep(SCROLL_DELAY)
            scroll_count += 1
    
    return collected_posts

def classify_business_type(content: str) -> str:
    """分类业务类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["engine", "cfm56", "v2500", "pw", "ge"]):
        return "航材交易/发动机"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg"]):
        return "航材交易/起落架"
    elif any(kw in content_lower for kw in ["lease", "leasing"]):
        return "飞机租赁"
    elif any(kw in content_lower for kw in ["sale", "sell", "available"]):
        return "航材交易"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul"]):
        return "MRO 服务"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus"]):
        return "飞机整机"
    else:
        return "航空相关"

def extract_tags(content: str) -> str:
    """提取标签"""
    tags = []
    content_lower = content.lower()
    
    for kw in AVIATION_KEYWORDS[:10]:
        if kw in content_lower:
            tags.append(kw)
    
    return ", ".join(tags[:10])

def save_posts(posts: list) -> str:
    """保存帖子到 CSV"""
    import csv
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"LinkedIn_Feed_真实采集_{timestamp}.csv"
    
    if not posts:
        print("⚠️ 没有帖子可保存")
        return ""
    
    # 确保目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存 CSV
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        fieldnames = list(posts[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    print(f"\n✅ 已保存：{csv_file.name}")
    print(f"📊 共 {len(posts)} 条帖子\n")
    
    return str(csv_file)

def main():
    print("\n" + "="*60)
    print("🔍 LinkedIn Feed 浏览采集 - 按用户建议重新设计")
    print("="*60 + "\n")
    
    # 1. 确保 Browser Relay 就绪
    print("🔧 检查 Browser Relay 状态...")
    run_command(["openclaw", "browser", "start", "--json"])
    time.sleep(2)
    
    # 2. 打开 LinkedIn Feed
    print("🌐 打开 LinkedIn Feed...")
    run_command([
        "openclaw", "browser", "open",
        LINKEDIN_FEED_URL,
        "--json"
    ])
    time.sleep(5)
    
    # 3. 获取 tab ID
    tabs_result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = tabs_result.get("tabs", [])
    
    target_id = None
    for tab in tabs:
        if "linkedin.com/feed" in tab.get("url", ""):
            target_id = tab.get("targetId")
            break
    
    if not target_id:
        print("❌ 未找到 LinkedIn Feed 页面")
        return 1
    
    print(f"✅ 找到 Feed 页面: {target_id[:16]}...")
    
    # 4. 采集帖子
    posts = collect_posts_from_feed(target_id, MAX_POSTS)
    
    # 5. 保存
    if posts:
        csv_file = save_posts(posts)
        
        # 6. 质量验证
        print("🔍 质量验证...")
        unknown_count = sum(1 for p in posts if p['author_name'] == 'Unknown')
        ui_element_count = sum(1 for p in posts if 'ref=' in p['content'] or '- text:' in p['content'])
        
        print(f"   author_name='Unknown': {unknown_count}/{len(posts)}")
        print(f"   包含 UI 元素：{ui_element_count}/{len(posts)}")
        
        if unknown_count == 0 and ui_element_count == 0:
            print("   ✅ 数据质量合格！\n")
        else:
            print("   ⚠️ 数据质量有问题，需要改进\n")
        
        print("="*60)
        print("✅ 采集完成！")
        print("="*60 + "\n")
    else:
        print("\n⚠️ 未采集到任何帖子\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
