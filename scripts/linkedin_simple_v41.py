#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集脚本 v4.1 - 简化快速版
直接使用现有浏览器页面，不打开新窗口
"""

import time
import json
import sys
import io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright

# 配置
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)
run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = OUTPUT_DIR / f"linkedin_simple_log_{run_id}.txt"
results_file = OUTPUT_DIR / f"linkedin_simple_posts_{run_id}.csv"

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {msg}\n")

def extract_posts(page):
    posts = []
    try:
        posts_data = page.evaluate('''() => {
            const posts = [];
            const elements = document.querySelectorAll('div[class*="update"]');
            elements.forEach(el => {
                try {
                    const text = el.innerText.substring(0, 500);
                    if (text.trim().length > 50) {
                        posts.push({
                            text: text.replace(/\\n/g, ' '),
                            time: new Date().toISOString()
                        });
                    }
                } catch(e) {}
            });
            return posts;
        }''')
        posts = posts_data[:10]
    except Exception as e:
        log(f"提取失败：{e}")
    return posts

def main():
    log("=" * 60)
    log("LinkedIn 采集 v4.1 - 简化版")
    log("=" * 60)
    
    start_time = datetime.now()
    total_posts = 0
    unique_posts = set()
    
    with sync_playwright() as p:
        # 连接浏览器
        log("连接浏览器...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
        log("连接成功")
        
        # 使用现有页面
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        # 访问 LinkedIn
        log("访问 LinkedIn...")
        page.goto("https://www.linkedin.com/feed/", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        log(f"当前 URL: {page.url}")
        
        # 检查登录
        if "sign-in" in page.url.lower():
            log("未登录，等待 30 秒...")
            time.sleep(30)
        
        log("开始采集 (目标 30 分钟)...")
        
        # 采集 30 分钟
        batch = 0
        while (datetime.now() - start_time).total_seconds() < 1800:  # 30 分钟
            batch += 1
            
            # 提取帖子
            posts = extract_posts(page)
            new_count = 0
            
            for post in posts:
                post_hash = hash(post['text'])
                if post_hash not in unique_posts:
                    unique_posts.add(post_hash)
                    new_count += 1
                    
                    with open(results_file, 'a', encoding='utf-8') as f:
                        f.write(f"{post['time']}|{post['text'][:200]}\n")
            
            total_posts += len(posts)
            
            # 日志
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            log(f"批次{batch}: 看到{len(posts)}个，新增{new_count}个，总计{total_posts}个，唯一{len(unique_posts)}个 ({elapsed:.1f}分钟)")
            
            # 滚动 - 最强版
            log(f"开始滚动...")
            for i in range(10):
                # 随机滚动距离，模拟人工
                import random
                scroll_dist = random.randint(800, 1500)
                page.evaluate(f"window.scrollBy(0, {scroll_dist})")
                time.sleep(random.uniform(3, 6))
            
            # 每批次返回顶部，强制刷新内容
            log("返回顶部刷新...")
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(3)
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(3)
            
            # 保存状态
            state = {
                'elapsed_minutes': elapsed,
                'total_posts': total_posts,
                'unique_posts': len(unique_posts),
                'batch': batch
            }
            state_file = OUTPUT_DIR / f"linkedin_state_{run_id}.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        
        # 完成
        elapsed = (datetime.now() - start_time).total_seconds() / 60
        log("=" * 60)
        log("采集完成！")
        log(f"运行时长：{elapsed:.1f} 分钟")
        log(f"总浏览：{total_posts} 个帖子")
        log(f"唯一新增：{len(unique_posts)} 个帖子")
        log(f"结果保存：{results_file}")
        log("=" * 60)
        
        browser.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n用户中断")
    except Exception as e:
        log(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
