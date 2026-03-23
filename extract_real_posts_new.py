import json
import os
from datetime import datetime

# 从最新快照提取的真实帖子
new_real_posts = [
    {
        "post_id": "linkedin_real_114",
        "author": "Lidia Skoczen",
        "company": "PBES",
        "title": "New Role: Parts & Procurement Manager at PBES",
        "content": "Accepted the role of Parts & Procurement Manager at PBES. Leading components' sales and procurement strategy with focus on supporting business jet clients. Contact: LSkoczen@pbes.co.uk or Enquiries@pbes.co.uk. Website: www.pbes.co.uk",
        "business_type": "航材供应/招聘",
        "contact_info": "LSkoczen@pbes.co.uk, Enquiries@pbes.co.uk, www.pbes.co.uk",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/lidia-skoczen/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_115",
        "author": "LS Technics",
        "company": "LS Technics",
        "title": "Part-145 Certificate Expansion for Airbus A220",
        "content": "Expanded Part-145 certificate with new capabilities for Airbus A220 family with PW1500G and PW1900G engines. First MRO in Poland with such broad scope. Over 1,000 specialists across eight airports in Poland.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/ls-technics/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/ls-technics/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_116",
        "author": "MRO Guangzhou",
        "company": "MRO Guangzhou",
        "title": "AMP Aero Services Confirmed Exhibitor 2026",
        "content": "AMP Aero Services confirmed as exhibitor for MRO Guangzhou 2026. Headquartered in Miami with locations in Kansas City, New Delhi, Istanbul, and London. March 24-26, 2026. Register: mrosummitchina.com",
        "business_type": "MRO服务/展会",
        "contact_info": "mrosummitchina.com",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/showcase/mro-guangzhou/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_117",
        "author": "Nico von Appen",
        "company": "VA Aviation Ltd",
        "title": "DAE Capital Acquisition News",
        "content": "DAE Capital nears deal to buy aircraft leasing firm Macquarie Airfinance. Source: Reuters.",
        "business_type": "飞机租赁/投资",
        "contact_info": "LinkedIn contact",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.reuters.com/business/aerospace-defense/dae-capital-nears-deal-buy-aircraft-leasing-firm-macquarie-airfinance-sources-2026-02-22/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_118",
        "author": "KP Aviation",
        "company": "KP Aviation",
        "title": "Airside MRO Expansion - Part 145 Certified",
        "content": "Announced expansion of Airside MRO, certified FAA, EASA, and UK CAA Part 145 repair and overhaul organization. Open House March 19th. Website: airsidemro.com",
        "business_type": "MRO服务",
        "contact_info": "https://airsidemro.com/, https://lnkd.in/ga2sxyVf",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/kp-aviation/posts",
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
for post in new_real_posts:
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
print(f'Added {added_count} new REAL posts')
print(f'Total posts: {total}')
print(f'Target: 150 (need 37 more from current 113)')
print(f'Remaining: {max(0, 150 - total)}')
