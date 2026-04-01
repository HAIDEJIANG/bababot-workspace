#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 采集 - Gateway HTTP API 版
通过 OpenClaw Gateway (port 18789) 调用浏览器工具
持续采集 60 分钟航材相关帖子
"""

import sys
import io
import time
import json
import re
import requests
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 配置 ====================

GATEWAY_URL = "http://127.0.0.1:18789"
TARGET_ID = "ADF0A2830B02D1A0B58A55ECE358A323"
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

DURATION_MINUTES = 60
SCROLL_PAUSE = 5  # 秒

# PN 号正则
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',
    r'\b[A-Z]{1,2}-[0-9]{4,}-[0-9]{2,}\b',
    r'\bHG[0-9]{4}[A-Z]{2}\b',
    r'\b[0-9]{3,5}[A-Z]?-[0-9]{3,4}-[0-9]{2,3}\b',
]

# 业务关键词
BUSINESS_KEYWORDS = [
    'available', 'stock', 'price', 'quote', 'RFQ', 'offer', 'sale', 'buy', 'urgent',
    '现货', '价格', '询价', '报价', '出售', '采购', '急购',
    'PN', 'P/N', 'Part Number', '件号', 'S/N', 'serial',
    'CFM56', 'V2500', 'A320', 'B737', 'LEAP', 'PW', 'GE', 'Trent', 'RR',
    'engine', 'landing gear', 'APU', 'rotable', 'surplus', 'spare', 'parts',
    'aircraft', 'helicopter', 'component', 'module', 'blade', 'fuel',
    'starter', 'generator', 'pump', 'valve', 'actuator', 'sensor', 'probe',
    'ADIRU', 'MCP', 'TCAS', 'display', 'avionics', 'radio', 'transponder',
    'ferry', 'delivery', 'leased', 'lease', 'sold', 'purchase',
]

# ==================== 工具函数 ====================

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def extract_pn(text: str) -> list:
    pns = []
    for pattern in PN_PATTERNS:
        pns.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(pns))

def has_business_intent(text: str) -> bool:
    text_lower = text.lower()
    for keyword in BUSINESS_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

def gateway_act(kind, **params):
    """通过 Gateway 发送浏览器操作"""
    payload = {
        "action": "act",
        "targetId": TARGET_ID,
        "request": {"kind": kind, **params}
    }
    
    try:
        r = requests.post(f"{GATEWAY_URL}/browser", json=payload, timeout=30)
        data = r.json()
        if data.get('ok'):
            return data.get('result')
        else:
            log(f"Gateway error: {data.get('error', 'unknown')}")
            return None
    except Exception as e:
        log(f"Request error: {e}")
        return None

def scroll_page():
    """滚动页面"""
    gateway_act("evaluate", fn="window.scrollBy(0, 800)")

def get_posts():
    """提取页面帖子"""
    js_code = """
    (() => {
        let posts = []; let seen = new Set();
        document.querySelectorAll('div, article, section, span, p').forEach(el => {
            let text = (el.innerText || '').trim();
            let key = text.slice(0, 100);
            if (seen.has(key) || text.length < 50 || text.length > 3000) return;
            seen.add(key);
            let keywords = ['CFM56', 'V2500', 'A320', 'B737', 'LEAP', 'engine', 'landing', 'APU', 
                          'stock', 'price', 'available', 'PN', 'P/N', '件号', '现货', '出售',
                          'starter', 'generator', 'pump', 'valve', 'actuator', 'sensor',
                          'ADIRU', 'MCP', 'TCAS', 'surplus', 'rotable', 'aircraft', 'ferry',
                          'delivery', 'lease', 'sold', 'purchase', 'engine', 'blade', 'module'];
            for (let kw of keywords) {
                if (text.toLowerCase().includes(kw.toLowerCase())) {
                    posts.push(text);
                    break;
                }
            }
        });
        return posts.slice(0, 10);
    })()
    """
    return gateway_act("evaluate", fn=js_code) or []

def save_posts(posts: list, output_file: Path):
    """保存帖子到 CSV"""
    if not posts:
        return 0
    
    existing = set()
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[1:]:
                if line.strip():
                    existing.add(line[:100])
    
    new_count = 0
    with open(output_file, 'a', encoding='utf-8') as f:
        if not output_file.exists() or output_file.stat().st_size == 0:
            f.write("采集时间,内容摘要,零件号,业务意图\n")
        
        for post in posts:
            text = post.get('text', '')[:500].replace(',', ' ').replace('\n', ' ').replace('\r', '')
            if text[:100] in existing:
                continue
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pns = ','.join(post.get('pn', []))
            business = '是' if post.get('business_intent') else '否'
            
            f.write(f"{timestamp},{text},{pns},{business}\n")
            new_count += 1
            existing.add(text[:100])
    
    return new_count

def main():
    log("=" * 60)
    log("LinkedIn Feed 采集 - Gateway HTTP API")
    log(f"目标时长: {DURATION_MINUTES} 分钟")
    log("=" * 60)
    
    # 检查 Gateway 连接
    try:
        r = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        log(f"Gateway: {r.status_code}")
    except:
        log("Gateway 未响应!")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = OUTPUT_DIR / f"LinkedIn_Gateway_{timestamp}.csv"
    
    all_posts = []
    scroll_count = 0
    start_time = time.time()
    end_time = start_time + DURATION_MINUTES * 60
    
    log("开始采集...")
    
    while time.time() < end_time:
        scroll_count += 1
        remaining = int((end_time - time.time()) / 60)
        
        # 滚动
        scroll_page()
        time.sleep(SCROLL_PAUSE)
        
        # 提取
        texts = get_posts()
        
        found = 0
        for text in texts:
            if isinstance(text, str) and len(text) > 50:
                pns = extract_pn(text)
                business = has_business_intent(text)
                
                if business or pns:
                    post = {
                        'text': text,
                        'pn': pns,
                        'business_intent': business
                    }
                    all_posts.append(post)
                    found += 1
        
        log(f"滚动 #{scroll_count} | 剩余 {remaining}分钟 | 发现 {found} 条 | 总计 {len(all_posts)} 条")
        
        # 每 15 次滚动保存
        if scroll_count % 15 == 0:
            new_count = save_posts(all_posts, output_file)
            if new_count:
                log(f"  保存 {new_count} 条新帖子")
        
        # 随机等待
        wait = SCROLL_PAUSE + (scroll_count % 3)
        time.sleep(wait)
    
    # 最终保存
    final_count = save_posts(all_posts, output_file)
    
    log("=" * 60)
    log("采集完成!")
    log(f"总滚动: {scroll_count} 次")
    log(f"总帖子: {len(all_posts)} 条")
    log(f"新保存: {final_count} 条")
    log(f"文件: {output_file}")
    log("=" * 60)

if __name__ == "__main__":
    main()