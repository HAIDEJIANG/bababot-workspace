#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 采集脚本 - 1小时版本
使用 OpenClaw Gateway HTTP API 控制 Edge 浏览器
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
BROWSER_PORT = 18800
TARGET_ID = "ADF0A2830B02D1A0B58A55ECE358A323"
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

DURATION_MINUTES = 60  # 采集时长
SCROLL_PAUSE = 4  # 滚动后等待秒数
SCROLL_PIXELS = 800  # 每次滚动像素

# PN 号识别正则
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',
    r'\b[A-Z]{1,2}-[0-9]{4,}-[0-9]{2,}\b',
]

# 业务关键词
BUSINESS_KEYWORDS = [
    'available', 'stock', 'price', 'quote', 'RFQ', 'offer', 'sale', 'buy',
    '现货', '价格', '询价', '报价', '出售', '采购',
    'PN', 'P/N', 'Part Number', '件号',
    'CFM56', 'V2500', 'A320', 'B737', 'LEAP', 'PW', 'GE',
    'engine', 'landing gear', 'APU', 'rotable', 'surplus',
    'aircraft', 'helicopter', 'component', 'module',
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
    score = 0
    for keyword in BUSINESS_KEYWORDS:
        if keyword.lower() in text_lower:
            score += 1
    return score >= 1  # 降低阈值，单关键词匹配也算

def gateway_request(action, params=None):
    """通过 Gateway HTTP API 发送浏览器指令"""
    payload = {
        "action": action,
        "targetId": TARGET_ID,
    }
    if params:
        payload.update(params)
    
    try:
        r = requests.post(f"{GATEWAY_URL}/browser", json=payload, timeout=30)
        return r.json()
    except Exception as e:
        log(f"Gateway error: {e}")
        return None

def scroll_page():
    """向下滚动页面"""
    result = gateway_request("act", {
        "request": {
            "kind": "evaluate",
            "fn": f"window.scrollBy(0, {SCROLL_PIXELS})"
        }
    })
    return result

def get_page_text():
    """获取页面文本内容"""
    result = gateway_request("act", {
        "request": {
            "kind": "evaluate",
            "fn": """
            (() => {
                // 尝试多种方式提取帖子内容
                let posts = [];
                
                // 方法1: 查找所有包含 urn:li:activity 的元素
                document.querySelectorAll('[data-id*="urn:li:activity"]').forEach(el => {
                    let text = el.innerText || el.textContent;
                    if (text && text.length > 50) {
                        posts.push(text);
                    }
                });
                
                // 方法2: 查找所有 article 标签
                if (posts.length === 0) {
                    document.querySelectorAll('article').forEach(el => {
                        let text = el.innerText || el.textContent;
                        if (text && text.length > 50) {
                            posts.push(text);
                        }
                    });
                }
                
                // 方法3: 查找 feed-update 类
                if (posts.length === 0) {
                    document.querySelectorAll('.feed-update, .update-v2').forEach(el => {
                        let text = el.innerText || el.textContent;
                        if (text && text.length > 50) {
                            posts.push(text);
                        }
                    });
                }
                
                // 方法4: 遍历所有 div，查找包含业务关键词的
                if (posts.length === 0) {
                    document.querySelectorAll('div').forEach(el => {
                        let text = el.innerText || '';
                        if (text.length > 100 && text.length < 2000) {
                            // 检查是否包含业务关键词
                            let keywords = ['CFM56', 'V2500', 'A320', 'B737', 'engine', 'landing', 'APU', 
                                          'stock', 'price', 'available', 'PN', 'P/N', '件号', '现货'];
                            for (let kw of keywords) {
                                if (text.toLowerCase().includes(kw.toLowerCase())) {
                                    posts.push(text);
                                    break;
                                }
                            }
                        }
                    });
                }
                
                // 方法5: 直接获取 body 文本（最后手段）
                if (posts.length === 0) {
                    let bodyText = document.body.innerText;
                    // 按段落分割
                    let paragraphs = bodyText.split('\\n\\n').filter(p => p.length > 50);
                    posts = paragraphs.slice(0, 10);  // 取前10段
                }
                
                return posts.slice(0, 20);  // 最多返回20条
            })()
            """
        }
    })
    
    if result and 'ok' in result:
        return result.get('result', [])
    return []

def save_posts(posts: list, output_file: Path):
    if not posts:
        return
    
    # 读取已有数据
    existing = set()
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[1:]:  # 跳过表头
                if line.strip():
                    existing.add(line[:100])  # 用前100字符作为唯一标识
    
    # 追加新数据
    with open(output_file, 'a', encoding='utf-8') as f:
        if output_file.exists() and output_file.stat().st_size > 0:
            pass  # 已有表头
        else:
            f.write("采集时间,发帖人,发布时间,内容摘要,零件号,业务意图,原始链接\n")
        
        for post in posts:
            text = post.get('text', '')[:500].replace(',', ' ').replace('\n', ' ')
            if text[:100] in existing:
                continue  # 去重
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            author = post.get('author', 'Unknown').replace(',', ' ')
            pub_time = post.get('timestamp', '') or ''
            pns = ','.join(post.get('pn', []))
            business = '是' if post.get('business_intent') else '否'
            link = post.get('link', '')
            
            f.write(f"{timestamp},{author},{pub_time},{text},{pns},{business},{link}\n")

# ==================== 主采集流程 ====================

def main():
    log("=" * 50)
    log("LinkedIn Feed 采集开始")
    log(f"目标时长: {DURATION_MINUTES} 分钟")
    log(f"输出目录: {OUTPUT_DIR}")
    log("=" * 50)
    
    # 输出文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = OUTPUT_DIR / f"LinkedIn_Collection_{timestamp}.csv"
    
    all_posts = []
    scroll_count = 0
    start_time = time.time()
    end_time = start_time + DURATION_MINUTES * 60
    
    while time.time() < end_time:
        scroll_count += 1
        remaining = int((end_time - time.time()) / 60)
        log(f"滚动 #{scroll_count} | 剩余 {remaining} 分钟 | 已采集 {len(all_posts)} 条")
        
        # 滚动页面
        scroll_page()
        time.sleep(SCROLL_PAUSE)
        
        # 提取内容
        texts = get_page_text()
        
        if texts:
            for text in texts:
                pns = extract_pn(text)
                business = has_business_intent(text)
                
                if business or pns:  # 只保留有业务价值的内容
                    post = {
                        'text': text,
                        'pn': pns,
                        'business_intent': business,
                        'author': 'LinkedIn User',
                        'timestamp': '',
                        'link': ''
                    }
                    all_posts.append(post)
                    log(f"  发现帖子: PN={pns}, 业务={business}")
        
        # 每 10 次滚动保存一次
        if scroll_count % 10 == 0:
            save_posts(all_posts, output_file)
            log(f"  已保存 {len(all_posts)} 条到 {output_file.name}")
        
        # 随机等待，模拟人类行为
        wait_time = SCROLL_PAUSE + (scroll_count % 3)
        time.sleep(wait_time)
    
    # 最终保存
    save_posts(all_posts, output_file)
    
    log("=" * 50)
    log("采集完成!")
    log(f"总滚动次数: {scroll_count}")
    log(f"总采集帖子: {len(all_posts)} 条")
    log(f"输出文件: {output_file}")
    log("=" * 50)

if __name__ == "__main__":
    main()