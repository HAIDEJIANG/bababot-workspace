#!/usr/bin/env python3
"""
LinkedIn Feed 采集脚本 - 简化版
"""

import csv
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

CSV_PATH = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"
LINKEDIN_URL = "https://www.linkedin.com/feed/"
COLLECTION_DURATION_MINUTES = 60
CDP_URL = "http://127.0.0.1:18800"

AVIATION_KEYWORDS = [
    'engine', 'cfm56', 'v2500', 'pw4000', 'ge90', 'trent', 'leap',
    'aircraft', 'boeing', 'airbus', 'b737', 'b747', 'b777', 'b787',
    'a320', 'a330', 'a350', 'a380', 'atr', 'embraer',
    'landing gear', 'gear', 'actuator',
    'part', 'component', 'spare', 'rotable', 'apu',
    'mro', 'maintenance', 'repair', 'overhaul', 'service'
]

def is_aviation_related(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in AVIATION_KEYWORDS)

def categorize(content):
    cl = content.lower()
    if any(k in cl for k in ['engine', 'cfm56', 'v2500']): cat = 'engine'
    elif any(k in cl for k in ['landing gear', 'actuator']): cat = 'landing_gear'
    elif any(k in cl for k in ['mro', 'maintenance', 'repair']): cat = 'mro'
    elif any(k in cl for k in ['aircraft', 'boeing', 'airbus', 'b737', 'a320']): cat = 'aircraft'
    else: cat = 'parts'
    
    if any(k in cl for k in ['available', 'sell', 'offering', 'inventory']): bt = 'supply'
    elif any(k in cl for k in ['looking', 'requirement', 'need', 'buy']): bt = 'demand'
    else: bt = 'service'
    
    bv = 'high' if any(k in cl for k in ['urgent', 'asap', '$']) else 'medium'
    return cat, bt, bv

def save(data):
    content = data.get('content', '')
    cat, bt, bv = categorize(content)
    
    contact = ''
    if '@' in content:
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        contact = '; '.join(emails)
    
    author = data.get('author', 'unknown')[:30].lower().replace(' ', '_')
    pid = f"{author}_{cat}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    row = {
        'post_id': pid,
        'post_date': data.get('postDate', datetime.now().strftime('%Y-%m-%d'))[:10],
        'author': data.get('author', ''),
        'author_title': '',
        'company': '',
        'category': cat,
        'business_type': bt,
        'business_value': bv,
        'content': content[:500],
        'content_summary': content[:200] + '...' if len(content) > 200 else content,
        'contact_info': contact,
        'source_url': data.get('sourceUrl', LINKEDIN_URL),
        'collection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'verified': True,
        'notes': ''
    }
    
    exists = os.path.exists(CSV_PATH)
    fields = ['post_id', 'post_date', 'author', 'author_title', 'company', 
              'category', 'business_type', 'business_value', 'content', 
              'content_summary', 'contact_info', 'source_url', 
              'collection_date', 'verified', 'notes']
    
    with open(CSV_PATH, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if not exists: w.writeheader()
        w.writerow(row)
    return row

def main():
    print("=" * 60)
    print("LinkedIn Feed Collection Task")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {COLLECTION_DURATION_MINUTES} min")
    print(f"Target: {CSV_PATH}")
    print("=" * 60)
    
    count = 0
    seen = set()
    start = time.time()
    end = start + (COLLECTION_DURATION_MINUTES * 60)
    scrolls = 0
    
    with sync_playwright() as p:
        print(f"Connecting to {CDP_URL}...")
        browser = p.chromium.connect_over_cdp(CDP_URL, timeout=30000)
        print("Connected!")
        
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        
        # Navigate if needed
        if 'linkedin' not in page.url.lower():
            print("Navigating to LinkedIn...")
            page.goto(LINKEDIN_URL, wait_until='networkidle', timeout=60000)
            time.sleep(5)
        print(f"Current URL: {page.url}")
        
        print("Starting collection...")
        
        while time.time() < end:
            try:
                posts = page.evaluate('''() => {
                    const articles = document.querySelectorAll('article[aria-label*="Feed post"], div[role="article"]');
                    const posts = [];
                    articles.forEach(a => {
                        try {
                            const author = a.querySelector('a[href*="/in/"], a[href*="/company/"]');
                            const content = a.querySelector('span[aria-hidden="false"]');
                            const link = a.querySelector('a[href*="/posts/"]');
                            if (content && content.textContent.length > 50) {
                                posts.push({
                                    author: author ? author.textContent.trim() : '',
                                    content: content.textContent.trim(),
                                    sourceUrl: link ? link.href : window.location.href,
                                    postDate: new Date().toISOString()
                                });
                            }
                        } catch(e) {}
                    });
                    return posts;
                }''')
                
                new_count = 0
                for post in posts:
                    key = f"{post['author']}_{post['content'][:100]}"
                    if key not in seen and is_aviation_related(post['content']):
                        seen.add(key)
                        row = save(post)
                        count += 1
                        new_count += 1
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] + {row['author'][:20]} | {row['category']} | {row['business_type']}")
                
                if new_count:
                    print(f"  -> New: {new_count}, Total: {count}")
                
                # Scroll
                h = page.evaluate("document.body.scrollHeight")
                page.evaluate(f"window.scrollTo(0, {h})")
                scrolls += 1
                
                elapsed = (time.time() - start) / 60
                print(f"  -> Scroll #{scrolls} | {elapsed:.1f}/{COLLECTION_DURATION_MINUTES} min | {count} posts")
                print("-" * 60)
                
                time.sleep(4)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        
        browser.close()
    
    total = (time.time() - start) / 60
    print("=" * 60)
    print("DONE!")
    print(f"Total time: {total:.1f} min")
    print(f"Posts collected: {count}")
    print(f"Saved to: {CSV_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()
