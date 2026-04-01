#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集脚本 - 使用 Browser 工具 HTTP API
通过 OpenClaw browser 工具的 evaluate 功能采集数据
"""

import sys
import io
import json
import time
import csv
import requests
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)
GATEWAY_URL = "http://127.0.0.1:18789"
GATEWAY_TOKEN = "f2139bc84b38325ade4ed7a3cc3f5006f36bbddf"

# 业务关键词
BUSINESS_KEYWORDS = [
    'available', 'stock', 'price', 'quote', 'RFQ', 'offer', 'sale', 'sell',
    '现货', '价格', '询价', '报价', '出售', '采购',
    'PN', 'P/N', 'Part Number', '件号', 'engine', 'landing gear', 'APU',
    'CFM56', 'V2500', 'A320', 'B737', 'aircraft', 'aviation', 'parts',
]

# 航空行业关键词（用于筛选相关帖子）
AVIATION_KEYWORDS = [
    'aviation', 'aerospace', 'aircraft', 'airline', 'MRO', 'engine', 'landing gear',
    'APU', 'CFM56', 'V2500', 'A320', 'B737', 'parts', 'component', 'supplier',
    '飞', '航', '发动机', '起落架', '航材',
]

def call_browser(action: str, **kwargs) -> dict:
    """调用 OpenClaw browser 工具"""
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "tool": "browser",
        "action": action,
        **kwargs
    }
    
    try:
        response = requests.post(
            f"{GATEWAY_URL}/rpc/browser",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERR] Browser API 调用失败: {e}")
        return {"error": str(e)}

def scroll_feed():
    """滚动 Feed 页面"""
    result = call_browser("act", kind="evaluate", fn="() => { window.scrollBy(0, 1000); return 'scrolled'; }")
    return result.get("result") == "scrolled"

def extract_posts():
    """提取当前页面的帖子数据"""
    js_code = """
    () => {
        const posts = [];
        const feedItems = document.querySelectorAll('[data-urn]');
        
        feedItems.forEach(item => {
            try {
                const urn = item.getAttribute('data-urn');
                const textContent = item.innerText || '';
                
                // 提取发布者
                const authorEl = item.querySelector('[data-anonymize="person-name"]') || 
                                 item.querySelector('.update-components-actor__name') ||
                                 item.querySelector('span[dir="ltr"]');
                const author = authorEl ? authorEl.innerText.trim() : '';
                
                // 提取职位/公司
                const titleEl = item.querySelector('.update-components-actor__description') ||
                               item.querySelector('[data-anonymize="job-title"]');
                const title = titleEl ? titleEl.innerText.trim() : '';
                
                // 提取时间
                const timeEl = item.querySelector('time') || item.querySelector('.update-components-actor__sub-description');
                const postTime = timeEl ? timeEl.innerText.trim() : '';
                
                // 提取链接
                const linkEl = item.querySelector('a[href*="linkedin.com/posts"]');
                const postUrl = linkEl ? linkEl.href : '';
                
                posts.push({
                    urn: urn,
                    author: author,
                    title: title,
                    time: postTime,
                    content: textContent.substring(0, 500),
                    url: postUrl
                });
            } catch (e) {}
        });
        
        return JSON.stringify(posts);
    }
    """
    
    result = call_browser("act", kind="evaluate", fn=js_code)
    
    if result.get("result"):
        try:
            return json.loads(result["result"])
        except:
            return []
    return []

def is_aviation_related(post: dict) -> bool:
    """判断帖子是否与航空相关"""
    content = (post.get("content", "") + " " + post.get("title", "")).lower()
    
    for keyword in AVIATION_KEYWORDS:
        if keyword.lower() in content:
            return True
    return False

def is_business_post(post: dict) -> bool:
    """判断帖子是否有业务价值"""
    content = post.get("content", "").lower()
    score = 0
    
    for keyword in BUSINESS_KEYWORDS:
        if keyword.lower() in content:
            score += 1
    
    return score >= 2

def save_posts(posts: list, output_file: Path):
    """保存帖子到 CSV 文件"""
    if not posts:
        return
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['采集日期', 'URN', '发布者', '职位/公司', '内容摘要', '帖子时间', 'URL'])
        
        for post in posts:
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                post.get('urn', ''),
                post.get('author', ''),
                post.get('title', ''),
                post.get('content', '')[:200],
                post.get('time', ''),
                post.get('url', '')
            ])
    
    print(f"[OK] 已保存 {len(posts)} 条帖子到 {output_file}")

def main():
    """主函数"""
    print("=" * 70)
    print("LinkedIn 采集 - Browser HTTP API 版")
    print("=" * 70)
    print(f"输出目录: {OUTPUT_DIR}")
    
    all_posts = []
    seen_urns = set()
    scroll_count = 0
    max_scrolls = 50
    
    output_file = OUTPUT_DIR / f"linkedin_collection_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    print(f"\n开始采集 (最多滚动 {max_scrolls} 次)...")
    
    while scroll_count < max_scrolls:
        # 提取当前页面帖子
        posts = extract_posts()
        
        new_count = 0
        for post in posts:
            urn = post.get("urn", "")
            if urn and urn not in seen_urns:
                seen_urns.add(urn)
                
                # 筛选航空相关帖子
                if is_aviation_related(post):
                    all_posts.append(post)
                    new_count += 1
                    
                    # 打印业务价值帖子
                    if is_business_post(post):
                        print(f"  [业务] {post.get('author', 'Unknown')}: {post.get('content', '')[:50]}...")
        
        print(f"[{scroll_count + 1}/{max_scrolls}] 发现 {new_count} 条新帖子，累计 {len(all_posts)} 条航空相关")
        
        # 滚动页面
        if not scroll_feed():
            print("[WARN] 滚动失败")
            break
        
        # 等待加载
        time.sleep(3)
        scroll_count += 1
        
        # 如果连续多次没有新帖子，提前结束
        if new_count == 0 and scroll_count > 10:
            print("[INFO] 无新帖子，提前结束")
            break
    
    # 保存结果
    save_posts(all_posts, output_file)
    
    # 统计
    business_count = sum(1 for p in all_posts if is_business_post(p))
    print(f"\n采集完成:")
    print(f"  - 总计: {len(all_posts)} 条航空相关帖子")
    print(f"  - 业务价值: {business_count} 条")
    print(f"  - 输出: {output_file}")

if __name__ == "__main__":
    main()