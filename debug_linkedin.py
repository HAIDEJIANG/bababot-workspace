#!/usr/bin/env python3
"""调试 LinkedIn 页面结构"""
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(CDP_URL, timeout=30000)
    ctx = browser.contexts[0]
    page = ctx.pages[0]
    
    print(f"URL: {page.url}")
    
    # 检查页面元素
    articles = page.query_selector_all('article')
    print(f"Found {len(articles)} article elements")
    
    # 检查 aria-label
    feed_posts = page.query_selector_all('[aria-label*="Feed post"]')
    print(f"Found {len(feed_posts)} feed post elements")
    
    # 检查 role=article
    role_articles = page.query_selector_all('[role="article"]')
    print(f"Found {len(role_articles)} role=article elements")
    
    # 提取一些内容调试
    posts = page.evaluate('''() => {
        const all = document.querySelectorAll('article, div[role="article"]');
        const results = [];
        all.forEach((a, i) => {
            if (i < 5) {
                const text = a.textContent.substring(0, 200);
                const aria = a.getAttribute('aria-label');
                results.push({
                    index: i,
                    ariaLabel: aria,
                    textPreview: text.replace(/\\n/g, ' ')
                });
            }
        });
        return results;
    }''')
    
    print("\nFirst 5 posts:")
    for p in posts:
        print(f"  [{p['index']}] aria='{p['ariaLabel']}'")
        print(f"       text='{p['textPreview'][:100]}...'")
    
    browser.close()
