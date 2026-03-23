#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取LinkedIn真实帖子数据并保存
"""

import json
import csv
import pandas as pd
from datetime import datetime
import os
import shutil

# LinkedIn真实帖子数据 (从Browser Relay获取)
posts = [
    {
        "post_id": "linkedin_001",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "author_name": "Abraham San Emeterio",
        "company": "AIRCRAFT & ENGINE TRADERS PLATFORM",
        "position": "",
        "content": "Good evening, I am looking to purchase CFM56-5C2 Qty: 2, PW121A Qty: 1. Open to any cycles remaining but the more cycles the better. Please DM if you have any options available. Thank you, Abraham",
        "business_type": "发动机采购",
        "business_value_score": 5,
        "urgency": "高",
        "has_contact": True,
        "contact_info": "asanem@airsource.us",
        "post_time": "4 days ago",
        "reactions": 6,
        "comments": 1,
        "reposts": 0,
        "has_image": False,
        "image_content": "",
        "source_url": "https://www.linkedin.com/groups/3319971"
    },
    {
        "post_id": "linkedin_002",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "author_name": "Dragon Aviation Capital",
        "company": "Dragon Aviation Capital (Singapore) Pte. Ltd.",
        "position": "",
        "content": "Air India has grounded a Boeing 787 after a reported mid-flight fuel control switch movement from 'run' to 'cutoff' triggered a precautionary review. The incident occurred during cruise, prompting the flight crew to follow established procedures and stabilize the situation before continuing safely. The aircraft landed without injury to passengers or crew, according to initial reports. Engineers have since taken the jet out of service as inspections focus on the fuel control system and cockpit switch mechanisms.",
        "business_type": "行业新闻",
        "business_value_score": 3,
        "urgency": "中",
        "has_contact": False,
        "contact_info": "",
        "post_time": "11 hours ago",
        "reactions": 32,
        "comments": 4,
        "reposts": 1,
        "has_image": True,
        "image_content": "",
        "source_url": "https://www.linkedin.com/company/dragon-aviation-company-singapore-pte-ltd/posts"
    },
    {
        "post_id": "linkedin_003",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "author_name": "Nilesh Salve",
        "company": "Smit Aviation",
        "position": "Founder & CEO",
        "content": "Off-Market Challenger CL605 Available for Sale. Low Hours and on Program. DM me for more details.",
        "business_type": "飞机销售",
        "business_value_score": 4,
        "urgency": "中",
        "has_contact": False,
        "contact_info": "",
        "post_time": "13 hours ago",
        "reactions": 0,
        "comments": 0,
        "reposts": 0,
        "has_image": False,
        "image_content": "",
        "source_url": "https://www.linkedin.com/in/nilesh-salve-829b0a1a7"
    },
    {
        "post_id": "linkedin_004",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "author_name": "Eglė Palevičiūtė",
        "company": "Heston Materials",
        "position": "Global Sales | Airframe Component",
        "content": "Heston Materials currently has a overhauled A320 landing gear shipset available for immediate sale or lease — perfect for operators planning scheduled maintenance or preparing for a 10-year landing gear replacement. Key Details: CSN: 8098, TSN: 13,843:32, Overhauled: November 2024, Zero time/cycles since overhaul. This single-operator shipset is crated, ready for installation, and includes full traceability from BTB. It comes certified with: EASA Form 1, FAA 8130.",
        "business_type": "起落架销售/租赁",
        "business_value_score": 5,
        "urgency": "高",
        "has_contact": True,
        "contact_info": "rfq@hestonmaterials.com",
        "post_time": "2 weeks ago",
        "reactions": 4,
        "comments": 0,
        "reposts": 0,
        "has_image": True,
        "image_content": "",
        "source_url": "https://www.linkedin.com/in/egle-paleviciute"
    },
    {
        "post_id": "linkedin_005",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "author_name": "Aero Inspection",
        "company": "Aero Inspection",
        "position": "",
        "content": "We're pleased to share that our Regional Sales Manager for APAC, Mirna Sivakumar, will be joining the Aero Engines APAC conference in Hong Kong from March 4-5. We look forward to engaging with lessors, airlines, and partners on aircraft technical asset management and sharing how our team can add value in a rapidly evolving industry.",
        "business_type": "会议活动",
        "business_value_score": 3,
        "urgency": "低",
        "has_contact": False,
        "contact_info": "",
        "post_time": "4 hours ago",
        "reactions": 14,
        "comments": 0,
        "reposts": 1,
        "has_image": True,
        "image_content": "",
        "source_url": "https://www.linkedin.com/company/aero-inspection/posts"
    },
    {
        "post_id": "linkedin_006",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "author_name": "Tatjana Obrazcova",
        "company": "50skyshades World Aviation News",
        "position": "Managing Partner/Founder",
        "content": "ACIA Aero Leasing announced the delivery of its third ATR 72-600 passenger aircraft on lease to PNG Air, Papua New Guinea's leading domestic airline. For nearly four decades, PNG Air has proudly connected the people of Papua New Guinea with safe, reliable, and affordable air services. PNG Air operates over 22 destinations, providing essential passenger and cargo services. In 2024, the airline carried more than 150,000 passengers, underscoring its pivotal role as the nation's connector.",
        "business_type": "飞机租赁",
        "business_value_score": 4,
        "urgency": "中",
        "has_contact": False,
        "contact_info": "",
        "post_time": "15 hours ago",
        "reactions": 49,
        "comments": 2,
        "reposts": 2,
        "has_image": True,
        "image_content": "",
        "source_url": "https://www.linkedin.com/in/tatjana-obrazcova-601a734b"
    },
    {
        "post_id": "linkedin_007",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "author_name": "Kate Duffy",
        "company": "Bloomberg",
        "position": "Aerospace Reporter",
        "content": "The man who sold more than 60,000 fake jet-engine parts to airline customers worldwide has just been sentenced to +4 years in prison. Jose Alejandro Zamora Yrala, the former director of AOG Technics Ltd and part-time DJ, dressed in a navy suit and spoke only to confirm his name. The global scandal, which our aviation team first reported in 2023, has grounded planes, caused £40 million in damages and forced major airlines to hunt for parts with falsified documents in their fleets.",
        "business_type": "行业新闻",
        "business_value_score": 3,
        "urgency": "低",
        "has_contact": False,
        "contact_info": "",
        "post_time": "16 hours ago",
        "reactions": 33,
        "comments": 2,
        "reposts": 2,
        "has_image": True,
        "image_content": "",
        "source_url": "https://www.linkedin.com/in/kate-duffy-2187a2124"
    }
]

# 保存为JSON
json_file = 'linkedin_real_posts_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.json'
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

# 保存为CSV
csv_file = json_file.replace('.json', '.csv')
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=posts[0].keys())
    writer.writeheader()
    writer.writerows(posts)

# 创建Excel文件
excel_file = 'LinkedIn_Real_Posts_' + datetime.now().strftime('%Y%m%d') + '.xlsx'
df = pd.DataFrame(posts)
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='真实帖子数据', index=False)
    
    # 创建业务类型统计
    stats = df.groupby('business_type').agg({
        'post_id': 'count',
        'business_value_score': 'mean',
        'reactions': 'sum'
    }).rename(columns={'post_id': '数量', 'business_value_score': '平均评分', 'reactions': '总互动'})
    stats.to_excel(writer, sheet_name='业务类型统计')

# 复制到桌面
desktop = os.path.expanduser('~/Desktop/LINKEDIN/Real_Posts')
os.makedirs(desktop, exist_ok=True)
shutil.copy(json_file, desktop)
shutil.copy(csv_file, desktop)
shutil.copy(excel_file, desktop)

print('成功提取', len(posts), '条真实LinkedIn帖子')
print('JSON:', json_file)
print('CSV:', csv_file)
print('Excel:', excel_file)
print('已保存到:', desktop)
print()
print('业务价值统计:')
print('- 高价值 (5分):', len([p for p in posts if p['business_value_score'] == 5]))
print('- 中高价值 (4分):', len([p for p in posts if p['business_value_score'] == 4]))
print('- 一般 (3分):', len([p for p in posts if p['business_value_score'] == 3]))
print('- 紧急:', len([p for p in posts if p['urgency'] == '高']))
