# LinkedIn Aviation Data Collection - Batch 3
# 手动采集的新帖子

import csv
from datetime import datetime

current_time = "2026-03-01T16:50:00+08:00"

new_posts = [
    {
        "timestamp": current_time,
        "author_name": "Piaggio Aerospace / Baykar",
        "author_title": "-",
        "author_company": "Piaggio Aerospace",
        "post_content": "Italian company Piaggio Aerospace, owned by Turkish drone giant Baykar, has unveiled its next-generation aircraft, the Avanti NX. A revolution is underway in Turkish-Italian aviation with modern avionics systems and an annual production target of 30 aircraft.",
        "hashtags": "",
        "source_url": "https://lnkd.in/e6zMAUtY",
        "post_type": "Aircraft News",
        "collected_at": current_time
    },
    {
        "timestamp": current_time,
        "author_name": "Kalitta Air",
        "author_title": "Founder",
        "author_company": "Kalitta Air",
        "post_content": "Happy Birthday, Conrad 'Connie' Kalitta — a true American visionary and entrepreneur. Founder of Kalitta Air in 2000, transforming it into a global freight powerhouse operating worldwide charter and scheduled cargo services.",
        "hashtags": "",
        "source_url": "",
        "post_type": "Company News",
        "collected_at": current_time
    },
    {
        "timestamp": current_time,
        "author_name": "AEUSA / Aviation Week",
        "author_title": "-",
        "author_company": "Aviation Week",
        "post_content": "We're just days away from the biggest event in the aero engines industry! Don't miss your chance to join us next week and be part of a record-breaking year. Secure your spot now.",
        "hashtags": "#AEUSA #AviationWeek #AvWeekEvents #Aviation #AeroEngines #EngineLeasing",
        "source_url": "https://utm.io/ujh2F",
        "post_type": "Event Promotion",
        "collected_at": current_time
    },
    {
        "timestamp": current_time,
        "author_name": "Aerospace Engineering Solutions",
        "author_title": "-",
        "author_company": "Aerospace Engineering Solutions",
        "post_content": "Provided Part 21J exterior livery drawings and EASA-approved certification for Brussels Airlines' newest Tintin-themed Airbus A320 (OO-SNJ), supporting Airbourne Colours Ltd and the wider project team.",
        "hashtags": "#Part21J #AerospaceEngineering #EASA",
        "source_url": "",
        "post_type": "Project Completion",
        "collected_at": current_time
    },
    {
        "timestamp": current_time,
        "author_name": "AMP Aero Services",
        "author_title": "-",
        "author_company": "AMP Aero Services",
        "post_content": "AI brings your weaknesses to baseline. I still focus on what sets you apart. In my work at AMP Aero Services, I see this play out daily. AI can clean a messy dataset in 5 minutes or write Python scripts in 2, but it cannot replace human expertise in aviation.",
        "hashtags": "",
        "source_url": "",
        "post_type": "Industry Insight",
        "collected_at": current_time
    }
]

# 读取现有索引
existing_content = set()
try:
    with open('outputs/aviation_linkedin_master_20250301.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
            existing_content.add(key)
except:
    pass

# 去重并保存
new_count = 0
for post in new_posts:
    key = f"{post['author_name']}_{post['post_content'][:100]}"
    if key not in existing_content:
        with open('outputs/aviation_linkedin_master_20250301.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                post['timestamp'], post['author_name'], post['author_title'],
                post['author_company'], post['post_content'], post['hashtags'],
                post['source_url'], post['post_type'], post['collected_at']
            ])
        new_count += 1
        existing_content.add(key)

print(f"Batch 3: 新增 {new_count} 条记录")
print(f"累计索引: {len(existing_content)} 条")
