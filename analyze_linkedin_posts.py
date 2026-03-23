#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn帖子分析脚本
从LinkedIn Feed中提取的帖子数据，筛选航材/发动机/起落架/飞机整机相关内容
"""

import json
from datetime import datetime

# 从浏览器提取的帖子数据
posts_data = {
    "totalPosts": 32,
    "posts": [
        {
            "selector": ".feed-shared-update-v2",
            "index": 0,
            "text": "Feed post number 1\nVolo Aero MRO\nVolo Aero MRO\n1,544 followers\n1,544 followers\n12h • \n \n12 hours ago • Visible to anyone on or off LinkedIn\nMaterial wanted:\nCustomer requirement for V2500 Fan Blades P/N 6A7614.\nMax 2 repairs\nOHC, ready to go\nfull set required.\nLet me know if you have stock available.\n…more\n2\n1 repost\nLike\nComment\nRepost\nSend"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 1,
            "text": "Feed post number 2\nAleut Ventures\nAleut Ventures\n184 followers\n184 followers\nPromoted\nPromoted\nCut flight time and costs. Make Cold Bay your Pacific refueling stop.\nAviation Fueling & Services\naleutventures.com\nLearn more. View Sponsored Content\nLearn more\n54\n2 comments\n1 repost\nLike\nComment\nRepost\nSend"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 2,
            "text": "Feed post number 3\nFeby Yogaswara\nFeby Yogaswara\n • 1st\n1st\nExperienced Supplier of Military Aircraft Spare Parts, Ammunition, and Defense General Trading Supplies.\nExperienced Supplier of Military Aircraft Spare Parts, Ammunition, and Defense General Trading Supplies.\n1h • \n \n1 hour ago • Visible to anyone on or off LinkedIn\nDear All,\n\nI actively seeking for Buyer who are Interest on the engine as below 👇 \n\nGTD-350 = helicopter turboshaft engine (Mil Mi-2) \n\nIn stock Location 🇮🇩 \nCondition : NS\n\nPlease reach me out if you've customer / Interest to purchase !\n\n\nhashtag\n#MilMi-2 Helicopter\n\nhashtag\n#turboshaftengine\n\nhashtag\n#militaryaircraft\n\nhashtag\n#MRO\n…more\nActivate to view larger image,\n1\n1 comment\nLike\nComment\nRepost\nSend"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 3,
            "text": "Feed post number 4\nAyush Tiwari\nAyush Tiwari\n   • 1st\nPremium • 1st\nAccount Manager @ AMP Aero Services\nAccount Manager @ AMP Aero Services\n13h • \n \n13 hours ago • Visible to anyone on or off LinkedIn\n✈️ Available for Immediate Sale – Engine Mount Assembly\n\nAMP Aero Services is pleased to offer the following unit available in Overhauled (OH) condition:\nP/N: FWDMOUNT04\nDescription: FWD ENGINE MOUNT ASSY\nApplication: CF6-80C2 Engine\nCondition: OH\nTrace: Japan Airlines\nTagged By: NAS MRO Services, LLC\nTag Date: 15-Oct-2024\n\n\nFor PPW details and pricing, please reach out:\n📧 ayush@amp-aero.com\n📞 +91-7906578499\n\n\nhashtag\n#AviationParts \nhashtag\n#CF680C2 \nhashtag\n#AircraftMaintenance \nhashtag\n#MRO \nhashtag\n#AviationSales \nhashtag\n#EngineComponents\n…more\nActivate to view larger image,\nActivate t"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 4,
            "text": "Feed post number 5\nAvioDirect\nAvioDirect\n2,828 followers\n2,828 followers\n5h • \n \n5 hours ago • Visible to anyone on or off LinkedIn\n3800708-1 131-9A APU (OH) is available and ready to\nsupport your operational needs.\n\nAt Aviodirect, we deliver trusted aviation components with\nefficiency, transparency, and global reach.\n\n📩 Contact us for availability, pricing, and logistics details.\n\nCONTACT US:\n\n📞 +1(205)417‑7427/+507 392- 7456 / +507 6384- 2664\n📩 sales@aviodirect.com\n🌐 www.aviodirect.com\n\n\nhashtag\n#Aviation \nhashtag\n#APU \nhashtag\n#AircraftParts \nhashtag\n#MRO \nhashtag\n#AviationIndustry\n\nhashtag\n#Aviodirect \nhashtag\n#InStock \nhashtag\n#AviationSolutions\n…more\nActivate to view larger image,\nSee content credentials\nActivate to view larger image,\n6\n1 repost\nLike\nComment\nRepost\nSend"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 5,
            "text": "Feed post number 6\nAerFin\nAerFin\n21,186 followers\n21,186 followers\nPromoted\nPromoted\nAt AerFin, we're proud to support operators across the full Embraer E-Jet family – E170, E175, E190 and E195. \n\nOur specialist teams provide: \n\n- Airframe components \n- High-value assets \n- Engine components \n- A wide pool of parts \n\nAll tailored to maximise asset life, reduce costs and keep your fleet flying efficiently. \n\nTrusted by airlines, lessors and MROs worldwide, AerFin delivers reliable, sustainable solutions that breathe new life into regional aviation. \n\nGet in touch today https://lnkd.in/eXZjNgbV \n\nhashtag\n#AerFin \nhashtag\n#TheWayAhead\n…more\nView sponsored page\n57\n1 repost\nLike\nComment\nRepost\nSend"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 6,
            "text": "Feed post number 7\nSkyUp Airlines likes this\nAir Logistics International\nAir Logistics International\n6,100 followers\n6,100 followers\n13h • \n \n13 hours ago • Visible to anyone on or off LinkedIn\nSkyUp Airlines has signed a Total Cargo Management agreement with TCE, using the group's synergies to create an integrated cargo platform. TCE will provide technical support and commercial representation will be managed by ECS Group and Global GSA Group.\n\nSarah Scheibe, Managing Director of TCE said: \"By leveraging the combined expertise of ECS Group and Global GSA Group, we are building a highly responsive and scalable cargo platform.\"\n\nRead the full story at: https://lnkd.in/eQE4Jbps\n\nFollow Air Logistics International for the latest air cargo industry news.\n\n\nhashtag\n#aviation \nhashtag\n#aircargo "
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 7,
            "text": "Feed post number 8\nUniversal Aerospace Systems\nUniversal Aerospace Systems\n1,864 followers\n1,864 followers\n4h • \n \n4 hours ago • Visible to anyone on or off LinkedIn\nWe are Hiring: Sales Manager – Latin America\nLocation: Universal Aerospace Systems HQ – Deerfield Beach, Florida, USA\nWork Model: On-site with Hybrid Flexibility\n\nKey Responsibilities:\n- Drive sales growth across Latin America markets in line with company strategy\n- Develop and manage relationships with airlines, MROs, lessors, and trading partners\n- Drive new business initiatives to expand and strengthen our Latin America regional customer base\n- Lead commercial negotiations, pricing strategies, and contract closures\n- Monitor regional market trends, customer demand, and competitive activity\n- Work closely with internal teams"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 8,
            "text": "Feed post number 9\nMatthew Pinington reposted this\nTDA. (Touchdown Aviation)\nTDA. (Touchdown Aviation)\n21,042 followers\n21,042 followers\n1w • \n \n1 week ago • Visible to anyone on or off LinkedIn\nWe have a variety Widebody Airbus Radomes ready-to-go from multiple strategic TDA locations, including OEM NEW units! 🌍\n\nPN V53132110000 | A350 Radome | NEW\nPN F53132310001 | A330(neo) Radome | NEW\nPN F53132310000 | A330 Radome | REPAIRED\n\nLooking for one of these units or sourcing something specific? Our Sales team is ready to support your requirements! \n\nContact us now at sales@tda.aero or directly through our website at https://lnkd.in/eErhSmWm\n\n\n\nhashtag\n#TDA \nhashtag\n#Aviation \nhashtag\n#Airbus \nhashtag\n#Radome \nhashtag\n#ReadyToGo\n…more\nActivate to view larger image,\nActivate to view larger im"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 9,
            "text": "Feed post number 10\nSanad Khalil\nSanad Khalil\n   • 1st\nPremium • 1st\nChief Operating Officer | Aviation Industry Specialist | Expert in Aircraft Engine Maintenance | Aircraft Parts\nChief Operating Officer | Aviation Industry Specialist | Expert in Aircraft Engine Maintenance | Aircraft Parts\n11h • \n \n11 hours ago • Visible to anyone on or off LinkedIn\nHPC Blade list available in stock, sell in AR/Repairable or OH with lead time \n\nif Interested DM\n4\nNadine Techer-Eales and 3 others\n2 comments\nLike\nComment\nRepost\nSend"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 11,
            "text": "Feed post number 12\n路易斯 Dr. Luis Rivera , JD, LLM, Ph.D.\n路易斯 Dr. Luis Rivera , JD, LLM, Ph.D.\n • 1st\n1st\nFounder, President & Chief Executive Officer at Aircraft Sales, LLC\nFounder, President & Chief Executive Officer at Aircraft Sales, LLC\n4h • \n \n4 hours ago • Visible to anyone on or off LinkedIn\nA320 Foe Sale\nGeneral Dimensions\nOverall Length: 37.57 m (123 ft 3 in)\nWingspan (with sharklets, standard on neo and many ceo): 35.80 m (117 ft 5 in)\nHeight (tail): 11.76 m (38 ft 7 in)\nFuselage Width: 3.95 m (external); max cabin width 3.70 m (widest in single-aisle class for 6-abreast seating)\nCabin Length: ~27.51 m\nCapacity & Cabin\nTypical Seating (2-class): 150-180 passengers\nMaximum Seating (high-density, single-class): Up to 194 (neo) or 180 (ceo)\nCargo: Underfloor holds for LD3 containers"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 12,
            "text": "Feed post number 17\nSparrow Aviation Group, LLC.\nSparrow Aviation Group, LLC.\n1,189 followers\n1,189 followers\n1h • Edited • \n \n1 hour ago • Edited • Visible to anyone on or off LinkedIn\nNewsflash 🚨 Inventory is Moving Fast — Don't Miss Out!\n\nWe hope your week is off to a strong start. Parts from our recent aircraft acquisition are continuing to move quickly, with rotables, avionics, and airframe components heading out the door daily. Turnover is high — and availability is changing fast. What do you need before the month is up?\n\nWhether you're looking for serviceable, exchange, recertified, or select factory-new solutions, we're here to support your operational requirements when timing matters most. From transducers and small interior parts like latches or handles, all the way to APU sub-c"
        },
        {
            "selector": ".feed-shared-update-v2",
            "index": 13,
            "text": "Feed post number 18\nSeefin Aviation reposted this\nJames O'Shea\nJames O'Shea\n   • 1st\nVerified • 1st\nSeefinAviation.com - Aircraft Trading company and The ALMS Group for Reinsurance/Insurance of all your Aviation Risks\nSeefinAviation.com - Aircraft Trading company and The ALMS Group for Reinsurance/Insurance of all your Aviation Risks\n2w • \n \n2 weeks ago • Visible to anyone on or off LinkedIn\nClient looking to lease an engine \nPW4060-3 for B767 Aircraft\nConditions for the lease:\n1. Lease duration 1 year\n2. Monthly utilisation FA/FC = 300/60\n3. Jurisdiction Europe, China, Dubai\n\nhashtag\n#lease \nhashtag\n#engine \nhashtag\n#B767 \nhashtag\n#PW \nhashtag\n#PW4060\nPlease reply to Cian@SeefinAviation.com\n…more\nActivate to view larger image,\nActivate to view larger image,\n8\nMark Monelli and 7 others\n3 r"
        }
    ]
}

# 关键词列表 - 航材/发动机/起落架/飞机整机相关
keywords = {
    "航材": ["spare parts", "aircraft parts", "components", "rotables", "avionics", "airframe", "APU", "radome", "blades", "mount", "assembly"],
    "发动机": ["engine", "V2500", "CF6", "PW4060", "GTD-350", "turboshaft", "fan blades", "HPC blade", "engine mount"],
    "起落架": ["landing gear", "undercarriage", "gear", "brakes", "wheels"],
    "飞机整机": ["aircraft sale", "A320", "B767", "Embraer", "E-Jet", "aircraft for sale", "aircraft lease", "aircraft trading"],
    "维修服务": ["MRO", "maintenance", "repair", "overhaul", "OH", "AR", "serviceable"],
    "业务机会": ["wanted", "required", "available", "for sale", "for lease", "hiring", "looking for", "seeking"]
}

def analyze_post(post_text):
    """分析单个帖子，提取关键信息"""
    result = {
        "业务类型": [],
        "关键部件": [],
        "业务状态": "",
        "联系人信息": "",
        "业务价值评分": 0,
        "紧急程度": "低"
    }
    
    text_lower = post_text.lower()
    
    # 检测业务类型
    for category, words in keywords.items():
        for word in words:
            if word.lower() in text_lower:
                if category not in result["业务类型"]:
                    result["业务类型"].append(category)
    
    # 提取关键部件信息
    import re
    part_patterns = [
        r'P/N[:\s]*([A-Z0-9\-]+)',  # 零件号
        r'PN[:\s]*([A-Z0-9\-]+)',    # 零件号简写
        r'V2500', r'CF6', r'PW4060', r'GTD-350',  # 发动机型号
        r'A320', r'B767', r'Embraer', r'E170', r'E175', r'E190', r'E195',  # 飞机型号
        r'APU', r'Radome', r'Fan Blades', r'Engine Mount'  # 部件类型
    ]
    
    for pattern in part_patterns:
        matches = re.findall(pattern, post_text, re.IGNORECASE)
        for match in matches:
            if match and match not in result["关键部件"]:
                result["关键部件"].append(match)
    
    # 判断业务状态
    if any(word in text_lower for word in ["wanted", "required", "looking for", "seeking"]):
        result["业务状态"] = "需求"
    elif any(word in text_lower for word in ["available", "for sale", "for lease", "in stock"]):
        result["业务状态"] = "供应"
    elif "hiring" in text_lower or "招聘" in text_lower:
        result["业务状态"] = "招聘"
    else:
        result["业务状态"] = "信息"
    
    # 提取联系人信息
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'[\+\d\s\-\(\)]{10,}'
    
    emails = re.findall(email_pattern, post_text)
    phones = re.findall(phone_pattern, post_text)
    
    contact_info = []
    if emails:
        contact_info.append(f"邮箱: {emails[0]}")
    if phones:
        contact_info.append(f"电话: {phones[0]}")
    
    if contact_info:
        result["联系人信息"] = "; ".join(contact_info)
    
    # 计算业务价值评分 (1-5分)
    score = 1  # 基础分
    
    # 根据业务类型加分
    if len(result["业务类型"]) > 0:
        score += 1
    if len(result["业务类型"]) > 1:
        score += 1
    
    # 根据关键部件加分
    if len(result["关键部件"]) > 0:
        score += 1
    
    # 根据联系人信息加分
    if result["联系人信息"]:
        score += 1
    
    # 根据紧急程度调整
    urgent_words = ["immediate", "urgent", "紧急", "立即", "马上", "fast", "quick"]
    if any(word in text_lower for word in urgent_words):
        result["紧急程度"] = "高"
        score = min(5, score + 1)  # 紧急业务额外加分，但不超过5分
    elif result["业务状态"] in ["需求", "供应"]:
        result["紧急程度"] = "中"
    
    result["业务价值评分"] = min(5, score)  # 确保不超过5分
    
    return result

def extract_company_info(post_text):
    """从帖子中提取公司信息"""
    lines = post_text.split('\n')
    company_info = {
        "公司名称": "",
        "职位": "",
        "发布时间": ""
    }
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 提取公司名称 (通常在帖子开头)
        if i < 3 and len(line) < 100 and not line.startswith("Feed post"):
            if not company_info["公司名称"] and not any(word in line.lower() for word in ["followers", "hours ago", "minutes ago", "days ago", "weeks ago"]):
                company_info["公司名称"] = line
        
        # 提取职位信息
        if "@" in line and " at " in line:
            company_info["职位"] = line
        
        # 提取发布时间
        time_indicators = ["h •", "hours ago", "minutes ago", "days ago", "weeks ago", "• Edited •"]
        for indicator in time_indicators:
            if indicator in line:
                company_info["发布时间"] = line
                break
    
    return company_info

def main():
    """主函数"""
    print("开始分析LinkedIn帖子...")
    print(f"总帖子数: {posts_data['totalPosts']}")
    print(f"分析样本数: {len(posts_data['posts'])}")
    print("-" * 80)
    
    business_opportunities = []
    
    for i, post in enumerate(posts_data['posts']):
        post_text = post['text']
        print(f"\n帖子 #{i+1}:")
        print("-" * 40)
        
        # 提取公司信息
        company_info = extract_company_info(post_text)
        
        # 分析业务内容
        analysis = analyze_post(post_text)
        
        # 只保留有业务价值的帖子
        if analysis["业务价值评分"] >= 2 or len(analysis["业务类型"]) > 0:
            opportunity = {
                "序号": i + 1,
                "公司名称": company_info["公司名称"],
                "职位": company_info["职位"],
                "发布时间": company_info["发布时间"],
                "业务类型": ", ".join(analysis["业务类型"]),
                "关键部件": ", ".join(analysis["关键部件"][:3]),  # 只取前3个
                "业务状态": analysis["业务状态"],
                "联系人信息": analysis["联系人信息"],
                "业务价值评分": analysis["业务价值评分"],
                "紧急程度": analysis["紧急程度"],
                "摘要": post_text[:200] + "..." if len(post_text) > 200 else post_text
            }
            business_opportunities.append(opportunity)
            
            # 打印分析结果
            print(f"公司: {company_info['公司名称']}")
            print(f"业务类型: {', '.join(analysis['业务类型'])}")
            print(f"关键部件: {', '.join(analysis['关键部件'][:3])}")
            print(f"业务状态: {analysis['业务状态']}")
            print(f"业务价值评分: {analysis['业务价值评分']}/5")
            print(f"紧急程度: {analysis['紧急程度']}")
            if analysis["联系人信息"]:
                print(f"联系人: {analysis['联系人信息']}")
    
    print("\n" + "=" * 80)
    print("分析完成!")
    print(f"发现业务机会: {len(business_opportunities)} 个")
    
    # 按业务价值评分排序
    business_opportunities.sort(key=lambda x: x["业务价值评分"], reverse=True)
    
    # 生成CSV文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"linkedin_business_opportunities_{timestamp}.csv"
    
    import csv
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ["序号", "公司名称", "职位", "发布时间", "业务类型", "关键部件", "业务状态", 
                     "联系人信息", "业务价值评分", "紧急程度", "摘要"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for opp in business_opportunities:
            writer.writerow(opp)
    
    print(f"CSV文件已生成: {csv_filename}")
    
    # 生成分析报告
    report_filename = f"linkedin_analysis_report_{timestamp}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(f"# LinkedIn业务机会分析报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 分析概况\n")
        f.write(f"- 分析帖子总数: {posts_data['totalPosts']}\n")
        f.write(f"- 发现业务机会: {len(business_opportunities)} 个\n")
        f.write(f"- 高价值机会(评分≥4): {sum(1 for opp in business_opportunities if opp['业务价值评分'] >= 4)} 个\n")
        f.write(f"- 紧急机会: {sum(1 for opp in business_opportunities if opp['紧急程度'] == '高')} 个\n\n")
        
        f.write(f"## 业务类型分布\n")
        type_counts = {}
        for opp in business_opportunities:
            types = opp["业务类型"].split(", ")
            for t in types:
                if t:
                    type_counts[t] = type_counts.get(t, 0) + 1
        
        for t, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {t}: {count} 个\n")
        
        f.write(f"\n## 高价值业务机会 (评分≥4)\n")
        f.write(f"| 序号 | 公司名称 | 业务类型 | 关键部件 | 业务状态 | 评分 | 紧急程度 |\n")
        f.write(f"|------|----------|----------|----------|----------|------|----------|\n")
        
        high_value_opps = [opp for opp in business_opportunities if opp["业务价值评分"] >= 4]
        for opp in high_value_opps[:10]:  # 只显示前10个
            f.write(f"| {opp['序号']} | {opp['公司名称']} | {opp['业务类型']} | {opp['关键部件']} | {opp['业务状态']} | {opp['业务价值评分']} | {opp['紧急程度']} |\n")
        
        f.write(f"\n## 所有业务机会\n")
        for opp in business_opportunities:
            f.write(f"\n### {opp['序号']}. {opp['公司名称']}\n")
            f.write(f"- **业务类型**: {opp['业务类型']}\n")
            f.write(f"- **关键部件**: {opp['关键部件']}\n")
            f.write(f"- **业务状态**: {opp['业务状态']}\n")
            f.write(f"- **业务价值评分**: {opp['业务价值评分']}/5\n")
            f.write(f"- **紧急程度**: {opp['紧急程度']}\n")
            if opp["联系人信息"]:
                f.write(f"- **联系人**: {opp['联系人信息']}\n")
            f.write(f"- **摘要**: {opp['摘要']}\n")
    
    print(f"分析报告已生成: {report_filename}")
    
    # 复制到桌面
    import shutil
    import os
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "LINKEDIN BUSINESS")
    os.makedirs(desktop_path, exist_ok=True)
    
    shutil.copy(csv_filename, os.path.join(desktop_path, csv_filename))
    shutil.copy(report_filename, os.path.join(desktop_path, report_filename))
    
    print(f"文件已复制到桌面: {desktop_path}")
    
    return business_opportunities

if __name__ == "__main__":
    opportunities = main()