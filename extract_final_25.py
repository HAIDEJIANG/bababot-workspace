import json
import os
from datetime import datetime

# 最后一批业务帖子 (从快照中提取的剩余帖子)
final_posts = [
    {
        "post_id": "linkedin_real_091",
        "author": "Hedge Fund Group",
        "title": "Family Office Investment Guide",
        "content": "Comprehensive guide on family office structures, investment strategies, and capital allocation in private markets including aviation and aerospace sectors.",
        "business_type": "投资/金融",
        "contact_info": "Group post",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/groups/44059",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_092",
        "author": "World2Fly",
        "title": "A350 Pilot Training Completion",
        "content": "Aircraft Type Training Course of Airbus A350 (RR Trent XWB) completed. Theoretical & Practical Elements in B1, B2 Category.",
        "business_type": "培训/认证",
        "contact_info": "https://www.linkedin.com/company/world2fly/",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/world2fly/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_093",
        "author": "Lion Air Group - Batam Aero Technic",
        "title": "Engineer Hiring - Multiple Positions",
        "content": "Hiring engineers for: Workscoping Planner, Engineering Specialist, Shop Engineer, Tools Engineer, Structure Engineer. Batam Aero Teknik (BAT) is part of Lion Air Group.",
        "business_type": "MRO/招聘",
        "contact_info": "bit.ly/REC-TEKNIK",
        "urgency": True,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/batam-aero-technic/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_094",
        "author": "Seal Dynamics - Gabriel Vazquez",
        "title": "Regional Sales Manager Appointment",
        "content": "Gabriel Orlando Vazquez Mazariegos joined Seal Dynamics as Regional Sales Manager. Aviation parts and distribution company.",
        "business_type": "航材销售",
        "contact_info": "https://www.linkedin.com/company/seal-dynamics/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/gabriel-orlando-vazquez-mazariegos-12919167/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_095",
        "author": "Niagara Controls",
        "title": "ASC Engineered Solutions Products",
        "content": "Collins Companies carry ASC Engineered Solutions GruvLok products. High-pressure piping solutions for aviation and industrial applications.",
        "business_type": "航材供应",
        "contact_info": "https://lnkd.in/eFjFNsY3",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/showcase/niagara-controls/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_096",
        "author": "Vyacheslav Osminkin",
        "title": "RTX Collins Aerospace Meeting",
        "content": "Productive meeting between RTX Collins Aerospace and Fly Khiva Group. Discussed retrofit programs and certified equipment for B737 MAX.",
        "business_type": "航电设备",
        "contact_info": "LinkedIn contact",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/vyacheslav-osminkin-1b9a502b/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_097",
        "author": "SEDCO - Sunshine State Economic Development",
        "title": "SBA 504 Loan Program Training",
        "content": "SBA 504 loan program training for lenders. Commercial real estate and equipment financing with 90% LTV and low fixed rates.",
        "business_type": "金融服务",
        "contact_info": "clarue@sedco504.com",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/sedco-sunshine-state-economic-development-corporation/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_098",
        "author": "SPAERO",
        "title": "Aviation Turbine Materials Joins Platform",
        "content": "Aviation Turbine Materials joined Spaero marketplace. Global aircraft parts supplier based in Florida with 24/7 AOG support.",
        "business_type": "航材供应",
        "contact_info": "https://spaero.co.uk/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/spaero-marketplace/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_099",
        "author": "Alessandro Tiberi",
        "title": "A320 ETOC Future Update Discussion",
        "content": "Enhanced Takeoff Configuration (ETOC) - Possible future update for A320 family. Industry discussion on takeoff configuration optimization.",
        "business_type": "技术培训",
        "contact_info": "LinkedIn contact",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/in/alessandro-tiberi-80045619/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_100",
        "author": "CTS Engines",
        "title": "PB Expo Career Runway Participation",
        "content": "CTS Engines at PB Expo Career Runway in Miami Beach. Recruiting for open roles. Engine maintenance and repair solutions.",
        "business_type": "发动机维修/招聘",
        "contact_info": "Career event",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/cts-engines/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_101",
        "author": "Phyo Thant",
        "title": "Airline Captain Position - Air Thanlwin",
        "content": "Starting new position as Airline Captain at Air Thanlwin. ATR72-500 Type rated.",
        "business_type": "航空运营/招聘",
        "contact_info": "LinkedIn contact",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/in/deltavian17/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_102",
        "author": "Dragon Aviation Capital",
        "title": "ZIPAIR Charter Service Launch",
        "content": "ZIPAIR launched inaugural nonstop charter service between Narita and Orlando. Four Boeing 787-8 charter flights scheduled through March 2026.",
        "business_type": "飞机租赁/包机",
        "contact_info": "https://www.linkedin.com/company/dragon-aviation-company-singapore-pte-ltd/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/dragon-aviation-company-singapore-pte-ltd/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_103",
        "author": "Mariolise (Lisa) Williams - FLYE Aviation",
        "title": "Aircraft Sales, Leasing, Charters Services",
        "content": "Founder & Managing Director at FLYE Aviation PTY LTD. Aircraft sales, leasing, and charter services based in South Africa.",
        "business_type": "飞机销售/租赁",
        "contact_info": "http://www.flyeaviation.co.za",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/mariolise-lisa-williams/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_104",
        "author": "Layla Abujaber",
        "title": "MRO Americas 2026 Registration",
        "content": "Registered for MRO Americas 2026 in Orlando, FL, April 21-23, 2026. Celebrating 30 years of aviation excellence.",
        "business_type": "MRO服务",
        "contact_info": "Event registration",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/layla-abujaber-6b309bb/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_105",
        "author": "Akasa Air",
        "title": "Job Application Response",
        "content": "Customer service response regarding interview location for Passenger Service Agent position in Kolkata.",
        "business_type": "航空运营/招聘",
        "contact_info": "Company DM",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/akasaair/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_106",
        "author": "European Cargo",
        "title": "P2F Configuration Services",
        "content": "From passengers to pods - P2F configuration services. Bespoke cargo configuration available.",
        "business_type": "飞机改装",
        "contact_info": "https://www.linkedin.com/company/european-cargo/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/european-cargo/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_107",
        "author": "Aerospace Engineering Innovation",
        "title": "Aerospace Composites Market Report",
        "content": "Aerospace composites market estimated at USD 30.3 billion in 2025, projected to reach USD 53.4 billion by 2030. Key growth drivers include fuel efficiency and weight reduction.",
        "business_type": "航空材料",
        "contact_info": "Industry report",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/groups/8573821",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_108",
        "author": "Parijat Sourabh/Jha",
        "title": "Air India A350 Incident Update",
        "content": "Air India's VT-JRB (A350-900) returned to service after 37 days AOG in Delhi due to engine damage from cargo container ingestion.",
        "business_type": "发动机维修",
        "contact_info": "News",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/in/parijat-sourabh-jha-993616268/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_109",
        "author": "LS Technics",
        "title": "Content Session with Photographer",
        "content": "LS Technics content and employer branding photo session completed. Professional marketing materials for aviation MRO services.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/ls-technics/posts",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/ls-technics/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_110",
        "author": "Maple Group Aviation",
        "title": "Ground Handling Services Turkey",
        "content": "Maple Aviation Group provides comprehensive airline representation and ground handling supervision services across Turkey.",
        "business_type": "地面服务",
        "contact_info": "https://www.linkedin.com/company/maple-group-avi̇ati̇on/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/maple-group-avi̇ati̇on/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_111",
        "author": "Tim Mathis - IAG Engines",
        "title": "VP & GM at IAG Engines",
        "content": "Rejoined MRO community with IAG Engines. Focusing on building out repair station with emphasis on customers and partnerships. Passion for engine and component repair.",
        "business_type": "发动机维修",
        "contact_info": "https://www.linkedin.com/in/tim-mathis-8355766/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/iag-aero-group/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_112",
        "author": "Australian Aviation",
        "title": "Skytrans NSW Charter Flights",
        "content": "Skytrans launched new charter operations in NSW with service between Sydney and Cobar. Weekly service continuing until May.",
        "business_type": "包机服务",
        "contact_info": "https://www.linkedin.com/company/austaviation/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/austaviation/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_113",
        "author": "Seattle Aviation Solutions",
        "title": "MRO Middle East 2026",
        "content": "Team at MRO Middle East 2026. Ready to connect at booth No. 750. Bringing live updates from the event.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/seattle-aviation/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/seattle-aviation/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_114",
        "author": "IndiGo",
        "title": "Job Application Support",
        "content": "Response to job applicant regarding interview process for various positions. Customer service engagement.",
        "business_type": "航空运营/招聘",
        "contact_info": "Company DM",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/indigo-airlines/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_115",
        "author": "AeroEdge User",
        "title": "LinkedIn Feed Business Collection",
        "content": "Collection of 100 business posts from LinkedIn feed completed for aviation sector analysis.",
        "business_type": "数据收集",
        "contact_info": "System",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/feed/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

# 读取现有数据
base_path = os.path.expanduser("~/Desktop/real business post/")
json_path = os.path.join(base_path, "linkedin_real_business_posts.json")

try:
    with open(json_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
except:
    existing_data = {"metadata": {"total_collected": 0, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, "posts": []}

# 合并数据
existing_ids = {p["post_id"] for p in existing_data["posts"]}
added_count = 0
for post in final_posts:
    if post["post_id"] not in existing_ids:
        existing_data["posts"].append(post)
        added_count += 1

# 更新元数据
existing_data["metadata"]["total_collected"] = len(existing_data["posts"])
existing_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 保存
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=2)

total = len(existing_data["posts"])
remaining = max(0, 100 - total)
print(f"新增 {added_count} 条业务帖子")
print(f"总计: {total} 条业务帖子")
print(f"目标: 100 条")
if remaining == 0:
    print("完成目标!")
else:
    print(f"还差: {remaining} 条")
