#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集 - CDP 连接 Chrome 浏览器
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

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - CDP 连接 Chrome")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        # 连接 Chrome (默认 CDP 端口 9222)
        log("连接 Chrome 浏览器 (CDP :9222)...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
            log("连接成功")
        except Exception as e:
            log(f"CDP 连接失败：{e}")
            log("尝试启动 Chrome...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=r"C:\Users\Haide\AppData\Local\Google\Chrome\User Data",
                headless=False,
                args=["--remote-debugging-port=9222", "--no-sandbox"],
                timeout=60000
            )
        
        # 获取所有页面
        contexts = browser.contexts
        log(f"找到 {len(contexts)} 个上下文")
        
        linkedin_page = None
        for ctx in contexts:
            for page in ctx.pages:
                try:
                    url = page.url
                    log(f"  页面：{url[:80]}...")
                    if "linkedin.com/feed" in url.lower():
                        linkedin_page = page
                        log("  -> 找到 LinkedIn Feed 页面!")
                except:
                    pass
        
        if not linkedin_page:
            # 创建新页面
            log("未找到 LinkedIn 页面，创建新页面...")
            for ctx in contexts:
                linkedin_page = ctx.new_page()
                break
            if not linkedin_page:
                linkedin_page = browser.new_page()
            
            log("访问 LinkedIn...")
            linkedin_page.goto("https://www.linkedin.com/feed/", timeout=60000)
            time.sleep(5)
        
        page = linkedin_page
        page.bring_to_front()
        
        log(f"\n当前页面：{page.url}")
        log("开始采集，目标 60 分钟...")
        log("-" * 70)
        
        batch_num = 0
        while (datetime.now() - start_time).total_seconds() < 60 * 60:
            batch_num += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            
            # 检查页面
            try:
                url = page.url
                if "linkedin.com" not in url.lower():
                    log(f"页面跳转：{url[:60]}... 返回 LinkedIn...")
                    page.goto("https://www.linkedin.com/feed/", timeout=30000)
                    time.sleep(3)
            except Exception as e:
                log(f"页面检查失败：{e}")
                try:
                    page.goto("https://www.linkedin.com/feed/", timeout=30000)
                    time.sleep(3)
                except:
                    log("无法恢复页面，结束")
                    break
            
            log(f"\n【批次 {batch_num}】{elapsed:.1f} 分钟")
            
            # 滚动
            for i in range(3):
                try:
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(2)
                except:
                    pass
            
            # 提取帖子
            try:
                posts_data = page.evaluate('''() => {
                    const results = [];
                    const elements = document.querySelectorAll('[data-id*="urn:li:activity"], div[class*="update"], article');
                    elements.forEach(function(el) {
                        try {
                            const text = el.innerText;
                            if (text && text.length > 100) {
                                results.push(text.substring(0, 800));
                            }
                        } catch(e) {}
                    });
                    return results;
                }''')
                
                new_count = 0
                for post in posts_data:
                    h = hash(post)
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        all_posts.append({"text": post, "time": datetime.now().isoformat()})
                        new_count += 1
                
                log(f"看到 {len(posts_data)} 个，新增 {new_count} 个，总计 {len(all_posts)} 个")
                
                # 保存
                if len(all_posts) > 0 and batch_num % 2 == 0:
                    with open(OUTPUT_DIR / "linkedin_1hour.csv", 'w', encoding='utf-8') as f:
                        f.write("timestamp,text\n")
                        for p in all_posts:
                            text_safe = p["text"].replace('"', '""')
                            f.write(f'"{p["time"]}","{text_safe}"\n')
                    log(f"已保存 {len(all_posts)} 条")
                    
            except Exception as e:
                log(f"提取失败：{e}")
            
            time.sleep(30)
        
        # 最终保存
        if all_posts:
            with open(OUTPUT_DIR / "linkedin_1hour_final.csv", 'w', encoding='utf-8') as f:
                f.write("timestamp,text\n")
                for p in all_posts:
                    text_safe = p["text"].replace('"', '""')
                    f.write(f'"{p["time"]}","{text_safe}"\n')
            log(f"\n" + "=" * 70)
            log(f"采集完成！共 {len(all_posts)} 条帖子")
            log(f"输出文件：{OUTPUT_DIR / 'linkedin_1hour_final.csv'}")
            log("=" * 70)
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
