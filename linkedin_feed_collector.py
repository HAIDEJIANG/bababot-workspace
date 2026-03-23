#!/usr/bin/env python3
"""
LinkedIn Feed 信息采集脚本
持续采集航空业务相关帖子（发动机、飞机、起落架、航材、MRO）
"""

import csv
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# 配置
CSV_PATH = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"
LINKEDIN_URL = "https://www.linkedin.com/feed/"
COLLECTION_DURATION_MINUTES = 60
SCROLL_PAUSE_SECONDS = 3

# 航空业务关键词
AVIATION_KEYWORDS = {
    'engine': ['engine', 'cfm56', 'v2500', 'pw4000', 'ge90', 'trent', 'leap', 'cf34', 'ctp', 'accessory', 'gearbox'],
    'aircraft': ['aircraft', 'boeing', 'airbus', 'b737', 'b747', 'b757', 'b767', 'b777', 'b787', 'a320', 'a330', 'a340', 'a350', 'a380', 'atr', 'embraer', 'bombardier'],
    'landing_gear': ['landing gear', 'undercarriage', 'gear', 'actuator', 'wheel', 'brake'],
    'parts': ['part', 'component', 'spare', 'rotable', 'consumable', 'material', 'avic', 'apu', 'pump', 'valve', 'sensor'],
    'mro': ['mro', 'maintenance', 'repair', 'overhaul', 'service', 'support', 'modification', 'sb', 'ad', 'airworthiness']
}

# 业务类型关键词
SUPPLY_KEYWORDS = ['available', 'supply', 'sell', 'offering', 'present', 'inventory', 'stock', 'for sale']
DEMAND_KEYWORDS = ['looking', 'requirement', 'need', 'request', 'seeking', 'wanted', 'buy', 'purchase']
SERVICE_KEYWORDS = ['service', 'support', 'repair', 'maintenance', 'overhaul', 'engineering', 'consulting']

def categorize_post(content):
    """根据内容分类帖子"""
    content_lower = content.lower()
    
    # 确定类别
    category = 'parts'  # 默认
    max_matches = 0
    for cat, keywords in AVIATION_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in content_lower)
        if matches > max_matches:
            max_matches = matches
            category = cat
    
    # 确定业务类型
    business_type = 'service'  # 默认
    supply_matches = sum(1 for kw in SUPPLY_KEYWORDS if kw in content_lower)
    demand_matches = sum(1 for kw in DEMAND_KEYWORDS if kw in content_lower)
    service_matches = sum(1 for kw in SERVICE_KEYWORDS if kw in content_lower)
    
    if supply_matches > demand_matches and supply_matches >= service_matches:
        business_type = 'supply'
    elif demand_matches > supply_matches and demand_matches >= service_matches:
        business_type = 'demand'
    
    # 确定业务价值
    business_value = 'medium'
    if any(kw in content_lower for kw in ['urgent', 'immediately', 'asap', '€', '$', 'price', 'buy', 'sell']):
        business_value = 'high'
    
    return category, business_type, business_value

def extract_post_data(element):
    """从帖子元素提取数据"""
    try:
        # 提取作者信息
        author_elem = element.query_selector('a[href*="/in/"], a[href*="/company/"]')
        author = author_elem.inner_text() if author_elem else 'Unknown'
        
        # 提取作者职位
        author_title_elem = element.query_selector('div[aria-label*="followers"] + div, span:has-text("•")')
        author_title = author_title_elem.inner_text() if author_title_elem else ''
        
        # 提取公司
        company_elem = element.query_selector('a[href*="/company/"]')
        company = company_elem.inner_text() if company_elem else ''
        
        # 提取帖子内容
        content_elem = element.query_selector('div[aria-label*="Feed post"] div span[aria-hidden="false"]')
        content = content_elem.inner_text() if content_elem else ''
        
        # 提取时间
        time_elem = element.query_selector('time, span:has-text("min"), span:has-text("hr"), span:has-text("d")')
        post_date = time_elem.get_attribute('datetime') if time_elem else datetime.now().strftime('%Y-%m-%d')
        
        # 提取链接
        link_elem = element.query_selector('a[href*="/posts/"], a[href*="/feed/"]')
        source_url = link_elem.get_attribute('href') if link_elem else LINKEDIN_URL
        
        # 提取联系方式
        contact_info = ''
        if '@' in content:
            import re
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
            contact_info = '; '.join(emails)
        
        # 分类
        category, business_type, business_value = categorize_post(content)
        
        # 生成 ID
        post_id = f"{author.lower().replace(' ', '_')}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            'post_id': post_id,
            'post_date': post_date,
            'author': author,
            'author_title': author_title,
            'company': company,
            'category': category,
            'business_type': business_type,
            'business_value': business_value,
            'content': content[:500] if content else '',  # 限制长度
            'content_summary': content[:200] + '...' if len(content) > 200 else content,
            'contact_info': contact_info,
            'source_url': source_url,
            'collection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'verified': True,
            'notes': ''
        }
    except Exception as e:
        print(f"Error extracting post: {e}")
        return None

def save_to_csv(data, csv_path):
    """保存数据到 CSV"""
    file_exists = os.path.exists(csv_path)
    
    fieldnames = ['post_id', 'post_date', 'author', 'author_title', 'company', 
                  'category', 'business_type', 'business_value', 'content', 
                  'content_summary', 'contact_info', 'source_url', 
                  'collection_date', 'verified', 'notes']
    
    with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def is_aviation_related(content):
    """检查帖子是否与航空业务相关"""
    content_lower = content.lower()
    all_keywords = []
    for keywords in AVIATION_KEYWORDS.values():
        all_keywords.extend(keywords)
    
    return any(kw in content_lower for kw in all_keywords)

def main():
    print(f"开始 LinkedIn Feed 采集任务")
    print(f"目标：采集至少 {COLLECTION_DURATION_MINUTES} 分钟")
    print(f"保存路径：{CSV_PATH}")
    print("-" * 60)
    
    collected_count = 0
    start_time = time.time()
    end_time = start_time + (COLLECTION_DURATION_MINUTES * 60)
    
    with sync_playwright() as p:
        # 使用现有的浏览器配置
        browser = p.chromium.launch_persistent_context(
            user_data_dir="C:\\Users\\Haide\\.openclaw\\browser\\openclaw\\user-data",
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # 导航到 LinkedIn Feed
        print("正在访问 LinkedIn Feed...")
        page.goto(LINKEDIN_URL, wait_until='networkidle', timeout=60000)
        time.sleep(5)  # 等待页面加载
        
        print("开始采集...")
        
        last_height = 0
        scroll_count = 0
        
        while time.time() < end_time:
            try:
                # 获取当前页面高度
                new_height = page.evaluate("document.body.scrollHeight")
                
                # 提取帖子
                posts = page.query_selector_all('article[aria-label*="Feed post"], div[role="article"]')
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 发现 {len(posts)} 个帖子元素")
                
                new_posts_count = 0
                for post in posts:
                    try:
                        content_elem = post.query_selector('div[aria-label*="Feed post"] span[aria-hidden="false"]')
                        if not content_elem:
                            content_elem = post.query_selector('span[aria-hidden="false"]')
                        
                        if content_elem:
                            content = content_elem.inner_text()
                            
                            # 检查是否与航空相关
                            if is_aviation_related(content):
                                data = extract_post_data(post)
                                if data and data['post_id']:
                                    save_to_csv(data, CSV_PATH)
                                    collected_count += 1
                                    new_posts_count += 1
                                    print(f"  ✓ 采集：{data['author']} - {data['category']} ({data['business_type']})")
                    except Exception as e:
                        print(f"  处理帖子时出错：{e}")
                        continue
                
                # 向下滚动
                if new_height > last_height:
                    page.evaluate(f"window.scrollTo(0, {new_height})")
                    scroll_count += 1
                    print(f"  滚动 #{scroll_count}，已采集 {collected_count} 条记录")
                    last_height = new_height
                    time.sleep(SCROLL_PAUSE_SECONDS)
                else:
                    print("  已到达底部，等待新内容加载...")
                    time.sleep(10)
                    last_height = 0  # 重置以重新检查
                
                # 检查时间
                elapsed = (time.time() - start_time) / 60
                print(f"  已运行 {elapsed:.1f}/{COLLECTION_DURATION_MINUTES} 分钟")
                
            except Exception as e:
                print(f"采集循环出错：{e}")
                time.sleep(5)
        
        browser.close()
    
    print("-" * 60)
    print(f"采集完成！")
    print(f"总采集时间：{(time.time() - start_time) / 60:.1f} 分钟")
    print(f"采集帖子数：{collected_count}")
    print(f"保存路径：{CSV_PATH}")

if __name__ == "__main__":
    main()
