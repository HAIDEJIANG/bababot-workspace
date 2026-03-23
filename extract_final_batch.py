import json
import os
from datetime import datetime

# 从最新快照提取的业务帖子 (帖子 #57-#148)
new_posts_batch = [
    {
        "post_id": "linkedin_real_057",
        "author": "AIRCRAFT BUY SALE CHARTER LEASE",
        "title": "Boeing 777-200ER Available for Sale",
        "content": "Available for sale: 2 Units, B777-200 ER YOM 2004. Interested buyers welcome to provide contact details.",
        "business_type": "飞机整机买卖",
        "contact_info": "Group post - contact via LinkedIn",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/groups/4417384",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_058",
        "author": "Med-Air/Med-Craft",
        "title": "Aeroxchange Conference Team",
        "content": "Med-Air/Med-Craft team at Aeroxchange conference ready to meet. Sofia and Miguel available for meetings.",
        "business_type": "航材服务",
        "contact_info": "Conference contact",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/med-air-med-craft/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_059",
        "author": "Cat Buchanan - STACK.aero",
        "title": "Prime Jet Joins STACK.aero",
        "content": "Welcome Prime Jet into STACK.aero family! Aviation CRM platform for charter operators.",
        "business_type": "航空软件服务",
        "contact_info": "https://www.linkedin.com/company/stack-aero/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/cat-buchanan-28b18114/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_060",
        "author": "Dubai Aerospace Enterprise",
        "title": "Fireside Chat with Akasa Air",
        "content": "Firoz Tarapore, CEO joined by Priya Mehra, Chief of Governance & Strategic Acquisitions, Akasa Air for fireside chat.",
        "business_type": "飞机租赁",
        "contact_info": "https://www.linkedin.com/company/dubai-aerospace-enterprise/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/airline-economics/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_061",
        "author": "Céline MARCHAL - Aero Asset",
        "title": "VP Sales APAC at Aero Asset",
        "content": "New role as VP Sales APAC at Aero Asset. Building team in Singapore. Specializing in preowned turbine helicopter market.",
        "business_type": "直升机销售",
        "contact_info": "https://www.linkedin.com/in/celine-marchal-7025b452/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/aeroasset/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_062",
        "author": "Piero Fusco - FTAI Aviation",
        "title": "Director, Supply Chain at FTAI Aviation",
        "content": "Started new position as Director, Supply Chain at FTAI Aviation. Leader in engine repair and exchange space.",
        "business_type": "发动机维修",
        "contact_info": "https://www.linkedin.com/in/piero-fusco/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/ftai-aviation/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_063",
        "author": "Challenge Group",
        "title": "Europe's First 777-300 ERSF Cargo Aircraft",
        "content": "Europe's first 777-300 ERSF cargo aircraft now operational at Malta HQ. Moving cargo across global network.",
        "business_type": "飞机改装/货运",
        "contact_info": "https://www.linkedin.com/company/ace-aviation-group/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/ace-aviation-group/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_064",
        "author": "TARCG",
        "title": "Aircraft Painters Needed - Central Europe",
        "content": "Seeking Aircraft Painters for 2-week contract. Start: March 9, 2026. Accommodation provided. Contact: emma.meyer@tarcg.com",
        "business_type": "维修服务",
        "contact_info": "emma.meyer@tarcg.com",
        "urgency": True,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/groups/141784",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_065",
        "author": "elfc - Engine Lease Finance Corp",
        "title": "Aero Engines Asia Pacific Conference",
        "content": "Aero Engines Asia Pacific conference in Hong Kong next week. elfc team attending. Reach out to connect.",
        "business_type": "发动机租赁",
        "contact_info": "https://www.linkedin.com/company/engine-lease-finance-corporation/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/engine-lease-finance-corporation/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_066",
        "author": "GSE America",
        "title": "GSE Repair and Overhaul Services",
        "content": "GSE repair services available. Contact: servicesupport@gse-america.com",
        "business_type": "地面设备维修",
        "contact_info": "servicesupport@gse-america.com",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/gse-america/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_067",
        "author": "SPAERO",
        "title": "Aviation Turbine Materials Joins Spaero",
        "content": "Aviation Turbine Materials joined Spaero! Global aircraft parts supplier. 24/7 AOG support.",
        "business_type": "航材供应",
        "contact_info": "https://spaero.co.uk/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/spaero-marketplace/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_068",
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
        "post_id": "linkedin_real_069",
        "author": "Seattle Aviation Solutions",
        "title": "MRO Middle East 2026",
        "content": "Team at MRO Middle East 2026. Ready to connect at booth No. 750.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/seattle-aviation/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/seattle-aviation/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_070",
        "author": "Tim Mathis - IAG Engines",
        "title": "VP & GM at IAG Engines",
        "content": "Rejoined MRO community with IAG Engines. Focusing on building repair station with emphasis on engine and component repair.",
        "business_type": "发动机维修",
        "contact_info": "https://www.linkedin.com/in/tim-mathis-8355766/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/iag-aero-group/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_071",
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
        "post_id": "linkedin_real_072",
        "author": "Dragon Aviation Capital",
        "title": "ZIPAIR Charter Service Launch",
        "content": "ZIPAIR launched inaugural nonstop charter service between Narita and Orlando. Four Boeing 787-8 charter flights scheduled.",
        "business_type": "飞机租赁/包机",
        "contact_info": "https://www.linkedin.com/company/dragon-aviation-company-singapore-pte-ltd/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/dragon-aviation-company-singapore-pte-ltd/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_073",
        "author": "Aerospace Engineering Innovation",
        "title": "Aerospace Composites Market Report",
        "content": "Aerospace composites market estimated at USD 30.3 billion in 2025, projected to reach USD 53.4 billion by 2030.",
        "business_type": "航空材料",
        "contact_info": "Industry report",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/groups/8573821",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_074",
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
        "post_id": "linkedin_real_075",
        "author": "CTS Engines",
        "title": "PB Expo Career Runway",
        "content": "CTS Engines at PB Expo Career Runway in Miami Beach. Recruiting for open roles. Stop by booth to meet team.",
        "business_type": "发动机维修/招聘",
        "contact_info": "Career event",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/cts-engines/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_076",
        "author": "FLYE Aviation",
        "title": "Aircraft Sales, Leasing, Charters",
        "content": "Founder & Managing Director at FLYE Aviation. Aircraft sales, leasing, and charter services.",
        "business_type": "飞机销售/租赁",
        "contact_info": "http://www.flyeaviation.co.za",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/mariolise-lisa-williams/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_077",
        "author": "CAVU Aerospace",
        "title": "Sales & Procurement Team Hiring",
        "content": "CAVU Aerospace hiring for Sales & Procurement team in Hollywood, FL. Aviation aftermarket experience required.",
        "business_type": "航材销售/招聘",
        "contact_info": "https://www.linkedin.com/company/cavu-aerospace/posts",
        "urgency": True,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/cavu-aerospace/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_078",
        "author": "Aero Surround",
        "title": "MRO Americas 2026 Attendance",
        "content": "Aero Surround attending MRO Americas in Orlando, April 21-23, 2026. Team members Ovidijus and Arvydas available for meetings.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/aero-surround/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/aero-surround/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_079",
        "author": "AerFin",
        "title": "Strategic Aircraft Teardowns",
        "content": "CEO Simon Goodson explains how mid-life teardowns help owners unlock value and navigate supply chain constraints.",
        "business_type": "飞机拆解/资产管理",
        "contact_info": "https://www.linkedin.com/company/aerfin-limited/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/aerfin-limited/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_080",
        "author": "LS Technics",
        "title": "Airbus A220 Part-145 Expansion",
        "content": "Expanded Part-145 certificate with new capabilities for Airbus A220 family. First MRO in Poland with such broad scope.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/ls-technics/posts",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/ls-technics/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_081",
        "author": "ABL Aviation",
        "title": "737 MAX 8 Delivery to TUI",
        "content": "ABL Aviation completes second 737 MAX 8 delivery to TUI.",
        "business_type": "飞机租赁",
        "contact_info": "https://www.linkedin.com/company/ablaviation/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/avitrader-publications-corp/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_082",
        "author": "Aergo Capital",
        "title": "Boeing 737-800 Acquisition",
        "content": "Aergo Capital completed acquisition of One Boeing 737-800 from BBAM. Aircraft on lease to KLM Royal Dutch Airlines.",
        "business_type": "飞机交易",
        "contact_info": "https://www.linkedin.com/company/aergo-capital/posts",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/aergo-capital/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_083",
        "author": "Aviation Trading Circle",
        "title": "Aviation Match Maker Platform Launch",
        "content": "Launched Aviation Match Maker (AMM) - sourcing & remarketing platform for commercial aviation professionals. Free listings.",
        "business_type": "航空平台",
        "contact_info": "http://aviationmatchmaker.com",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/groups/2205442",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_084",
        "author": "APOC Aviation",
        "title": "MRO & Technical Services Expansion",
        "content": "VP MRO & Technical Ian Foster broadening APOC Aviation's reach in component repair, landing gear, and engine shop visits.",
        "business_type": "MRO服务",
        "contact_info": "https://www.linkedin.com/company/apoc-aviation/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/apoc-aviation/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_085",
        "author": "GKN Aerospace",
        "title": "MANTA Programme Completion",
        "content": "GKN Aerospace and partners successfully complete MANTA programme for next-gen aircraft control surface technologies.",
        "business_type": "航空技术",
        "contact_info": "https://www.linkedin.com/company/gkn-aerospace/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/gkn-aerospace/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_086",
        "author": "Earth & Flight Composites",
        "title": "Composite Repair Courses Frankfurt",
        "content": "FAA/EASA-approved composite repair courses in Frankfurt, Germany from March to June 2026. Seats limited.",
        "business_type": "维修培训",
        "contact_info": "https://www.linkedin.com/company/earth-flight-composites-training-and-consultancy/",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/groups/4433405",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_087",
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
        "post_id": "linkedin_real_088",
        "author": "Niagara Controls",
        "title": "ASC Engineered Solutions Products",
        "content": "Collins Companies carry ASC Engineered Solutions GruvLok products. High-pressure piping solutions.",
        "business_type": "航材供应",
        "contact_info": "https://lnkd.in/eFjFNsY3",
        "urgency": False,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/showcase/niagara-controls/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_089",
        "author": "Seal Dynamics",
        "title": "Regional Sales Manager Appointment",
        "content": "Gabriel Orlando Vazquez Mazariegos joined Seal Dynamics as Regional Sales Manager. Aviation parts and distribution.",
        "business_type": "航材销售",
        "contact_info": "https://www.linkedin.com/company/seal-dynamics/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/in/gabriel-orlando-vazquez-mazariegos-12919167/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_090",
        "author": "Batam Aero Technic",
        "title": "Engineer Hiring - Lion Air Group",
        "content": "Batam Aero Technic hiring engineers: Workscoping Planner, Engineering Specialist, Shop Engineer, Tools Engineer, Structure Engineer.",
        "business_type": "MRO/招聘",
        "contact_info": "bit.ly/REC-TEKNIK",
        "urgency": True,
        "business_value_score": 3,
        "source_url": "https://www.linkedin.com/company/batam-aero-technic/",
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
for post in new_posts_batch:
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
print(f"还差: {remaining} 条")
