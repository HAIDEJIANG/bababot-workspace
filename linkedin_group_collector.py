#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Group Collection Script - 周一/周日专用
采集已加入的航空相关群组内容
"""

import sys
import csv
import os
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
CSV_PATH = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"
CDP_URL = "http://127.0.0.1:9222"  # webtop_local.py 使用的端口
COLLECTION_DURATION_MINUTES = 45
SCROLL_PAUSE = 3

# 重点关注的航空群组
TARGET_GROUPS = [
    "Aviation Trading Circle",
    "Arab Aviation",
    "Aircraft Parts & Engine Traders",
    "AIRCRAFT & ENGINE TRADERS PLATFORM",
    "Buyers and Sellers of Aircraft Spare Parts",
    "AIRCRAFT & ENGINE TRADE MARKETPLACE",
    "Aircraft Engine Exchange",
    "Aircraft & Engine Teardown",
    "Wet Lease & ACMI",
    "Aircraft Engine Sales",
    "V2500-A5 Engine Parts",
    "Business Aviation Network",
    "Aviation Week MRO",
    "International Aircraft Engine Association",
]

AVIATION_KEYWORDS = [
    'engine', 'cfm56', 'v2500', 'pw4000', 'ge90', 'trent', 'leap',
    'aircraft', 'boeing', 'airbus', 'b737', 'b747', 'b777', 'b787',
    'a320', 'a330', 'a350', 'a380', 'atr', 'embraer',
    'landing gear', 'gear', 'actuator',
    'part', 'component', 'spare', 'rotable', 'apu',
    'mro', 'maintenance', 'repair', 'overhaul', 'service',
    'sale', 'buy', 'wanted', 'available', 'lease', 'acmi'
]

def is_aviation_related(text):
    """检查内容是否与航空业务相关"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in AVIATION_KEYWORDS)

def extract_contact_info(content):
    """从内容中提取联系信息"""
    contacts = []
    # 提取邮箱
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    contacts.extend(emails)
    # 提取电话
    phones = re.findall(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{6,15}', content)
    contacts.extend(phones[:2])  # 最多取 2 个电话
    return '; '.join(contacts[:3])

def categorize_content(content):
    """对内容进行分类"""
    cl = content.lower()
    
    # 业务类型
    if any(k in cl for k in ['available', 'sell', 'offering', 'inventory', 'for sale']):
        business_type = '航材销售'
    elif any(k in cl for k in ['looking', 'requirement', 'need', 'buy', 'wanted']):
        business_type = '采购需求'
    elif any(k in cl for k in ['lease', 'acmi', 'charter']):
        business_type = '租赁服务'
    elif any(k in cl for k in ['mro', 'maintenance', 'repair', 'overhaul']):
        business_type = 'MRO 服务'
    elif any(k in cl for k in ['hiring', 'job', 'career', 'position']):
        business_type = '行业招聘'
    else:
        business_type = '行业新闻'
    
    # 业务价值
    if any(k in cl for k in ['urgent', 'asap', 'aog', '$', 'price']):
        business_value = '高'
    elif any(k in cl for k in ['available', 'stock', 'ready']):
        business_value = '高'
    else:
        business_value = '中'
    
    # 飞机/发动机类型
    aircraft = ''
    if 'cfm56' in cl: aircraft = 'CFM56'
    elif 'v2500' in cl: aircraft = 'V2500'
    elif 'b737' in cl or '737' in cl: aircraft = 'B737'
    elif 'a320' in cl: aircraft = 'A320'
    elif 'b777' in cl: aircraft = 'B777'
    elif 'b787' in cl: aircraft = 'B787'
    
    return business_type, business_value, aircraft

def save_post(data, group_name):
    """保存帖子到 CSV"""
    content = data.get('content', '')
    business_type, business_value, aircraft = categorize_content(content)
    contact_info = extract_contact_info(content)
    
    author = data.get('author', 'unknown')[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    post_id = f"linkedin_group_{timestamp}_{len(content) % 10000}"
    
    row = {
        'post_id': post_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author_name': author,
        'company': data.get('company', ''),
        'position': data.get('position', ''),
        'content': content[:2000],
        'business_type': business_type,
        'business_value_score': '9.0' if business_value == '高' else '7.0',
        'urgency': '高' if business_value == '高' else '中',
        'has_contact': 'True' if contact_info else 'False',
        'contact_info': contact_info,
        'post_time': data.get('post_time', 'recent'),
        'reactions': str(data.get('reactions', '0')),
        'comments': str(data.get('comments', '0')),
        'reposts': str(data.get('reposts', '0')),
        'has_image': '1.0' if data.get('has_image', False) else '0.0',
        'image_content': data.get('image_content', ''),
        'source_url': data.get('source_url', ''),
        'source_file': f'LinkedIn_Group_Collection_{datetime.now().strftime("%Y%m%d")}.csv',
        'merge_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'batch_id': f'batch_group_{datetime.now().strftime("%Y%m%d")}',
        'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author_url': data.get('author_url', ''),
        'posted_time': data.get('post_time', ''),
        'content_summary': content[:200] + '...' if len(content) > 200 else content,
        'is_repost': 'false',
        'original_author': '',
        'category': business_type,
        'aircraft_type': aircraft,
        'author_title': data.get('position', ''),
        'content_type': 'text',
        'tags': f'#LinkedIn #Group #{business_type.replace(" ", "")}',
        'author': author,
        'likes': data.get('reactions', '0'),
        'summary': content[:150],
        'part_numbers': '',
        'condition': '',
        'quantity': '',
        'certification': '',
        'part_number': '',
        'status': 'active',
        'notes': f'From group: {group_name}'
    }
    
    exists = os.path.exists(CSV_PATH)
    fields = list(row.keys())
    
    with open(CSV_PATH, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            w.writeheader()
        w.writerow(row)
    
    return row

def collect_group_posts(page, group_name, group_url, seen_posts):
    """Collect posts from a single group"""
    print(f"\nCollecting group: {group_name}")
    print(f"URL: {group_url}")
    
    collected = 0
    
    try:
        page.goto(group_url, wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        # Scroll to load more
        for i in range(5):
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(SCROLL_PAUSE)
        
        # Extract posts
        posts = page.evaluate('''() => {
            const posts = [];
            const articles = document.querySelectorAll('article, div[role="article"], .update-components-actor__container');
            
            articles.forEach(article => {
                try {
                    const authorElem = article.querySelector('a[href*="/in/"], a[href*="/company/"], .update-components-actor__name');
                    const contentElem = article.querySelector('span[aria-hidden="true"], div[class*="commentary"]');
                    const timeElem = article.querySelector('time, span[class*="date"]');
                    
                    if (contentElem && contentElem.textContent.trim().length > 50) {
                        posts.push({
                            author: authorElem ? authorElem.textContent.trim() : 'Unknown',
                            author_url: authorElem ? authorElem.href : '',
                            position: '',
                            company: '',
                            content: contentElem.textContent.trim(),
                            post_time: timeElem ? timeElem.textContent.trim() : 'recent',
                            source_url: window.location.href,
                            reactions: '0',
                            comments: '0',
                            reposts: '0',
                            has_image: article.querySelector('img') !== null,
                            image_content: ''
                        });
                    }
                } catch(e) {}
            });
            
            return posts;
        }''')
        
        for post in posts:
            key = f"{post['author']}_{post['content'][:100]}"
            if key not in seen_posts and is_aviation_related(post['content']):
                seen_posts.add(key)
                row = save_post(post, group_name)
                collected += 1
                print(f"  + {row['author'][:30]} | {row['business_type']} | {row['urgency']}")
        
        print(f"Group {group_name} complete: {collected} aviation posts")
        
    except Exception as e:
        print(f"Group {group_name} failed: {e}")
    
    return collected

def main():
    print("=" * 70)
    print("LinkedIn Group Collection Task - Monday/Sunday Special")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {COLLECTION_DURATION_MINUTES} min")
    print(f"Target: {CSV_PATH}")
    print("=" * 70)
    
    total_collected = 0
    seen_posts = set()
    start_time = time.time()
    end_time = start_time + (COLLECTION_DURATION_MINUTES * 60)
    
    try:
        with sync_playwright() as p:
            print(f"\nConnecting to CDP: {CDP_URL}")
            browser = p.chromium.connect_over_cdp(CDP_URL, timeout=30000)
            print("Connected!")
            
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            
            # Navigate to LinkedIn Groups
            print("\nAccessing LinkedIn Groups...")
            page.goto("https://www.linkedin.com/groups/", wait_until='networkidle', timeout=60000)
            time.sleep(5)
            
            # Extract joined groups list
            print("\nGetting joined groups list...")
            groups = page.evaluate('''() => {
                const groups = [];
                const items = document.querySelectorAll('a[href*="/groups/"]');
                items.forEach(item => {
                    const name = item.textContent.trim();
                    const url = item.href;
                    if (name && url && name.length > 5) {
                        groups.push({ name, url });
                    }
                });
                return groups.slice(0, 20);
            }''')
            
            print(f"Found {len(groups)} groups")
            
            # Collect from target groups first
            for group in groups:
                if time.time() > end_time:
                    print("\nTime limit reached")
                    break
                
                is_target = any(target.lower() in group['name'].lower() for target in TARGET_GROUPS)
                if is_target or len(groups) < 10:
                    collected = collect_group_posts(page, group['name'], group['url'], seen_posts)
                    total_collected += collected
                    time.sleep(2)
            
            browser.close()
            
    except Exception as e:
        print(f"\nError during collection: {e}")
        import traceback
        traceback.print_exc()
    
    elapsed = (time.time() - start_time) / 60
    print("\n" + "=" * 70)
    print("Collection Complete!")
    print(f"Total posts collected: {total_collected}")
    print(f"Elapsed: {elapsed:.1f} min")
    print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return total_collected

if __name__ == "__main__":
    main()
