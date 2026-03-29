#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 采集 - 直接使用 Chrome 用户数据目录
最简单稳定的方案
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

# 使用日常 Chrome 用户数据目录
CHROME_USER_DATA = r"C:\Users\Haide\AppData\Local\Google\Chrome\User Data"
CDP_PORT = 9223  # 使用不同端口避免冲突

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - Chrome 持久化会话")
    log(f"用户数据：{CHROME_USER_DATA}")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        log("\n启动 Chrome (带调试端口)...")
        
        try:
            # 启动持久化 Chrome 上下文
            context = p.chromium.launch_persistent_context(
                user_data_dir=CHROME_USER_DATA,
                headless=False,
                args=[
                    f"--remote-debugging-port={CDP_PORT}",
                    "--disable-blink-features=AutomationControlled",
                ],
                timeout=90000
            )
            log("✓ Chrome 启动成功")
        except Exception as e:
            log(f"✗ Chrome 启动失败：{e}")
            log("\n请关闭所有 Chrome 窗口后重试")
            return
        
        # 获取页面
        pages = context.pages
        log(f"找到 {len(pages)} 个页面")
        
        linkedin_page = None
        
        # 查找 LinkedIn Feed 页面
        for i, page in enumerate(pages):
            try:
                url = page.url
                log(f"  页面 {i+1}: {url[:70]}...")
                if "linkedin.com/feed" in url.lower() and "login" not in url.lower():
                    linkedin_page = page
                    log("  ✓ 找到已登录的 LinkedIn!")
            except:
                pass
        
        # 如果没有，创建新页面
        if not linkedin_page:
            log("\n创建新页面访问 LinkedIn...")
            linkedin_page = context.new_page()
            linkedin_page.goto("https://www.linkedin.com/feed/", timeout=60000)
            log("请手动登录 LinkedIn（如果还没登录）")
            time.sleep(10)
        
        page = linkedin_page
        page.bring_to_front()
        
        try:
            log(f"\n当前 URL: {page.url}")
        except:
            log("\n当前页面：LinkedIn")
        
        log("\n开始采集，目标 60 分钟...")
        log("-" * 70)
        
        batch_num = 0
        
        while (datetime.now() - start_time).total_seconds() < 60 * 60:
            batch_num += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            
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
                    const elements = document.querySelectorAll('[data-id*="urn:li:activity"], [data-id*="urn:li:share"], article');
                    elements.forEach(el => {
                        try {
                            const text = el.innerText;
                            if (text && text.length > 100 && text.length < 2000) {
                                results.push(text);
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
                
                # 定期保存
                if batch_num % 2 == 0 and all_posts:
                    with open(OUTPUT_DIR / "linkedin_1hour.csv", 'w', encoding='utf-8') as f:
                        f.write("timestamp,text\n")
                        for p in all_posts:
                            text_safe = p["text"].replace('"', '""').replace('\n', ' ')
                            f.write(f'"{p["time"]}","{text_safe}"\n')
                    log(f"✓ 已保存 {len(all_posts)} 条")
                    
            except Exception as e:
                log(f"✗ 提取失败：{e}")
            
            time.sleep(30)
        
        # 最终保存
        if all_posts:
            with open(OUTPUT_DIR / "linkedin_1hour_final.csv", 'w', encoding='utf-8') as f:
                f.write("timestamp,text\n")
                for p in all_posts:
                    text_safe = p["text"].replace('"', '""').replace('\n', ' ')
                    f.write(f'"{p["time"]}","{text_safe}"\n')
            log("\n" + "=" * 70)
            log(f"✓ 完成！共 {len(all_posts)} 条")
            log(f"文件：{OUTPUT_DIR / 'linkedin_1hour_final.csv'}")
            log("=" * 70)
        else:
            log("\n⚠ 未采集到数据")
        
        context.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n用户中断")
    except Exception as e:
        log(f"\n✗ 错误：{e}")
        import traceback
        traceback.print_exc()
