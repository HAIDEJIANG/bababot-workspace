#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集脚本 - Browser Relay 模式
直接操作 Edge 浏览器中已登录的 LinkedIn 标签页
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

# 配置
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)
DURATION_MINUTES = 30
CDP_PORT = 9222

# PN 号识别
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")

def extract_pn(text):
    pns = []
    for pattern in PN_PATTERNS:
        pns.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(pns))

def main():
    log("=" * 60)
    log("LinkedIn 采集 - Browser Relay 模式")
    log("=" * 60)
    log(f"CDP 端口：{CDP_PORT}")
    log(f"采集时长：{DURATION_MINUTES} 分钟")
    
    posts_collected = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        try:
            # 连接浏览器
            log("连接浏览器...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}", timeout=30000)
            log("✅ 连接成功")
            
            # 查找 LinkedIn 页面
            context = browser.contexts[0]
            pages = context.pages
            
            log(f"找到 {len(pages)} 个标签页")
            
            # 查找 LinkedIn Feed 页面
            target_page = None
            for i, page in enumerate(pages):
                try:
                    url = page.url
                    log(f"  页面 {i}: {url[:80]}...")
                    if 'linkedin.com/feed' in url and 'sign-in' not in url:
                        target_page = page
                        log(f"  ✅ 找到已登录的 Feed 页面！")
                        break
                except:
                    continue
            
            if not target_page:
                log("❌ 未找到已登录的 LinkedIn Feed 页面")
                log("请在 Edge 中打开 https://www.linkedin.com/feed 并确保已登录")
                browser.close()
                return
            
            # 开始采集
            log(f"\n开始采集（{DURATION_MINUTES}分钟）...")
            start_time = time.time()
            end_time = start_time + (DURATION_MINUTES * 60)
            scroll_count = 0
            
            while time.time() < end_time:
                try:
                    # 提取帖子
                    posts_data = target_page.evaluate('''() => {
                        var posts = [];
                        var articles = document.querySelectorAll('article, div[role="article"]');
                        for (var i = 0; i < articles.length; i++) {
                            var text = articles[i].innerText;
                            if (text && text.length > 100) {
                                posts.push(text.substring(0, 2000));
                            }
                        }
                        return posts;
                    }''')
                    
                    new_count = 0
                    for text in posts_data:
                        post_hash = hash(text)
                        if post_hash not in seen_hashes:
                            seen_hashes.add(post_hash)
                            posts_collected.append({
                                'text': text,
                                'pn_numbers': extract_pn(text),
                                'collected_at': datetime.now().isoformat()
                            })
                            new_count += 1
                            
                            if extract_pn(text):
                                log(f"  🎯 发现含 PN 的帖子：{extract_pn(text)}")
                    
                    elapsed = int(time.time() - start_time)
                    log(f"滚动 #{scroll_count} | 累计：{len(posts_collected)} | 新增：{new_count} | {elapsed//60}m{elapsed%60}s")
                    
                    # 滚动页面
                    target_page.evaluate('window.scrollBy(0, 800)')
                    scroll_count += 1
                    time.sleep(5)
                    
                except Exception as e:
                    log(f"提取失败：{e}")
                    time.sleep(3)
            
            log("=" * 60)
            log(f"采集完成！")
            log(f"总帖子数：{len(posts_collected)}")
            log(f"含 PN 帖子：{sum(1 for p in posts_collected if p['pn_numbers'])}")
            
            # 保存 CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = OUTPUT_DIR / f"linkedin_relay_{timestamp}.csv"
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write("序号，PN 号，帖子内容，采集时间\n")
                for i, post in enumerate(posts_collected):
                    text_escaped = post['text'].replace('"', '""').replace('\n', ' ')
                    pn_str = ';'.join(post['pn_numbers'])
                    f.write(f'{i},"{pn_str}","{text_escaped[:500]}",{post["collected_at"]}\n')
            
            log(f"CSV 已保存：{csv_path}")
            
            browser.close()
            
        except Exception as e:
            log(f"❌ 失败：{e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
