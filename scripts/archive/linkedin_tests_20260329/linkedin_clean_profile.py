#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 采集 - 独立浏览器配置文件
不依赖日常 Chrome 的加密凭据
"""

import time
import sys
import io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

# Edge 浏览器数据目录
BROWSER_DATA_DIR = Path(r"C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile")
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - 独立浏览器配置")
    log(f"数据目录：{BROWSER_DATA_DIR}")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    # 创建数据目录
    BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    log(f"✓ 浏览器数据目录已准备")
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        log("\n启动浏览器...")
        
        try:
            # 启动独立的持久化浏览器上下文
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_DATA_DIR),
                headless=False,
                args=[
                    "--remote-debugging-port=9224",
                    "--disable-blink-features=AutomationControlled",
                ],
                timeout=90000
            )
            log("✓ 浏览器启动成功")
        except Exception as e:
            log(f"✗ 启动失败：{e}")
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
        
        # 如果没有，创建新页面并访问 LinkedIn
        if not linkedin_page:
            log("\n⚠ 未找到已登录的 LinkedIn")
            log("创建新页面...")
            linkedin_page = context.new_page()
            
            log("访问 LinkedIn 登录页...")
            linkedin_page.goto("https://www.linkedin.com/login", timeout=60000)
            
            log("\n" + "!" * 70)
            log("请在打开的浏览器中登录 LinkedIn")
            log("登录后将自动开始采集")
            log("!" * 70)
            
            # 等待登录（最多 5 分钟）
            logged_in = False
            for _ in range(30):
                time.sleep(10)
                try:
                    url = linkedin_page.url
                    if "linkedin.com/feed" in url.lower() and "login" not in url.lower():
                        log("✓ 检测到已登录!")
                        logged_in = True
                        break
                except:
                    pass
            
            if not logged_in:
                log("⚠ 等待登录超时，但继续尝试采集...")
        
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
            
            # 检查页面
            try:
                url = page.url
                if "linkedin.com" not in url.lower():
                    log(f"⚠ 页面跳转：{url[:60]}... 返回 LinkedIn")
                    page.goto("https://www.linkedin.com/feed/", timeout=30000)
                    time.sleep(3)
            except:
                pass
            
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
        log("浏览器已关闭")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n用户中断")
    except Exception as e:
        log(f"\n✗ 错误：{e}")
        import traceback
        traceback.print_exc()
