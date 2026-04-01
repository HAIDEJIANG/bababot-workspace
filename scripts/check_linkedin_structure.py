#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    # 连接到现有浏览器（9222 端口）
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    
    # 获取所有页面
    pages = browser.contexts[0].pages if browser.contexts else []
    if not pages:
        pages = [browser.new_page()]
    
    page = pages[0]
    
    # 导航到 LinkedIn Feed
    print("导航到 LinkedIn Feed...")
    page.goto("https://www.linkedin.com/feed/", timeout=60000)
    time.sleep(5)
    
    # 检查页面内容
    print("\n=== 检查页面结构 ===")
    
    # 方法 1: 查找所有 article 标签
    articles = page.query_selector_all("article")
    print(f"article 标签数量：{len(articles)}")
    
    # 方法 2: 查找所有 div[role="article"]
    role_articles = page.query_selector_all('div[role="article"]')
    print(f'div[role="article"] 数量：{len(role_articles)}')
    
    # 方法 3: 查找所有包含文本的元素
    all_text = page.evaluate("document.body.innerText")
    print(f"\n页面文本长度：{len(all_text)}")
    print(f"前 500 字符:\n{all_text[:500]}")
    
    # 方法 4: 使用 XPath 查找帖子
    xpath_posts = page.query_selector_all("//div[contains(@class, 'update-v2')]")
    print(f"\nXPath 查找 update-v2: {len(xpath_posts)}")
    
    # 方法 5: 查找所有有 href="/in/"的元素（发帖人链接）
    author_links = page.query_selector_all('a[href*="/in/"]')
    print(f"\n发帖人链接数量：{len(author_links)}")
    for i, link in enumerate(author_links[:5]):
        text = link.inner_text()
        print(f"  [{i+1}] {text}")
    
    # 方法 6: 获取页面所有类名包含"feed"的元素
    feed_elements = page.query_selector_all('[class*="feed"]')
    print(f"\n类名包含 feed 的元素：{len(feed_elements)}")
    
    browser.close()
    print("\n检查完成")
