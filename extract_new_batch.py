import json
import os
from datetime import datetime

# 新提取的帖子数据 (从快照中提取)
new_posts = [
    {
        "post_id": "linkedin_new_001",
        "author": "Leo Gutierrez",
        "company": "Southern Spares Services LLC",
        "title": "TFE731 SOAP KIT Available",
        "content": "TFE731 SOAP KIT Part Number 831044-1. Reliable support starts with having the right parts available at the right time. Visit www.southernsparesllc.com",
        "business_type": "航材供应",
        "contact_info": "www.southernsparesllc.com",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/southernsparesllc/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_002",
        "author": "LS Technics",
        "company": "LS Technics",
        "title": "Airbus A220 Part-145 Certificate Expansion",
        "content": "Expanded Part-145 certificate with new capabilities for Airbus A220 family with PW1500G and PW1900G engines. First MRO in Poland with such broad scope.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/ls-technics/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/ls-technics/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_003",
        "author": "AMP Aero Services",
        "company": "AMP Aero Services",
        "title": "MRO Guangzhou 2026 Exhibitor",
        "content": "AMP Aero Services confirmed as exhibitor for MRO Guangzhou 2026. Headquartered in Miami with locations in Kansas City, New Delhi, Istanbul, and London.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/ampaeroservices/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/showcase/mro-guangzhou/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_004",
        "author": "Aleut Ventures",
        "company": "Aleut Ventures",
        "title": "Aviation Fueling & Services - Cold Bay",
        "content": "Cut flight time and costs. Make Cold Bay your Pacific refueling stop. Aviation Fueling & Services available.",
        "business_type": "地面服务",
        "contact_info": "https://aleutventures.com/frosty-fuels/",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/aleut-ventures/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

# 读取现有数据
json_path = os.path.expanduser('~/Desktop/real business post/linkedin_real_business_posts.json')
with open(json_path, 'r', encoding='utf-8') as f:
    existing_data = json.load(f)

# 合并数据
existing_ids = {p['post_id'] for p in existing_data['posts']}
added_count = 0
for post in new_posts:
    if post['post_id'] not in existing_ids:
        existing_data['posts'].append(post)
        added_count += 1

# 更新元数据
existing_data['metadata']['total_collected'] = len(existing_data['posts'])
existing_data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 保存
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=2)

total = len(existing_data['posts'])
print(f'Added {added_count} new posts')
print(f'Total posts: {total}')
print(f'Target: 150')
print(f'Remaining: {max(0, 150 - total)}')
