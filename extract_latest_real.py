import json
import os
from datetime import datetime

# 最新提取的真实帖子
new_real_posts = [
    {
        "post_id": "linkedin_real_119",
        "author": "Gizem Cakalagaoglu",
        "company": "未明确",
        "title": "New listings for Sale - CFM56 Engines",
        "content": "New listings for Sale: CFM56-7B27 (C/R: 8,750), CFM56-7B27 (C/R: 8,583), CFM56-5B4 (C/R: 5,004), CFM56-5B6 (C/R: 6,491). Contact for more details.",
        "business_type": "发动机买卖",
        "contact_info": "LinkedIn contact",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/in/gizem-cakalagaoglu-96986b3a/",
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
print(f'Added {added_count} new REAL post(s)')
print(f'Total posts: {total}')
print(f'Target: 150 (need 32 more)')
print(f'Remaining: {max(0, 150 - total)}')
