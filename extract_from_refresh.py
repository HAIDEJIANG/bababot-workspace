import json
import os
from datetime import datetime

# 批量提取新帖子（基于刷新后的页面内容）
new_posts_batch = [
    {
        "post_id": "linkedin_new_011",
        "author": "ACC Aviation",
        "company": "ACC Aviation Ltd",
        "title": "Air Calédonie ATR 72-600 Aircraft Remarketing",
        "content": "Supported Air Calédonie with remarketing of their ATR 72-600 aircraft, successfully acquired by Federal Express Corporation (FedEx).",
        "business_type": "飞机交易/再营销",
        "contact_info": "https://www.linkedin.com/company/acc-aviation-ltd/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/acc-aviation-ltd/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_012",
        "author": "Linn Shaw",
        "company": "KP Aviation",
        "title": "Airside MRO Expansion - Part 145 Certification",
        "content": "KP Aviation announces expansion of Airside MRO, certified FAA, EASA, and UK CAA Part 145 repair and overhaul organization. Open House March 19th.",
        "business_type": "MRO服务",
        "contact_info": "https://airsidemro.com/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/kp-aviation/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_new_013",
        "author": "Robert Sitta",
        "company": "ACC Aviation",
        "title": "Aircraft Remarketing Success Story",
        "content": "Reposted ACC Aviation successful aircraft remarketing project. ATR 72-600 transaction completed with FedEx.",
        "business_type": "飞机交易",
        "contact_info": "https://www.linkedin.com/in/robert-sitta-266a6895/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/robert-sitta-266a6895/",
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
print(f'Added {added_count} new posts from refresh')
print(f'Total posts: {total}')
print(f'Target: 150')
print(f'Remaining: {max(0, 150 - total)}')
