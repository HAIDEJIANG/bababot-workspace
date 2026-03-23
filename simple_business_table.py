#!/usr/bin/env python3
"""
简化版业务信息表创建器
"""

import json
import csv
import os
from datetime import datetime
import re

def create_business_info_table():
    """创建业务信息表"""
    
    # 示例数据
    sample_posts = [
        {
            "author": "John Smith",
            "company": "ABC Aviation",
            "content": "紧急采购CFM56-7B发动机PN: 123-456，需要现货，价格USD 500,000，联系方式: WhatsApp +86 13800138000",
            "url": "https://www.linkedin.com/feed/update/123",
            "time": "2小时前"
        },
        {
            "author": "李经理",
            "company": "航空材料公司",
            "content": "供应A320起落架，件号：335-010-401-0，有现货，价格优惠，联系微信: aviation_parts",
            "url": "https://www.linkedin.com/feed/update/456",
            "time": "5小时前"
        },
        {
            "author": "航空发动机专家",
            "company": "MRO服务中心",
            "content": "提供V2500发动机大修服务，专业团队，快速交付，联系邮箱: service@mro.com",
            "url": "https://www.linkedin.com/feed/update/789",
            "time": "1天前"
        },
        {
            "author": "飞机交易经纪人",
            "company": "国际航空资产",
            "content": "出售B737-800飞机整机，2015年制造，总飞行时间25,000小时，价格面议，联系邮箱: aircraft@global.com",
            "url": "https://www.linkedin.com/feed/update/101",
            "time": "3天前"
        },
        {
            "author": "航材供应商",
            "company": "全球航材供应",
            "content": "大量航材库存，包括A320、B737系列零件，PN齐全，欢迎询价RFQ，邮箱: sales@parts.com",
            "url": "https://www.linkedin.com/feed/update/112",
            "time": "1周前"
        }
    ]
    
    # 生成50条数据
    all_posts = []
    for i in range(50):
        post_index = i % len(sample_posts)
        post = sample_posts[post_index].copy()
        post["content"] = f"[示例{i+1}] {post['content']}"
        all_posts.append(post)
    
    # 分析业务信息
    business_posts = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for idx, post in enumerate(all_posts, 1):
        content = post["content"]
        
        # 简单业务分析
        business_types = []
        if "发动机" in content:
            business_types.append("发动机")
        if "起落架" in content:
            business_types.append("起落架")
        if "飞机整机" in content or "飞机" in content:
            business_types.append("飞机整机")
        if "航材" in content:
            business_types.append("航材")
        if "APU" in content:
            business_types.append("APU")
        if "MRO" in content or "维修" in content:
            business_types.append("MRO服务")
        
        # 提取联系方式
        contacts = []
        if "WhatsApp" in content:
            contacts.append("WhatsApp: " + re.findall(r'WhatsApp[:\s]*([+\d\s\-]+)', content)[0])
        if "微信" in content:
            contacts.append("微信: " + re.findall(r'微信[:\s]*([a-zA-Z0-9_\-]+)', content)[0])
        if "@" in content:
            emails = re.findall(r'[\w\.\-]+@[\w\.\-]+\.\w+', content)
            contacts.extend(emails)
        
        # 业务价值评分
        score = 1
        if "USD" in content or "价格" in content:
            score += 1
        if contacts:
            score += 1
        if "PN" in content or "件号" in content:
            score += 1
        if "现货" in content or "库存" in content:
            score += 1
        if "紧急" in content:
            score += 1
        
        # 跟进建议
        if "采购" in content or "需要" in content:
            followup = "主动联系提供报价"
        elif "出售" in content or "供应" in content:
            followup = "询价了解详情"
        elif "紧急" in content:
            followup = "立即联系，高优先级"
        else:
            followup = "常规跟进，建立联系"
        
        business_post = {
            "ID": f"BI{timestamp}_{idx:03d}",
            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "发帖人": post["author"],
            "公司/职位": post["company"],
            "帖子内容摘要": content[:200],
            "帖子链接": post["url"],
            "发帖时间": post["time"],
            "业务类型": ", ".join(business_types) if business_types else "其他",
            "联系方式": ", ".join(contacts[:3]),
            "业务价值评分": min(score, 5),
            "跟进建议": followup,
            "跟进状态": "待跟进"
        }
        
        business_posts.append(business_post)
    
    # 保存到文件
    output_dir = "LinkedIn_Business_Info"
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV文件
    csv_file = os.path.join(output_dir, f"business_info_{timestamp}.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        if business_posts:
            writer = csv.DictWriter(f, fieldnames=business_posts[0].keys())
            writer.writeheader()
            writer.writerows(business_posts)
    
    # JSON文件
    json_file = os.path.join(output_dir, f"business_info_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(business_posts, f, ensure_ascii=False, indent=2)
    
    # 生成统计
    biz_type_dist = {}
    for post in business_posts:
        types = post["业务类型"].split(", ")
        for t in types:
            if t:
                biz_type_dist[t] = biz_type_dist.get(t, 0) + 1
    
    high_value = len([p for p in business_posts if p["业务价值评分"] >= 4])
    
    print("=" * 60)
    print("业务信息表创建完成")
    print("=" * 60)
    print(f"总业务信息数: {len(business_posts)}")
    print(f"业务类型分布: {biz_type_dist}")
    print(f"高价值信息(评分≥4): {high_value}条")
    print(f"CSV文件: {csv_file}")
    print(f"JSON文件: {json_file}")
    print()
    print("前5条业务信息:")
    for i, post in enumerate(business_posts[:5], 1):
        print(f"  {i}. [{post['ID']}] {post['发帖人']} - {post['业务类型']}")
        print(f"     评分: {post['业务价值评分']}/5, 跟进: {post['跟进建议']}")
        print(f"     联系方式: {post['联系方式']}")
    print()
    print("下一步行动:")
    print("  1. 使用业务信息表进行系统化跟进")
    print("  2. 重点关注高价值(评分≥4)业务")
    print("  3. 定期更新数据，建立持续收集机制")

if __name__ == "__main__":
    create_business_info_table()