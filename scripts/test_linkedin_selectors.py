#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 选择器测试脚本
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright

def test_selectors():
    with sync_playwright() as p:
        print("连接浏览器...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
        print("连接成功")
        
        context = browser.contexts[0]
        page = context.pages[0]
        
        print(f"当前 URL: {page.url}")
        
        # 尝试多种选择器并报告结果
        selectors = [
            '[class*="feed-shared-update-v2"]',
            '[class*="update-v2"]',
            'div[role="article"]',
            '[data-id*="urn:li:activity"]',
            'article',
            '.feed-shared-update-v2',
            '[class*="feed"]',
        ]
        
        for selector in selectors:
            try:
                elements = page.query_selector_all(selector)
                print(f"{selector}: {len(elements)} 个元素")
                if len(elements) > 0:
                    # 打印第一个元素的文本
                    text = elements[0].inner_text()[:200]
                    print(f"  示例文本：{text[:100]}...")
            except Exception as e:
                print(f"{selector}: 错误 - {e}")
        
        # 获取页面完整 HTML 中的类名
        print("\n页面中的类名（包含 feed 或 update）:")
        class_names = page.evaluate('''() => {
            var classes = {};
            var all = document.querySelectorAll('[class]');
            for (var i = 0; i < all.length; i++) {
                var cls = all[i].className;
                if (typeof cls === 'string' && (cls.indexOf('feed') >= 0 || cls.indexOf('update') >= 0 || cls.indexOf('post') >= 0)) {
                    classes[cls] = (classes[cls] || 0) + 1;
                }
            }
            return classes;
        }''')
        
        for cls, count in list(class_names.items())[:20]:
            print(f"  {cls}: {count} 次")

if __name__ == '__main__':
    test_selectors()
