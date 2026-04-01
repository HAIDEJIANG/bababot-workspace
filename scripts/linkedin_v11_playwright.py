#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集脚本 v11 - Playwright 版

使用 Playwright 浏览器自动化，可以正确处理 Shadow DOM 和动态内容。

用法：
  python scripts/linkedin_v11_playwright.py --duration 5
"""

import sys
import io
import time
import json
import re
import argparse
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 配置 ====================

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_DURATION_MINUTES = 5
SCROLL_PAUSE = 2
SCROLL_PIXELS = 800

# PN 号识别正则
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',
]

# 业务关键词
BUSINESS_KEYWORDS = [
    'available', 'stock', 'price', 'quote', 'RFQ', 'offer',
    '现货', '价格', '询价', '报价', '出售', '采购',
    'PN', 'P/N', 'Part Number', '件号',
    'CFM56', 'V2500', 'A320', 'B737', 'engine', 'landing gear', 'APU',
]

# ==================== 工具函数 ====================

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
    return score >= 2

def save_posts(posts: list, output_file: Path):
    if not posts:
        log("[INFO] 没有帖子需要保存")
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("采集时间，发帖人，发布时间，内容摘要，零件号，业务意图，原始链接\n")
        
        for post in posts:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            author = post.get('author', 'Unknown').replace(',', ' ')
            pub_time = post.get('timestamp', '') or ''
            content = post.get('text', '')[:500].replace(',', ' ').replace('\n', ' ')
            pns = ','.join(post.get('pn', []))
            business = '是' if post.get('business_intent') else '否'
            link = post.get('link', '')
            
            f.write(f"{timestamp},{author},{pub_time},{content},{pns},{business},{link}\n")
    
    log(f"[OK] 已保存 {len(posts)} 条帖子到：{output_file}")

def save_raw_posts(posts: list, output_file: Path):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    log(f"[OK] 已保存原始数据到：{output_file}")

def log(msg: str):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

# ==================== 主采集流程 ====================

def collect_linkedin_posts(duration_minutes: int):
    log("=" * 70)
    log("LinkedIn 采集 v11 - Playwright 版")
    log("=" * 70)
    log(f"采集时长：{duration_minutes} 分钟")
    log(f"输出目录：{OUTPUT_DIR}")
    
    posts_collected = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        # 连接到现有浏览器（9222 端口）
        log("\n[INFO] 连接到现有浏览器 (CDP 端口 9222)...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            log("[OK] 浏览器连接成功")
        except Exception as e:
            log(f"[ERR] 浏览器连接失败：{e}")
            log("[INFO] 尝试启动新浏览器...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=r"C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile",
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                ]
            )
        
        # 检查是否已登录
        log("[INFO] 检查登录状态...")
        # 获取或创建页面
        try:
            contexts = browser.contexts
            if contexts and contexts[0].pages:
                page = contexts[0].pages[0]
            else:
                page = contexts[0].new_page() if contexts else browser.new_page()
        except:
            page = browser.new_page()
        
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        
        # 等待页面加载
        try:
            page.wait_for_selector('article', timeout=30000)
            log("[OK] LinkedIn Feed 已加载")
        except PlaywrightTimeout:
            log("[WARN] 未检测到 article 元素，可能未登录或页面结构变化")
        
        log("\n" + "=" * 70)
        log("开始采集...")
        log("=" * 70)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        scroll_count = 0
        
        while time.time() < end_time:
            try:
                # 提取帖子 - 使用多种选择器
                posts = page.evaluate("""
                    () => {
                        var posts = [];
                        
                        // 方法 1: article 标签
                        var articles = document.querySelectorAll('article');
                        for (var i = 0; i < articles.length; i++) {
                            var el = articles[i];
                            var text = el.innerText || '';
                            if (text.length < 100) continue;
                            
                            var authorEl = el.querySelector('[href*="/in/"]');
                            var author = authorEl ? authorEl.innerText : 'Unknown';
                            
                            var timeEl = el.querySelector('time');
                            var timestamp = timeEl ? timeEl.getAttribute('datetime') : null;
                            
                            posts.push({
                                author: author,
                                text: text.substring(0, 3000),
                                timestamp: timestamp,
                                hash: text.substring(0, 200)
                            });
                        }
                        
                        // 方法 2: div[role="article"]
                        var roleArticles = document.querySelectorAll('div[role="article"]');
                        for (var i = 0; i < roleArticles.length; i++) {
                            var el = roleArticles[i];
                            var text = el.innerText || '';
                            if (text.length < 100) continue;
                            
                            var authorEl = el.querySelector('[href*="/in/"]');
                            var author = authorEl ? authorEl.innerText : 'Unknown';
                            
                            posts.push({
                                author: author,
                                text: text.substring(0, 3000),
                                timestamp: null,
                                hash: text.substring(0, 200)
                            });
                        }
                        
                        return posts;
                    }
                """)
                
                new_count = 0
                for post_data in posts:
                    post_hash = hash(post_data.get('hash', ''))
                    
                    if post_hash not in seen_hashes:
                        seen_hashes.add(post_hash)
                        
                        # 提取零件号
                        pns = extract_pn(post_data.get('text', ''))
                        business = has_business_intent(post_data.get('text', ''))
                        
                        post_record = {
                            'author': post_data.get('author', 'Unknown'),
                            'text': post_data.get('text', ''),
                            'timestamp': post_data.get('timestamp'),
                            'pn': pns,
                            'business_intent': business,
                            'link': f"https://www.linkedin.com/feed/update/{post_hash}",
                            'collected_at': datetime.now().isoformat()
                        }
                        
                        posts_collected.append(post_record)
                        new_count += 1
                        
                        if business or pns:
                            log(f"[TARGET] 高价值帖子：{post_data.get('author', 'Unknown')[:30]} | PN: {pns if pns else 'N/A'}")
                
                if new_count > 0:
                    log(f"[NEW] 新增 {new_count} 条帖子（总计：{len(posts_collected)}）")
                else:
                    log(f"[INFO] 本轮未找到新帖子，当前总计：{len(posts_collected)}")
                
                # 滚动页面
                log(f"[SCROLL] 滚动页面 (第 {scroll_count + 1} 次)")
                page.mouse.wheel(0, SCROLL_PIXELS)
                scroll_count += 1
                time.sleep(SCROLL_PAUSE)
                
                # 每 5 分钟保存一次进度
                elapsed = (time.time() - start_time) / 60
                if int(elapsed) % 5 == 0 and int(elapsed) > 0:
                    temp_file = OUTPUT_DIR / f"linkedin_posts_temp_{datetime.now().strftime('%H%M')}.json"
                    save_raw_posts(posts_collected, temp_file)
            
            except Exception as e:
                log(f"[WARN] 采集异常：{e}")
                time.sleep(5)
        
        browser.close()
    
    elapsed_minutes = (time.time() - start_time) / 60
    log("\n" + "=" * 70)
    log("采集完成")
    log("=" * 70)
    log(f"运行时长：{elapsed_minutes:.1f} 分钟")
    log(f"采集帖子：{len(posts_collected)} 条")
    log(f"滚动次数：{scroll_count} 次")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"linkedin_posts_{timestamp}.csv"
    json_file = OUTPUT_DIR / f"linkedin_posts_{timestamp}.json"
    
    save_posts(posts_collected, csv_file)
    save_raw_posts(posts_collected, json_file)
    
    high_value = [p for p in posts_collected if p.get('business_intent') or p.get('pn')]
    if high_value:
        log(f"\n[TARGET] 高价值帖子：{len(high_value)} 条")
        for post in high_value[:10]:
            log(f"  - {post.get('author', 'Unknown')[:40]} | PN: {post.get('pn', ['N/A'])[0]}")
    
    return len(posts_collected)

# ==================== 命令行入口 ====================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn 采集 v11 - Playwright 版')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION_MINUTES,
                        help=f'采集时长（分钟），默认 {DEFAULT_DURATION_MINUTES}')
    
    args = parser.parse_args()
    
    try:
        collect_linkedin_posts(args.duration)
    except KeyboardInterrupt:
        log("\n[WARN] 用户中断")
    except Exception as e:
        log(f"\n[ERR] 程序异常：{e}")
        import traceback
        traceback.print_exc()
