#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 1 小时采集 - 直接启动浏览器版
"""

import time
import sys
import io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)
USER_DATA_DIR = r"C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data"

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - 60 分钟任务")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        log("启动 Edge 浏览器...")
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ],
                timeout=60000
            )
            log("浏览器启动成功")
        except Exception as e:
            log(f"启动失败：{e}")
            log("尝试备用数据目录...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=r"C:\Users\Haide\AppData\Local\OpenClaw\BrowserData",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                timeout=60000
            )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        log("访问 LinkedIn Feed...")
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        
        # 检查登录状态
        if "sign-in" in page.url.lower():
            log("请手动登录 LinkedIn...")
            log("等待 120 秒...")
            for i in range(120):
                time.sleep(1)
                if i % 10 == 0:
                    log(f"等待中... ({i}/120 秒)")
                if "feed" in page.url.lower():
                    log("登录成功！")
                    break
            else:
                if "sign-in" in page.url.lower():
                    log("登录超时，但继续尝试采集...")
        
        log(f"当前页面：{page.url}")
        log("开始采集，目标 60 分钟...")
        log("-" * 70)
        
        batch_num = 0
        while (datetime.now() - start_time).total_seconds() < 60 * 60:
            batch_num += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            
            # 检查页面
            try:
                if "linkedin" not in page.url.lower():
                    page.goto("https://www.linkedin.com/feed/", timeout=30000)
                    time.sleep(3)
            except:
                pass
            
            log(f"\n【批次 {batch_num}】{elapsed:.1f} 分钟")
            
            # 滚动
            for i in range(3):
                try:
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(2)
                except:
                    pass
            
            # 提取
            try:
                posts = page.evaluate('''() => {
                    const results = [];
                    const elements = document.querySelectorAll('[data-id*="urn:li:activity"], div[class*="update"], article');
                    elements.slice(0, 15).forEach(el => {
                        const text = el.innerText;
                        if (text && text.length > 100) {
                            results.push(text.substring(0, 800));
                        }
                    });
                    return results;
                }''')
                
                new_count = 0
                for post in posts:
                    h = hash(post)
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        all_posts.append({"text": post, "time": datetime.now().isoformat()})
                        new_count += 1
                
                log(f"看到 {len(posts)} 个，新增 {new_count} 个，总计 {len(all_posts)} 个")
                
                # 保存
                if len(all_posts) > 0 and batch_num % 2 == 0:
                    with open(OUTPUT_DIR / "linkedin_1hour.csv", 'w', encoding='utf-8') as f:
                        f.write("timestamp,text\n")
                        for p in all_posts:
                            f.write(f'"{p["time"]}","{p["text"].replace(chr(34), chr(34)+chr(34))}"\n')
                    log(f"已保存 {len(all_posts)} 条")
                    
            except Exception as e:
                log(f"提取失败：{e}")
            
            time.sleep(30)  # 每批次 30 秒
        
        # 最终保存
        if all_posts:
            with open(OUTPUT_DIR / "linkedin_1hour_final.csv", 'w', encoding='utf-8') as f:
                f.write("timestamp,text\n")
                for p in all_posts:
                    f.write(f'"{p["time"]}","{p["text"].replace(chr(34), chr(34)+chr(34))}"\n')
            log(f"\n完成！共 {len(all_posts)} 条帖子")
        else:
            log("\n未采集到数据")
        
        browser.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("用户中断")
    except Exception as e:
        log(f"错误：{e}")
        import traceback
        traceback.print_exc()
