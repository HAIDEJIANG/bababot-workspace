#!/usr/bin/env python3
"""
LinkedIn Feed 简单采集脚本
使用 requests + BeautifulSoup 配合已登录的浏览器 cookie
"""

import csv
import os
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

# 配置
CSV_PATH = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"
LINKEDIN_URL = "https://www.linkedin.com/feed/"
COLLECTION_DURATION_MINUTES = 60

# 航空业务关键词
AVIATION_KEYWORDS = [
    'engine', 'cfm56', 'v2500', 'pw4000', 'ge90', 'trent', 'leap', 'cf34',
    'aircraft', 'boeing', 'airbus', 'b737', 'b747', 'b757', 'b767', 'b777', 'b787',
    'a320', 'a330', 'a340', 'a350', 'a380', 'atr', 'embraer',
    'landing gear', 'undercarriage', 'gear', 'actuator',
    'part', 'component', 'spare', 'rotable', 'consumable', 'material', 'avic', 'apu',
    'mro', 'maintenance', 'repair', 'overhaul', 'service', 'support'
]

def is_aviation_related(text):
    """检查文本是否与航空相关"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in AVIATION_KEYWORDS)

def extract_posts_from_page(page):
    """从当前页面提取帖子"""
    posts_data = []
    
    try:
        # 使用 JavaScript 提取帖子数据
        posts = page.evaluate('''() => {
            const articles = document.querySelectorAll('article[aria-label*="Feed post"], div[role="article"]');
            const posts = [];
            
            articles.forEach(article => {
                try {
                    // 提取作者
                    const authorLink = article.querySelector('a[href*="/in/"], a[href*="/company/"]');
                    const author = authorLink ? authorLink.textContent.trim() : '';
                    
                    // 提取内容
                    const contentSpans = article.querySelectorAll('span[aria-hidden="false"]');
                    let content = '';
                    contentSpans.forEach(span => {
                        content += span.textContent + ' ';
                    });
                    content = content.trim();
                    
                    // 提取链接
                    const postLink = article.querySelector('a[href*="/posts/"], a[href*="/feed/"]');
                    const sourceUrl = postLink ? postLink.href : window.location.href;
                    
                    // 提取时间
                    const timeElem = article.querySelector('time, span[aria-label*="minutes"], span[aria-label*="hours"]');
                    const postDate = timeElem ? (timeElem.dateTime || timeElem.textContent) : new Date().toISOString();
                    
                    if (content && content.length > 50) {
                        posts.push({
                            author: author,
                            content: content,
                            sourceUrl: sourceUrl,
                            postDate: postDate
                        });
                    }
                } catch (e) {
                    console.error('Error extracting post:', e);
                }
            });
            
            return posts;
        }''')
        
        return posts
    except Exception as e:
        print(f"提取帖子时出错：{e}")
        return []

def categorize_post(content):
    """分类帖子"""
    content_lower = content.lower()
    
    # 类别
    if any(kw in content_lower for kw in ['engine', 'cfm56', 'v2500', 'pw4000', 'ge90', 'trent', 'leap']):
        category = 'engine'
    elif any(kw in content_lower for kw in ['landing gear', 'undercarriage', 'gear', 'actuator']):
        category = 'landing_gear'
    elif any(kw in content_lower for kw in ['mro', 'maintenance', 'repair', 'overhaul']):
        category = 'mro'
    elif any(kw in content_lower for kw in ['aircraft', 'boeing', 'airbus', 'b737', 'a320', 'atr']):
        category = 'aircraft'
    else:
        category = 'parts'
    
    # 业务类型
    if any(kw in content_lower for kw in ['available', 'supply', 'sell', 'offering', 'present', 'inventory', 'stock']):
        business_type = 'supply'
    elif any(kw in content_lower for kw in ['looking', 'requirement', 'need', 'request', 'seeking', 'wanted', 'buy']):
        business_type = 'demand'
    else:
        business_type = 'service'
    
    # 业务价值
    business_value = 'high' if any(kw in content_lower for kw in ['urgent', 'immediately', 'asap', '€', '$']) else 'medium'
    
    return category, business_type, business_value

def save_post(post_data, csv_path):
    """保存帖子到 CSV"""
    content = post_data['content']
    category, business_type, business_value = categorize_post(content)
    
    # 提取联系信息
    contact_info = ''
    if '@' in content:
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        contact_info = '; '.join(emails)
    
    # 生成 ID
    author_clean = post_data['author'].lower().replace(' ', '_').replace(',', '')[:30]
    post_id = f"{author_clean}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    row = {
        'post_id': post_id,
        'post_date': post_data['postDate'][:10] if post_data['postDate'] else datetime.now().strftime('%Y-%m-%d'),
        'author': post_data['author'],
        'author_title': '',
        'company': '',
        'category': category,
        'business_type': business_type,
        'business_value': business_value,
        'content': content[:500],
        'content_summary': content[:200] + '...' if len(content) > 200 else content,
        'contact_info': contact_info,
        'source_url': post_data['sourceUrl'],
        'collection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'verified': True,
        'notes': ''
    }
    
    file_exists = os.path.exists(csv_path)
    fieldnames = ['post_id', 'post_date', 'author', 'author_title', 'company', 
                  'category', 'business_type', 'business_value', 'content', 
                  'content_summary', 'contact_info', 'source_url', 
                  'collection_date', 'verified', 'notes']
    
    with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    
    return row

def main():
    print("=" * 60)
    print("LinkedIn Feed 信息采集任务")
    print("=" * 60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标时长：{COLLECTION_DURATION_MINUTES} 分钟")
    print(f"保存路径：{CSV_PATH}")
    print("=" * 60)
    
    collected_count = 0
    seen_posts = set()
    start_time = time.time()
    end_time = start_time + (COLLECTION_DURATION_MINUTES * 60)
    scroll_count = 0
    
    with sync_playwright() as p:
        # 连接到已存在的浏览器
        try:
            browser = p.chromium.connect_over_cdp(
                "http://127.0.0.1:18800",
                timeout=30000
            )
            print("[OK] 成功连接到浏览器")
        except Exception as e:
            print(f"[ERROR] 连接浏览器失败：{e}")
            print("尝试启动新浏览器实例...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir="C:\\Users\\Haide\\.openclaw\\browser\\openclaw\\user-data",
                headless=False
            )
        
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        
        # 导航到 LinkedIn
        print("正在访问 LinkedIn Feed...")
        try:
            page.goto(LINKEDIN_URL, wait_until='networkidle', timeout=60000)
            time.sleep(5)
            print("[OK] 页面加载完成")
        except Exception as e:
            print(f"页面加载出错：{e}")
        
        print("\n开始采集航空业务相关帖子...")
        print("-" * 60)
        
        while time.time() < end_time:
            try:
                # 提取帖子
                posts = extract_posts_from_page(page)
                new_count = 0
                
                for post in posts:
                    # 创建唯一标识
                    post_key = f"{post['author']}_{post['content'][:100]}"
                    
                    if post_key not in seen_posts and is_aviation_related(post['content']):
                        seen_posts.add(post_key)
                        row = save_post(post, CSV_PATH)
                        collected_count += 1
                        new_count += 1
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] {row['author'][:30]} | {row['category']} | {row['business_type']}")
                
                if new_count > 0:
                    print(f"  → 本次新增 {new_count} 条，累计 {collected_count} 条")
                
                # 向下滚动
                current_height = page.evaluate("document.body.scrollHeight")
                page.evaluate(f"window.scrollTo(0, {current_height})")
                scroll_count += 1
                
                elapsed_min = (time.time() - start_time) / 60
                print(f"  → 滚动 #{scroll_count} | 运行 {elapsed_min:.1f}/{COLLECTION_DURATION_MINUTES} 分钟 | 共 {collected_count} 条")
                print("-" * 60)
                
                # 等待加载
                time.sleep(4)
                
            except Exception as e:
                print(f"采集出错：{e}")
                time.sleep(5)
        
        browser.close()
    
    elapsed_total = (time.time() - start_time) / 60
    print("\n" + "=" * 60)
    print("采集任务完成!")
    print("=" * 60)
    print(f"总运行时间：{elapsed_total:.1f} 分钟")
    print(f"采集帖子数：{collected_count}")
    print(f"保存路径：{CSV_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()
