import json
import os
from datetime import datetime

# 批量新提取的帖子数据
new_posts_batch = [
    {
        "post_id": "linkedin_new_005",
        "author": "MRO Guangzhou",
        "company": "AMP Aero Services",
        "title": "MRO Guangzhou 2026 Exhibitor Confirmation",
        "content": "AMP Aero Services confirmed as exhibitor for MRO Guangzhou 2026. Headquartered in Miami with locations in Kansas City, New Delhi, Istanbul, and London.",
        "business_type": "MRO服务/展会",
        "contact_info": "https://www.linkedin.com/company/ampaeroservices/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/showcase/mro-guangzhou/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_006",
        "author": "Aleut Ventures",
        "company": "Aleut Ventures",
        "title": "Pacific Aviation Fueling Services",
        "content": "Cut flight time and costs. Make Cold Bay your Pacific refueling stop. Aviation Fueling & Services available at Cold Bay.",
        "business_type": "地面服务",
        "contact_info": "https://aleutventures.com/frosty-fuels/",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/aleut-ventures/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_007",
        "author": "LS Technics",
        "company": "LS Technics",
        "title": "Airbus A220 Part-145 Certificate Expansion",
        "content": "Expanded Part-145 certificate with new capabilities for Airbus A220 family. First MRO in Poland with such broad scope for A220, PW1500G and PW1900G engines.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/ls-technics/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/ls-technics/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_008",
        "author": "Leo Gutierrez",
        "company": "Southern Spares Services LLC",
        "title": "TFE731 SOAP KIT Part Available",
        "content": "TFE731 SOAP KIT Part Number 831044-1 available. Reliable support for aircraft operations. Visit www.southernsparesllc.com for TFE731 components.",
        "business_type": "航材供应",
        "contact_info": "www.southernsparesllc.com",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/southernsparesllc/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_009",
        "author": "Avia Solutions Group",
        "company": "AviaAM Leasing",
        "title": "Boeing 737-400BDSF Sale Completed",
        "content": "AviaAM Leasing successfully completed the sale of a Boeing 737-400BDSF to ECT Aviation Group. Aircraft delivered with CFM56-3C1 engine installed on-wing.",
        "business_type": "飞机整机买卖",
        "contact_info": "https://www.linkedin.com/company/aviaam-leasing/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/avia-solutions-group/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_010",
        "author": "GREAT Trade and Investment",
        "company": "UK Government",
        "title": "UK Clean Energy Investment Opportunities",
        "content": "UK powering clean energy future with £60bn invested. Major opportunities in hydrogen, offshore wind, and advanced nuclear. Not directly aviation but potential for aviation fuel transition.",
        "business_type": "投资/其他",
        "contact_info": "https://www.business.gov.uk/",
        "urgency": False,
        "business_value_score": 2,
        "source_url": "https://www.linkedin.com/showcase/greattrade/posts",
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
for post in new_posts_batch:
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
