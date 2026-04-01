#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 快速采集脚本 - 简化版
直接连接现有浏览器，访问 LinkedIn Feed 并采集帖子
"""
import sys
import io
import time
import json
import re
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

# 导入 Cookie 管理
def load_cookies(context, cookie_file):
    """加载 Cookie 到浏览器上下文"""
    cookie_path = Path(cookie_file)
    if not cookie_path.exists():
        log(f"Cookie 文件不存在：{cookie_path}")
        return False
    
    try:
        with open(cookie_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cookies = data.get('cookies', [])
        if cookies:
            context.add_cookies(cookies)
            log(f"已加载 {len(cookies)} 个 Cookie")
            return True
        else:
            log("Cookie 为空")
            return False
    except Exception as e:
        log(f"加载 Cookie 失败：{e}")
        return False

# 配置
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)
CDP_PORT = 9222
DURATION_MINUTES = 35  # 不低于 30 分钟
SCROLL_PAUSE = 3

# PN 号识别
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',
]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")

def extract_pn(text):
    pns = []
    for pattern in PN_PATTERNS:
        pns.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(pns))

def extract_posts(page):
    posts = []
    try:
        # 使用 article 选择器
        elements = page.query_selector_all('article, div[role="article"], div.update-v2')
        
        for idx, el in enumerate(elements):
            try:
                text = el.inner_text()
                if len(text.strip()) < 100:
                    continue
                
                # 过滤广告
                if 'Sponsored' in text or 'Promoted' in text or '广告' in text:
                    continue
                
                post = {
                    'index': idx,
                    'text': text[:2000],
                    'pn_numbers': extract_pn(text),
                    'collected_at': datetime.now().isoformat(),
                    'url': 'https://www.linkedin.com/feed'
                }
                posts.append(post)
            except:
                continue
    except Exception as e:
        log(f"提取失败：{e}")
    
    return posts

def main():
    log("=" * 60)
    log("LinkedIn 快速采集 - 简化版")
    log("=" * 60)
    
    posts_collected = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        try:
            # 连接浏览器
            log("连接浏览器...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}", timeout=30000)
            log("连接成功")
            
            context = browser.contexts[0]
            
            # 加载 Cookie
            cookie_file = Path(__file__).parent / "linkedin_cookies.json"
            load_cookies(context, cookie_file)
            
            page = context.pages[0] if context.pages else context.new_page()
            
            # 访问 LinkedIn - 使用更宽松的策略
            log(f"当前页面：{page.url}")
            
            if 'linkedin.com' not in page.url:
                log("尝试访问 LinkedIn Feed...")
                try:
                    # 尝试导航，不等待完全加载
                    page.goto('https://www.linkedin.com/feed', wait_until='commit', timeout=30000)
                    time.sleep(8)
                except Exception as e:
                    log(f"导航失败：{e}")
                    log("⚠️ 请在 Edge 浏览器中访问 https://www.linkedin.com/feed")
                    log("等待 15 秒...")
                    time.sleep(15)
            
            # 检查页面
            log(f"当前页面：{page.url}")
            
            if 'sign-in' in page.url:
                log("⚠️ 未登录状态")
            elif 'linkedin.com' in page.url:
                log("✅ LinkedIn 已就绪")
            else:
                log("⚠️ 页面异常")
            
            log(f"最终页面：{page.url}")
            
            # 开始采集
            log(f"开始采集（{DURATION_MINUTES}分钟）...")
            start_time = time.time()
            end_time = start_time + (DURATION_MINUTES * 60)
            scroll_count = 0
            
            while time.time() < end_time:
                # 提取帖子
                posts = extract_posts(page)
                new_count = 0
                
                for post in posts:
                    post_hash = hash(post['text'])
                    if post_hash not in seen_hashes:
                        seen_hashes.add(post_hash)
                        posts_collected.append(post)
                        new_count += 1
                        
                        if post['pn_numbers']:
                            log(f"  发现含 PN 的帖子：{post['pn_numbers']}")
                
                elapsed = int(time.time() - start_time)
                log(f"滚动 #{scroll_count} | 累计：{len(posts_collected)} | 新增：{new_count} | {elapsed//60}m{elapsed%60}s")
                
                # 滚动
                page.evaluate('window.scrollBy(0, 1000)')
                scroll_count += 1
                time.sleep(SCROLL_PAUSE)
            
            log("=" * 60)
            log(f"采集完成！总帖子数：{len(posts_collected)}")
            log(f"含 PN 帖子：{sum(1 for p in posts_collected if p['pn_numbers'])}")
            
            # 保存 CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = OUTPUT_DIR / f"linkedin_quick_{timestamp}.csv"
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write("序号，PN 号，帖子内容，采集时间，链接\n")
                for post in posts_collected:
                    text_escaped = post['text'].replace('"', '""').replace('\n', ' ')
                    pn_str = ';'.join(post['pn_numbers'])
                    f.write(f'{post["index"]},"{pn_str}","{text_escaped[:500]}",{post["collected_at"]},{post["url"]}\n')
            
            log(f"CSV 已保存：{csv_path}")
            
            browser.close()
            
        except Exception as e:
            log(f"失败：{e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
