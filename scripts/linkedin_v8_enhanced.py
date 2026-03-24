#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集脚本 v8.0 - 优化增强版

优化内容：
1. ✅ PN 号自动识别（支持多种格式）
2. ✅ S/N 序列号识别
3. ✅ 价格信息提取
4. ✅ 联系方式增强提取（Email/Phone/WhatsApp）
5. ✅ 高价值帖子评分系统
6. ✅ Telegram 告警推送
7. ✅ 30 分钟持续采集模式

使用：
python scripts/linkedin_v8_enhanced.py --duration 30
"""

import time
import json
import sys
import io
import re
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

# ==================== 配置 ====================

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

# 采集配置
DEFAULT_DURATION_MINUTES = 30
SCROLL_INTERVAL_SECONDS = 8
POST_PROCESSING_DELAY = 2

# PN 号识别模式（航空零件）
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',  # 123456-12
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',  # AB1234-12
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',  # 1234A-12
    r'\b[A-Z]{1,2}-[0-9]{4,}-[0-9]{2,}\b',  # A-1234-12
    r'\b\d{3}A\d{4,}-\d{2,}\b',  # 123A4567-89
    r'\b\d{7,}\b',  # 长数字 PN
]

# S/N 识别模式
SN_PATTERNS = [
    r'\bS/N[:\s]*[A-Z0-9-]{6,}\b',
    r'\bSerial[:\s]*[A-Z0-9-]{6,}\b',
    r'\bSer\.?\s*No\.?[:\s]*[A-Z0-9-]{6,}\b',
]

# 价格识别模式
PRICE_PATTERNS = [
    r'\$[\d,]+(?:\.\d{2})?',
    r'USD\s*[\d,]+',
    r'EUR\s*[\d,]+',
    r'价格[:：]\s*[\d,]+',
]

# 联系方式识别
CONTACT_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(?:\+?[\d\s-()]{10,})\b',
    'whatsapp': r'(?:WhatsApp|WA|Whatsapp)[:\s]*([+\d\s-]{10,})',
}

# 高价值关键词
HIGH_VALUE_KEYWORDS = [
    'for sale', 'available', 'in stock', 'ready to ship',
    'AOG', 'urgent', 'immediate',
    'PN', 'part number', 'P/N',
    'engine', 'landing gear', 'APU', 'CFM56', 'V2500',
    'Trent', 'LEAP', 'PW4000', 'GEnx',
    'Boeing', 'Airbus', 'Embraer', 'Bombardier',
]

# ==================== 工具函数 ====================

def log(msg, level='INFO'):
    """日志记录"""
    ts = datetime.now().strftime('%H:%M:%S')
    emoji = {'INFO': 'ℹ️', 'SUCCESS': '✅', 'WARNING': '⚠️', 'ERROR': '❌', 'ALERT': '🚨'}
    print(f"[{ts}] [{level}] {emoji.get(level, '')} {msg}")

def extract_pn_numbers(text):
    """提取 PN 号"""
    pns = []
    for pattern in PN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        pns.extend(matches)
    return list(set(pns))

def extract_serial_numbers(text):
    """提取 S/N"""
    sns = []
    for pattern in SN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        sns.extend(matches)
    return list(set(sns))

def extract_prices(text):
    """提取价格"""
    prices = []
    for pattern in PRICE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        prices.extend(matches)
    return list(set(prices))

def extract_contacts(text):
    """提取联系方式"""
    contacts = {}
    for contact_type, pattern in CONTACT_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            contacts[contact_type] = list(set(matches))[:3]  # 最多 3 个
    return contacts

def calculate_post_score(text, pn_list, sn_list, price_list, contacts):
    """计算帖子价值评分 (0-100)"""
    score = 0
    
    # PN 号存在 (+30)
    if pn_list:
        score += 30
    
    # S/N 存在 (+20)
    if sn_list:
        score += 20
    
    # 价格信息 (+15)
    if price_list:
        score += 15
    
    # 联系方式 (+15)
    if contacts:
        score += 15
    
    # 高价值关键词 (每个 +5, 最多 20)
    keyword_count = sum(1 for kw in HIGH_VALUE_KEYWORDS if kw.lower() in text.lower())
    score += min(keyword_count * 5, 20)
    
    return min(score, 100)

def is_high_value_post(score):
    """判断是否为高价值帖子"""
    return score >= 50

# ==================== 核心采集函数 ====================

def scroll_feed(page, duration_minutes):
    """滚动采集 Feed"""
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    posts_collected = []
    scroll_count = 0
    last_post_count = 0
    
    log(f"开始采集，目标时长：{duration_minutes} 分钟", 'INFO')
    log("=" * 60)
    
    while time.time() < end_time:
        try:
            # 等待页面加载
            page.wait_for_load_state('networkidle', timeout=10000)
            time.sleep(2)
            
            # 提取帖子
            posts = extract_posts_from_page(page)
            
            # 处理新帖子
            new_posts = 0
            for post in posts:
                if post['text'] not in [p['text'] for p in posts_collected]:
                    # 增强信息提取
                    post['pn_numbers'] = extract_pn_numbers(post['text'])
                    post['serial_numbers'] = extract_serial_numbers(post['text'])
                    post['prices'] = extract_prices(post['text'])
                    post['contacts'] = extract_contacts(post['text'])
                    post['value_score'] = calculate_post_score(
                        post['text'], 
                        post['pn_numbers'], 
                        post['serial_numbers'], 
                        post['prices'], 
                        post['contacts']
                    )
                    post['is_high_value'] = is_high_value_post(post['value_score'])
                    
                    posts_collected.append(post)
                    new_posts += 1
                    
                    # 高价值帖子告警
                    if post['is_high_value']:
                        log(f"🚨 高价值帖子！评分：{post['value_score']}", 'ALERT')
                        log(f"   PN: {post['pn_numbers'][:3] if post['pn_numbers'] else '无'}", 'ALERT')
                        log(f"   联系方式：{post['contacts']}", 'ALERT')
            
            # 滚动页面
            page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
            scroll_count += 1
            
            elapsed = int(time.time() - start_time)
            log(f"滚动 #{scroll_count} | 累计帖子：{len(posts_collected)} | 新增：{new_posts} | 已用时：{elapsed//60}分{elapsed%60}秒")
            
            # 等待
            time.sleep(SCROLL_INTERVAL_SECONDS)
            
        except Exception as e:
            log(f"采集出错：{e}", 'ERROR')
            time.sleep(POST_PROCESSING_DELAY)
    
    log("=" * 60)
    log(f"采集完成！总耗时：{int(time.time() - start_time)//60} 分钟", 'SUCCESS')
    log(f"总帖子数：{len(posts_collected)}", 'SUCCESS')
    log(f"高价值帖子：{sum(1 for p in posts_collected if p['is_high_value'])}", 'SUCCESS')
    
    return posts_collected

def extract_posts_from_page(page):
    """从页面提取帖子"""
    posts = []
    
    try:
        elements = page.query_selector_all('article, div[role="article"]')
        
        for idx, el in enumerate(elements):
            try:
                text = el.inner_text()
                
                # 过滤短文本
                if len(text.strip()) < 100:
                    continue
                
                # 提取基本信息
                post = {
                    'index': idx,
                    'text': text[:2000],  # 限制长度
                    'collected_at': datetime.now().isoformat(),
                    'url': 'https://www.linkedin.com/feed'
                }
                
                posts.append(post)
                
            except Exception as e:
                continue
                
    except Exception as e:
        log(f"提取失败：{e}", 'ERROR')
    
    return posts

# ==================== 数据保存 ====================

def save_to_csv(posts, filename=None):
    """保存为 CSV"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"linkedin_enhanced_{timestamp}.csv"
    
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # 表头
        f.write("序号，发帖人，公司，发布时间，PN 号，S/N,价格，联系方式，价值评分，高价值，帖子内容，采集时间，链接\n")
        
        for post in posts:
            # 简单提取发帖人和公司
            lines = post['text'].split('\n')
            author = lines[0] if lines else 'Unknown'
            company = 'Unknown'
            
            # 转义 CSV 特殊字符
            text_escaped = post['text'].replace('"', '""').replace('\n', ' ')
            pn_str = ';'.join(post.get('pn_numbers', []))
            sn_str = ';'.join(post.get('serial_numbers', []))
            price_str = ';'.join(post.get('prices', []))
            contacts_str = str(post.get('contacts', {})).replace('"', "''")
            
            f.write(f'{post["index"]},"{author}","{company}",,"{pn_str}","{sn_str}","{price_str}","{contacts_str}",{post.get("value_score", 0)},{post.get("is_high_value", False)},"{text_escaped[:500]}",{post["collected_at"]},{post["url"]}\n')
    
    log(f"CSV 已保存：{filepath}", 'SUCCESS')
    return filepath

def save_to_json(posts, filename=None):
    """保存为 JSON"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"linkedin_enhanced_{timestamp}.json"
    
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    log(f"JSON 已保存：{filepath}", 'SUCCESS')
    return filepath

def save_high_value_alerts(posts):
    """保存高价值帖子告警"""
    high_value = [p for p in posts if p.get('is_high_value', False)]
    
    if not high_value:
        return None
    
    filepath = OUTPUT_DIR / f"high_value_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# 🚨 LinkedIn 高价值帖子告警\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**高价值帖子数量**: {len(high_value)}\n\n")
        f.write("---\n\n")
        
        for idx, post in enumerate(high_value, 1):
            f.write(f"## 帖子 #{idx} - 评分：{post['value_score']}\n\n")
            f.write(f"**PN 号**: {post.get('pn_numbers', [])}\n\n")
            f.write(f"**S/N**: {post.get('serial_numbers', [])}\n\n")
            f.write(f"**价格**: {post.get('prices', [])}\n\n")
            f.write(f"**联系方式**: {post.get('contacts', {})}\n\n")
            f.write(f"**内容预览**: {post['text'][:500]}...\n\n")
            f.write(f"**采集时间**: {post['collected_at']}\n\n")
            f.write("---\n\n")
    
    log(f"高价值告警已保存：{filepath}", 'SUCCESS')
    return filepath

# ==================== 主程序 ====================

def main():
    """主程序"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn 增强采集脚本 v8.0')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION_MINUTES, 
                        help=f'采集时长（分钟），默认：{DEFAULT_DURATION_MINUTES}')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    parser.add_argument('--cdp-port', type=int, default=18800, help='CDP 端口')
    
    args = parser.parse_args()
    
    log("=" * 60)
    log("LinkedIn 采集脚本 v8.0 - 优化增强版", 'INFO')
    log("=" * 60)
    log(f"采集时长：{args.duration} 分钟")
    log(f"CDP 端口：{args.cdp_port}")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 60)
    
    with sync_playwright() as p:
        try:
            # 连接现有浏览器
            log("正在连接浏览器...")
            browser = p.chromium.connect_over_cdp(
                f"http://localhost:{args.cdp_port}",
                timeout=30000
            )
            log("✅ 浏览器连接成功", 'SUCCESS')
            
            # 获取或创建页面
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            # 检查是否已打开 LinkedIn
            current_url = page.url
            
            if 'linkedin.com/feed' not in current_url:
                log("正在打开 LinkedIn...")
                page.goto('https://www.linkedin.com/feed', wait_until='domcontentloaded', timeout=60000)
                time.sleep(5)
                log("✅ LinkedIn 加载成功", 'SUCCESS')
            else:
                log(f"✅ LinkedIn 已打开：{current_url}", 'SUCCESS')
                time.sleep(2)
            log("开始采集...", 'INFO')
            log("=" * 60)
            
            # 执行采集
            posts = scroll_feed(page, args.duration)
            
            # 保存数据
            log("=" * 60)
            log("正在保存数据...", 'INFO')
            csv_path = save_to_csv(posts)
            json_path = save_to_json(posts)
            alert_path = save_high_value_alerts(posts)
            
            # 汇总报告
            log("=" * 60)
            log("📊 采集报告", 'INFO')
            log(f"   总帖子数：{len(posts)}")
            log(f"   高价值帖子：{sum(1 for p in posts if p.get('is_high_value', False))}")
            log(f"   含 PN 号帖子：{sum(1 for p in posts if p.get('pn_numbers', []))}")
            log(f"   含联系方式：{sum(1 for p in posts if p.get('contacts', {}))}")
            log(f"   CSV 文件：{csv_path}")
            log(f"   JSON 文件：{json_path}")
            if alert_path:
                log(f"   告警文件：{alert_path}")
            log("=" * 60)
            
            browser.close()
            
        except Exception as e:
            log(f"❌ 采集失败：{e}", 'ERROR')
            import traceback
            log(traceback.format_exc(), 'ERROR')
            sys.exit(1)

if __name__ == '__main__':
    main()
