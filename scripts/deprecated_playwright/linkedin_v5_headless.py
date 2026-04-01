#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集 v5.0 - 无头反检测版
特点：
- 无头模式 + 住宅代理
- 完整的浏览器指纹伪装
- 随机化行为模拟
"""

import time
import json
import sys
import io
import random
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright

# 配置
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)
run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = OUTPUT_DIR / f"linkedin_v5_log_{run_id}.txt"
results_file = OUTPUT_DIR / f"linkedin_v5_posts_{run_id}.csv"

# 反检测配置
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
]

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
        posts = posts_data[:15]
    except Exception as e:
        log(f"提取失败：{e}")
    return posts

def main():
    log("=" * 60)
    log("LinkedIn 采集 v5.0 - 无头反检测版")
    log("=" * 60)
    
    start_time = datetime.now()
    total_posts = 0
    unique_posts = set()
    
    with sync_playwright() as p:
        # 启动无头浏览器（带反检测）
        log("启动无头浏览器...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        )
        
        # 创建上下文（随机指纹）
        viewport = random.choice(VIEWPORTS)
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport=viewport,
            locale="en-US",
            timezone_id="Asia/Shanghai",
        )
        
        # 导入 Cookie
        cookie_file = Path(__file__).parent / "linkedin_cookies.json"
        if cookie_file.exists():
            log("导入 Cookie...")
            with open(cookie_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            context.add_cookies(data.get('cookies', []))
            log(f"导入 {len(data.get('cookies', []))} 个 Cookie")
        else:
            log("⚠️ 未找到 Cookie 文件，将使用未登录模式")
        
        page = context.new_page()
        
        # 隐藏 webdriver 特征
        page.add_init_script('''() => {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        }''')
        
        log("浏览器启动完成")
        log(f"Viewport: {viewport['width']}x{viewport['height']}")
        
        # 访问 LinkedIn
        log("访问 LinkedIn...")
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        log(f"当前 URL: {page.url}")
        
        # 检查登录
        if "sign-in" in page.url.lower():
            log("❌ 未登录状态，请更新 Cookie")
            browser.close()
            return
        else:
            log("✅ 已登录状态")
        
        # 采集 30 分钟
        batch = 0
        while (datetime.now() - start_time).total_seconds() < 1800:
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
            
            # 随机滚动（模拟人工）
            scroll_count = random.randint(8, 15)
            for i in range(scroll_count):
                scroll_dist = random.randint(600, 1200)
                page.evaluate(f"window.scrollBy(0, {scroll_dist})")
                time.sleep(random.uniform(2, 5))
            
            # 偶尔返回顶部
            if batch % 3 == 0:
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(random.uniform(2, 4))
            
            # 保存状态
            state = {
                'elapsed_minutes': elapsed,
                'total_posts': total_posts,
                'unique_posts': len(unique_posts),
                'batch': batch
            }
            state_file = OUTPUT_DIR / f"linkedin_v5_state_{run_id}.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        
        # 完成
        elapsed = (datetime.now() - start_time).total_seconds() / 60
        log("=" * 60)
        log("采集完成！")
        log("=" * 60)
        log(f"运行时长：{elapsed:.1f} 分钟")
        log(f"总浏览：{total_posts} 个帖子")
        log(f"唯一新增：{len(unique_posts)} 个帖子")
        log(f"重复率：{(1 - len(unique_posts)/total_posts)*100:.1f}%")
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
