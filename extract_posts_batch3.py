import json
import os
from datetime import datetime

# 从快照提取的新业务帖子
new_posts = [
    {
        "post_id": "linkedin_real_036",
        "author": "AviaAM Leasing",
        "title": "Boeing 737-400BDSF Sale to ECT Aviation Group",
        "content": "AviaAM Leasing successfully completed the sale of a Boeing 737-400BDSF to ECT Aviation Group. The aircraft was delivered with a CFM56-3C1 engine installed on-wing.",
        "business_type": "飞机整机买卖",
        "contact_info": "https://www.linkedin.com/company/aviaam-leasing/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/feed/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_037",
        "author": "VSE Aviation",
        "title": "CF6-80C2 HPT Stage 1 Nozzle Guide Vanes Installation",
        "content": "Engine experts successfully completed Stage 1 HPT NVG Installation on CF6-80C2 core module. Contact: US: support-davie@vseaviation.com, EUR: supprt-ie@vseaviation.com",
        "business_type": "发动机维修",
        "contact_info": "support-davie@vseaviation.com",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/vse-aviation-inc/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_038",
        "author": "Daniel Sheldon",
        "title": "TAY611-8 Engine Pair Available",
        "content": "AVIALABLE-G-IV-P/N 611-8 TAY611-8 ENGINE-PAIR 2.3M. 300 HRS Since Mid Life-8 Years till OH Due. RR Corp Care Optional. FREE INSTALLATION",
        "business_type": "发动机买卖",
        "contact_info": "LinkedIn DM",
        "urgency": True,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/in/daniel-sheldon-98b5685a/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_039",
        "author": "Aergo Capital",
        "title": "Boeing 737-800 Acquisition from BBAM",
        "content": "Aergo Capital Ltd. completed the acquisition of One Boeing 737-800 from BBAM. The aircraft, MSN 37593, is on lease to KLM Royal Dutch Airlines.",
        "business_type": "飞机整机买卖",
        "contact_info": "https://www.linkedin.com/company/aergo-capital/",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/company/aergo-capital/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_040",
        "author": "Abhi Krishna",
        "title": "Urgent: NLG For ATR 72 Required",
        "content": "Urgently required: NLG For ATR 72, PN: D22698172-108 QTY: 1 ASSY COND: OH Aircraft Type: ATR72-212",
        "business_type": "起落架交易",
        "contact_info": "sales@aviano.in",
        "urgency": True,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/in/abhi-krishna-b73418243/",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_041",
        "author": "MTU Aero Engines",
        "title": "MTU 2025 Financial Results - Record Highs",
        "content": "Adjusted revenue climbed 16% to €8.7 billion. Adjusted operating profit up 29% to €1.4 billion. EBIT margin 15.5%. Adjusted net income €968 million.",
        "business_type": "发动机服务",
        "contact_info": "https://www.linkedin.com/company/mtu-aero-engines/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/mtu-aero-engines/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_042",
        "author": "AvGen Aerospace",
        "title": "MRO Services Available",
        "content": "From Disassembly to Ready for Service. Precision, expertise, and reliability in every repair. Contact: repairs@avgenaerospace.com",
        "business_type": "MRO服务",
        "contact_info": "repairs@avgenaerospace.com",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/avgenaerospace/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_043",
        "author": "AIRCRAFT BUY SALE CHARTER LEASE",
        "title": "Boeing 777-200ER Available for Sale",
        "content": "Available for sale: 2 Units, B777-200 ER YOM 2004. Interested buyers welcome to provide contact details.",
        "business_type": "飞机整机买卖",
        "contact_info": "Group post",
        "urgency": False,
        "business_value_score": 5,
        "source_url": "https://www.linkedin.com/groups/4417384",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_044",
        "author": "Med-Air/Med-Craft",
        "title": "Aeroxchange Conference Team",
        "content": "Med-Air/Med-Craft team at Aeroxchange conference ready to meet. Sofia and Miguel available for meetings.",
        "business_type": "航材服务",
        "contact_info": "https://www.linkedin.com/company/med-air-med-craft/posts",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/med-air-med-craft/posts",
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "post_id": "linkedin_real_045",
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
        "post_id": "linkedin_real_046",
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
        "post_id": "linkedin_real_047",
        "author": "Céline MARCHAL",
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
        "post_id": "linkedin_real_048",
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
        "post_id": "linkedin_real_049",
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
        "post_id": "linkedin_real_050",
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
        "post_id": "linkedin_real_051",
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
        "post_id": "linkedin_real_052",
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
        "post_id": "linkedin_real_053",
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
        "post_id": "linkedin_real_054",
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
        "post_id": "linkedin_real_055",
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
        "post_id": "linkedin_real_056",
        "author": "Tim Mathis - IAG Engines",
        "title": "VP & GM at IAG Engines",
        "content": "Rejoined MRO community with IAG Engines. Focusing on building repair station with emphasis on engine and component repair.",
        "business_type": "发动机维修",
        "contact_info": "https://www.linkedin.com/in/tim-mathis-8355766/",
        "urgency": False,
        "business_value_score": 4,
        "source_url": "https://www.linkedin.com/company/iag-aero-group/",
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
for post in new_posts:
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
