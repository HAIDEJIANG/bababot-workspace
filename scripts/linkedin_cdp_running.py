#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 采集 - CDP 连接已运行的浏览器
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
CDP_PORT = 9224

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - CDP 连接已运行浏览器")
    log(f"CDP 端口：{CDP_PORT}")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        log("\n连接浏览器...")
        try:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}", timeout=30000)
            log("✓ 连接成功")
        except Exception as e:
            log(f"✗ 连接失败：{e}")
            log(f"请确保浏览器已启动（端口 {CDP_PORT}）")
            return
        
        # 获取所有页面
        contexts = browser.contexts
        log(f"找到 {len(contexts)} 个上下文")
        
        linkedin_page = None
        
        for ctx_idx, ctx in enumerate(contexts):
            try:
                pages = ctx.pages
                log(f"  上下文 {ctx_idx}: {len(pages)} 个页面")
                for page_idx, page in enumerate(pages):
                    try:
                        url = page.url
                        log(f"    页面 {page_idx+1}: {url[:70]}...")
                        if "linkedin.com/feed" in url.lower() and "login" not in url.lower():
                            linkedin_page = page
                            log("    ✓ 找到已登录的 LinkedIn!")
                    except Exception as e:
                        log(f"    页面检查失败：{e}")
            except Exception as e:
                log(f"  上下文 {ctx_idx} 检查失败：{e}")
        
        if not linkedin_page:
            log("\n未找到 LinkedIn Feed 页面")
            # 创建新页面
            for ctx in contexts:
                try:
                    linkedin_page = ctx.new_page()
                    break
                except:
                    pass
            
            if linkedin_page:
                log("访问 LinkedIn...")
                linkedin_page.goto("https://www.linkedin.com/feed/", timeout=60000)
                log("请确认已登录 LinkedIn")
                time.sleep(5)
        
        if not linkedin_page:
            log("✗ 无法获取页面，结束")
            browser.close()
            return
        
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
        
        browser.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n用户中断")
    except Exception as e:
        log(f"\n✗ 错误：{e}")
        import traceback
        traceback.print_exc()
