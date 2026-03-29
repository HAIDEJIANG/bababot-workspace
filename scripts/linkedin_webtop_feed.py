#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 采集 - 连接 WebTop 持久化浏览器
恢复原版稳定方案
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

# WebTop 浏览器配置
WEBTOP_USER_DATA = r"C:\Users\Haide\AppData\Local\Google\Chrome\User Data"
CDP_ENDPOINT = "http://localhost:9222"

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - WebTop 持久化浏览器")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        # 连接 WebTop 持久化浏览器
        log(f"连接 Chrome (CDP: {CDP_ENDPOINT})...")
        try:
            browser = p.chromium.connect_over_cdp(CDP_ENDPOINT, timeout=30000)
            log("✓ 连接成功")
        except Exception as e:
            log(f"✗ CDP 连接失败：{e}")
            log("\n请确保 WebTop 浏览器已启动:")
            log("  python scripts/webtop/webtop_local.py --start")
            return
        
        # 获取所有上下文和页面
        contexts = browser.contexts
        log(f"找到 {len(contexts)} 个浏览器上下文")
        
        linkedin_page = None
        
        # 查找已有的 LinkedIn Feed 页面
        for ctx_idx, ctx in enumerate(contexts):
            try:
                pages = ctx.pages
                log(f"  上下文 {ctx_idx}: {len(pages)} 个页面")
                for page_idx, page in enumerate(pages):
                    try:
                        url = page.url
                        log(f"    页面 {page_idx}: {url[:70]}...")
                        if "linkedin.com/feed" in url.lower() and "login" not in url.lower():
                            linkedin_page = page
                            log(f"    ✓ 找到已登录的 LinkedIn Feed 页面!")
                    except Exception as e:
                        log(f"    页面检查失败：{e}")
            except Exception as e:
                log(f"  上下文 {ctx_idx} 检查失败：{e}")
        
        # 如果没有找到，创建新页面并访问 LinkedIn
        if not linkedin_page:
            log("\n未找到已登录的 LinkedIn 页面")
            log("请在 Chrome 中访问 https://www.linkedin.com/feed/ 并登录")
            log("等待 60 秒...")
            
            # 创建新页面
            for ctx in contexts:
                try:
                    linkedin_page = ctx.new_page()
                    break
                except:
                    pass
            
            if linkedin_page:
                linkedin_page.goto("https://www.linkedin.com/login", timeout=60000)
                time.sleep(60)
                
                # 再次检查
                for ctx in contexts:
                    for page in ctx.pages:
                        try:
                            url = page.url
                            if "linkedin.com/feed" in url.lower() and "login" not in url.lower():
                                linkedin_page = page
                                log("✓ 检测到 LinkedIn Feed 页面")
                                break
                        except:
                            pass
        
        if not linkedin_page:
            log("✗ 无法获取 LinkedIn 页面，结束")
            browser.close()
            return
        
        page = linkedin_page
        page.bring_to_front()
        
        try:
            current_url = page.url
            log(f"\n当前页面：{current_url}")
        except:
            log("\n当前页面：LinkedIn")
        
        log("开始采集，目标 60 分钟...")
        log("-" * 70)
        
        batch_num = 0
        
        while (datetime.now() - start_time).total_seconds() < 60 * 60:
            batch_num += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            
            # 检查页面状态
            try:
                url = page.url
                if "linkedin.com" not in url.lower() or "login" in url.lower():
                    log(f"⚠ 页面跳转：{url[:60]}...")
            except:
                log("⚠ 页面状态检查失败")
            
            log(f"\n【批次 {batch_num}】{elapsed:.1f} 分钟")
            
            # 滚动页面触发更多内容
            for i in range(3):
                try:
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(2)
                except Exception as e:
                    log(f"  滚动失败：{e}")
            
            # 提取帖子内容
            try:
                posts_data = page.evaluate('''() => {
                    const results = [];
                    // LinkedIn 帖子选择器
                    const selectors = [
                        '[data-id*="urn:li:activity"]',
                        '[data-id*="urn:li:share"]',
                        'div[class*="updateContent"]',
                        'article[class*="post"]',
                        'div[aria-label*="post"]'
                    ];
                    
                    selectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(function(el) {
                            try {
                                const text = el.innerText;
                                if (text && text.length > 100 && text.length < 2000) {
                                    results.push(text);
                                }
                            } catch(e) {}
                        });
                    });
                    
                    return results;
                }''')
                
                new_count = 0
                for post in posts_data:
                    h = hash(post)
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        all_posts.append({
                            "text": post,
                            "time": datetime.now().isoformat(),
                            "url": page.url
                        })
                        new_count += 1
                
                log(f"看到 {len(posts_data)} 个帖子，新增 {new_count} 个，总计 {len(all_posts)} 个")
                
                # 每 2 个批次保存一次
                if len(all_posts) > 0 and batch_num % 2 == 0:
                    with open(OUTPUT_DIR / "linkedin_1hour.csv", 'w', encoding='utf-8') as f:
                        f.write("timestamp,url,text\n")
                        for p in all_posts:
                            text_safe = p["text"].replace('"', '""').replace('\n', ' ')
                            f.write(f'"{p["time"]}","{p["url"]}","{text_safe}"\n')
                    log(f"✓ 已保存 {len(all_posts)} 条到 CSV")
                    
            except Exception as e:
                log(f"✗ 提取失败：{e}")
            
            # 等待
            time.sleep(30)
        
        # 最终保存
        if all_posts:
            with open(OUTPUT_DIR / "linkedin_1hour_final.csv", 'w', encoding='utf-8') as f:
                f.write("timestamp,url,text\n")
                for p in all_posts:
                    text_safe = p["text"].replace('"', '""').replace('\n', ' ')
                    f.write(f'"{p["time"]}","{p["url"]}","{text_safe}"\n')
            
            log("\n" + "=" * 70)
            log(f"✓ 采集完成！")
            log(f"  共采集 {len(all_posts)} 条帖子")
            log(f"  输出文件：{OUTPUT_DIR / 'linkedin_1hour_final.csv'}")
            log("=" * 70)
        else:
            log("\n⚠ 未采集到数据")
        
        browser.close()
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
