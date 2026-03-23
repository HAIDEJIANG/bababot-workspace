#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn第三批真实帖子数据
"""

import json
import csv
import pandas as pd
from datetime import datetime
import os
import shutil

posts = [
    {
        "post_id": "linkedin_real_011",
        "timestamp": "2026-02-24 22:00:00",
        "author_name": "Rotafilo",
        "company": "Rotafilo",
        "position": "",
        "content": "Available Now — Ready to Support Your Operations. Rotafilo CFM56-3 Compatible Transportation Stand. P/N: RFENGSTDCFM3. Engineered for safe, reliable, and efficient engine transportation, this stand is built to meet the operational needs of airlines and MRO facilities. Key advantages: Durable construction ensuring secure engine support, Designed to streamline transportation and maintenance processes, Smooth mobility in hangar and ramp operations, Available for immediate dispatch to meet urgent demands.",
        "business_type": "地面设备销售",
        "business_value_score": 4,
        "urgency": "中",
        "has_contact": True,
        "contact_info": "sales@rotafilo.com",
        "post_time": "53 minutes ago",
        "reactions": 3,
        "comments": 0,
        "reposts": 3,
        "has_image": True,
        "source_url": "https://www.linkedin.com/company/rotafilo/posts"
    },
    {
        "post_id": "linkedin_real_012",
        "timestamp": "2026-02-24 22:00:00",
        "author_name": "Charles Zheng",
        "company": "CNS INTERTRANS(SHENZHEN)CO.,LTD",
        "position": "sales/pricing",
        "content": "Roll-on/Roll-off Port Operations: Safety First, Always! Loading a Ro-Ro vessel isn't just about driving vehicles on board—it's a carefully choreographed dance of precision, communication, and safety. Here's how we ensure smooth and secure operations at the port: Pre-loading checks, Clear communication, Speed control, Lashing & securing, Emergency readiness.",
        "business_type": "物流服务",
        "business_value_score": 3,
        "urgency": "低",
        "has_contact": False,
        "contact_info": "",
        "post_time": "5 hours ago",
        "reactions": 3,
        "comments": 0,
        "reposts": 0,
        "has_image": True,
        "source_url": "https://www.linkedin.com/in/charles-zheng-123372393"
    },
    {
        "post_id": "linkedin_real_013",
        "timestamp": "2026-02-24 22:00:00",
        "author_name": "APAS - A Professional Aviation Services",
        "company": "APAS",
        "position": "",
        "content": "Where the Real Decisions Happen. Executives often think in terms of aircraft checks and maintenance events. But the most financially and operationally critical decisions happen much lower — at the component level. This is where repair vs replace is decided, where TAT is won or lost, and where supply chain risk becomes tangible. A single LRU can ground an aircraft longer than an entire scheduled check.",
        "business_type": "MRO服务/咨询",
        "business_value_score": 4,
        "urgency": "中",
        "has_contact": False,
        "contact_info": "",
        "post_time": "25 minutes ago",
        "reactions": 1,
        "comments": 0,
        "reposts": 0,
        "has_image": True,
        "source_url": "https://www.linkedin.com/company/a-professional-aviation-services-corp/posts"
    },
    {
        "post_id": "linkedin_real_014",
        "timestamp": "2026-02-24 22:00:00",
        "author_name": "Ceren Neşşar",
        "company": "Turkish Nacelle Center - Collins Aerospace",
        "position": "Human Resources Manager",
        "content": "We're hiring! Check out this job at Turkish Nacelle Center - Collins Aerospace, Istanbul MRO. Customer Account Representative position available.",
        "business_type": "招聘信息",
        "business_value_score": 2,
        "urgency": "低",
        "has_contact": False,
        "contact_info": "",
        "post_time": "5 hours ago",
        "reactions": 19,
        "comments": 0,
        "reposts": 0,
        "has_image": False,
        "source_url": "https://www.linkedin.com/in/ceren-neşşar-397b392"
    }
]

# 保存为JSON
json_file = 'linkedin_real_posts_batch3_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.json'
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

# 保存为CSV
csv_file = json_file.replace('.json', '.csv')
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=posts[0].keys())
    writer.writeheader()
    writer.writerows(posts)

# 创建Excel
timestamp = datetime.now().strftime('%Y%m%d')
excel_file = 'LinkedIn_Real_Posts_Batch3_' + timestamp + '.xlsx'
df = pd.DataFrame(posts)
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='真实帖子数据', index=False)

# 复制到桌面
desktop = os.path.expanduser('~/Desktop/LINKEDIN/Real_Posts_Batch3')
os.makedirs(desktop, exist_ok=True)
shutil.copy(json_file, desktop)
shutil.copy(csv_file, desktop)
shutil.copy(excel_file, desktop)

print('LinkedIn第三批真实帖子采集完成!')
print('本次采集:', len(posts), '条真实帖子')
print('文件已保存到:', desktop)
