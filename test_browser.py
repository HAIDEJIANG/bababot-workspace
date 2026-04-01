#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

p = sync_playwright().start()
b = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
c = b.contexts[0]
pg = c.pages[0] if c.pages else c.new_page()
print('Current URL:', pg.url)
print('Title:', pg.title())
b.close()
