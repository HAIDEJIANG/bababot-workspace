#!/usr/bin/env python3
"""调试 LinkedIn 页面结构 - 改进版"""
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(CDP_URL, timeout=30000)
    ctx = browser.contexts[0]
    page = ctx.pages[0]
    
    print(f"URL: {page.url}")
    
    # 使用更具体的选择器
    posts = page.evaluate('''() => {
        // 尝试不同的选择器
        const selectors = [
            'div.update-v2',
            'article',
            'div[role="article"]',
            'div.feed-update',
            'div.relative'
        ];
        
        const results = [];
        
        for (const sel of selectors) {
            const elems = document.querySelectorAll(sel);
            if (elems.length > 0) {
                console.log(`Selector ${sel}: ${elems.length} elements`);
            }
        }
        
        // 查找包含实际文本的帖子
        const articles = document.querySelectorAll('article');
        articles.forEach((a, i) => {
            if (i < 10) {
                // 尝试找到内容 span
                const spans = a.querySelectorAll('span[aria-hidden="false"], span.visually-hidden');
                let content = '';
                spans.forEach(s => {
                    if (s.textContent && s.textContent.trim().length > 20) {
                        content += s.textContent.trim() + ' ';
                    }
                });
                
                // 也尝试 div
                if (!content) {
                    const divs = a.querySelectorAll('div');
                    divs.forEach(d => {
                        if (d.textContent && d.textContent.trim().length > 50) {
                            content = d.textContent.trim().substring(0, 200);
                        }
                    });
                }
                
                // 查找作者
                const author = a.querySelector('a[href*="/in/"], a[href*="/company/"]');
                
                if (content && content.length > 30) {
                    results.push({
                        index: i,
                        author: author ? author.textContent.trim() : 'N/A',
                        content: content.substring(0, 150).replace(/\\n/g, ' '),
                        hasEmail: content.includes('@')
                    });
                }
            }
        });
        
        return results;
    }''')
    
    print(f"\nFound {len(posts)} posts with content:")
    for p in posts:
        print(f"  [{p['index']}] Author: {p['author'][:40]}")
        print(f"       Content: {p['content'][:100]}...")
        print(f"       Has Email: {p['hasEmail']}")
        print()
    
    browser.close()
