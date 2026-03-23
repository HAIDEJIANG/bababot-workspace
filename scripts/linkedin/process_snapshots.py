#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 帖子数据提取器 - 批量处理快照文件
从所有快照文件中提取帖子并保存为 CSV
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()

AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce", "ge90", "leap",
    "landing gear", "nlg", "mlg", "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787",
    "part", "component", "inventory", "sale", "lease", "leasing", "available",
    "aviation", "aerospace", "AOG", "FAA", "EASA"
]

def extract_posts_from_snapshot(snapshot_text, source_url, company_name):
    """从快照中提取帖子"""
    posts = []
    
    # 如果是 JSON 字符串，尝试解析
    if isinstance(snapshot_text, str):
        # 检查是否是 JSON 格式
        if snapshot_text.strip().startswith('{'):
            try:
                data = json.loads(snapshot_text)
                # 如果是完整的 JSON 响应，提取 snapshot 字段
                if isinstance(data, dict):
                    if 'snapshot' in data:
                        snapshot_text = data['snapshot']
                    elif 'text' in data:
                        snapshot_text = data['text']
            except:
                pass
    
    lines = str(snapshot_text).split('\n')
    current_post = None
    content_buffer = []
    in_post = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # 检测新帖子开始
        if 'Feed post number' in line_stripped or 'Post number' in line_stripped:
            # 保存之前的帖子
            if current_post and content_buffer:
                current_post['content'] = ' '.join(content_buffer).strip()
                if len(current_post['content']) > 50:
                    posts.append(current_post)
            
            # 开始新帖子
            current_post = {
                'author_name': company_name,
                'content': '',
                'post_time': 'Unknown',
                'source_url': source_url
            }
            content_buffer = []
            in_post = True
        
        elif in_post:
            # 提取时间信息
            time_match = re.search(r'(\d+\s*[hdwm]\s*ago|\d+\s*[小时天周月]\s*前)', line_stripped, re.IGNORECASE)
            if time_match:
                current_post['post_time'] = time_match.group(1).replace(' ', '')
            
            # 累积内容（跳过 UI 元素）
            if len(line_stripped) > 30:
                # 跳过 UI 元素行
                skip_patterns = ['generic', 'heading', 'region', 'button', 'link', 'img', 'view.*followers', 
                               'See all', 'Show more', 'ref=e', 'cursor=pointer', 'aria-', 'targetId',
                               'About', 'Accessibility', 'Help Center', 'Privacy', 'Ad Choices']
                if any(x in line_stripped.lower() for x in skip_patterns):
                    continue
                
                # 跳过空行或纯符号
                if re.match(r'^[\s\W]+$', line_stripped):
                    continue
                
                # 添加有效内容
                content_buffer.append(line_stripped)
    
    # 添加最后一个帖子
    if current_post and content_buffer:
        current_post['content'] = ' '.join(content_buffer).strip()
        if len(current_post['content']) > 50:
            posts.append(current_post)
    
    return posts

def classify_business_type(content):
    """分类业务类型（中文）"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["cfm56", "v2500", "ge90", "pw4000", "leap", "engine", "engineer"]):
        return "航材供应 - 发动机组件/LLP/消耗件"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear", "起落架"]):
        return "起落架销售/租赁"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental", "ACMI", "租赁"]):
        return "飞机/发动机租赁"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair", "EASA", "FAA", "维修"]):
        return "MRO 服务"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "citation", "jet", "飞机"]):
        return "飞机整机销售/租赁"
    elif any(kw in content_lower for kw in ["part", "component", "inventory", "rotable", "航材"]):
        return "航材销售"
    elif any(kw in content_lower for kw in ["charter", "evacuation", "cargo", "freighter", "货运"]):
        return "包机/货运服务"
    elif any(kw in content_lower for kw in ["conference", "event", "ISTAT", "expo", "展会"]):
        return "航空展会/会议"
    elif any(kw in content_lower for kw in ["flight", "suspended", "cancelled", "route", "航班"]):
        return "航班动态"
    else:
        return "航空相关"

def format_posts(posts, batch_id, company_name):
    """格式化帖子为标准格式"""
    formatted = []
    
    for i, post in enumerate(posts, 1):
        content = post.get('content', '')[:2000]
        business_type = classify_business_type(content)
        
        # 提取联系方式
        email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
        contact = email_match.group() if email_match else ""
        
        # 生成 post_id
        safe_company = company_name.replace(' ', '_').replace('&', 'and').replace('-', '_')
        post_id = f"LI_REAL_{batch_id}_{safe_company}_{i:03d}"
        
        formatted.append({
            "post_id": post_id,
            "timestamp": datetime.now().isoformat(),
            "author_name": post.get('author_name', company_name),
            "author_url": "",
            "company": company_name,
            "position": "",
            "content": content,
            "business_type": business_type,
            "business_value_score": 7 if contact else 5,
            "urgency": "高" if contact else "中",
            "has_contact": bool(contact),
            "contact_info": contact,
            "post_time": post.get('post_time', 'Unknown'),
            "reactions": 0,
            "comments": 0,
            "reposts": 0,
            "has_image": False,
            "image_content": "",
            "source_url": post.get('source_url', ''),
            "batch_id": batch_id,
            "collected_at": datetime.now().isoformat(),
            "content_type": "text",
            "tags": ",".join([kw for kw in AVIATION_KEYWORDS[:10] if kw.lower() in content.lower()])
        })
    
    return formatted

def validate_post(post):
    """验证帖子质量"""
    errors = []
    
    if not post.get('author_name') or post['author_name'] == 'Unknown':
        errors.append("author_name missing")
    
    content = post.get('content', '')
    if 'ref=e' in content or 'cursor=pointer' in content:
        errors.append("content contains UI elements")
    
    source_url = post.get('source_url', '')
    if not source_url.startswith('https://www.linkedin.com/'):
        errors.append("invalid source_url")
    
    if len(content) < 50:
        errors.append("content too short")
    
    return len(errors) == 0, errors

def main():
    print("=" * 60)
    print("LinkedIn 帖子数据提取 - 批量处理")
    print("=" * 60)
    
    batch_id = datetime.now().strftime("%Y%m%d_%H%M")
    all_posts = []
    quality_stats = {"valid": 0, "invalid": 0}
    
    # 查找所有快照文件
    snapshot_files = list(OUTPUT_DIR.glob("snapshot_*.json"))
    print(f"\n找到 {len(snapshot_files)} 个快照文件")
    
    for snapshot_file in snapshot_files:
        print(f"\n处理：{snapshot_file.name}")
        
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            company_name = data.get('company', snapshot_file.stem.replace('snapshot_', '').replace(f'_{batch_id}', ''))
            source_url = data.get('url', '')
            snapshot = data.get('snapshot', '')
            
            # 提取帖子
            raw_posts = extract_posts_from_snapshot(snapshot, source_url, company_name)
            print(f"  原始帖子数：{len(raw_posts)}")
            
            if raw_posts:
                # 格式化
                formatted = format_posts(raw_posts, batch_id, company_name)
                
                # 质量验证
                valid_posts = []
                for post in formatted:
                    is_valid, errors = validate_post(post)
                    if is_valid:
                        valid_posts.append(post)
                        quality_stats["valid"] += 1
                    else:
                        quality_stats["invalid"] += 1
                        print(f"    无效：{errors} - {post['post_id']}")
                
                all_posts.extend(valid_posts)
                print(f"  有效帖子：{len(valid_posts)} 条")
        
        except Exception as e:
            print(f"  错误：{e}")
    
    # 去重（基于 content 前 100 字符）
    seen = set()
    unique_posts = []
    for post in all_posts:
        key = post['content'][:100]
        if key not in seen:
            seen.add(key)
            unique_posts.append(post)
    
    print(f"\n{'='*60}")
    print(f"统计:")
    print(f"  总帖子数：{len(all_posts)}")
    print(f"  去重后：{len(unique_posts)}")
    print(f"  质量合格：{quality_stats['valid']}")
    print(f"  质量不合格：{quality_stats['invalid']}")
    
    # 保存
    if unique_posts:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = OUTPUT_DIR / f"LinkedIn_Business_Posts_真实采集_{timestamp}.csv"
        
        fieldnames = [
            "post_id", "timestamp", "author_name", "author_url", "company", "position",
            "content", "business_type", "business_value_score", "urgency", "has_contact",
            "contact_info", "post_time", "reactions", "comments", "reposts", "has_image",
            "image_content", "source_url", "batch_id", "collected_at", "content_type", "tags"
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_posts)
        
        print(f"\n[OK] 保存成功：{csv_path.name}")
        print(f"     总计：{len(unique_posts)} 条帖子")
        
        # 生成报告
        generate_report(unique_posts, batch_id, quality_stats, csv_path.name)
    else:
        print("\n[WARN] 没有有效数据可保存")
    
    print("\n" + "=" * 60)
    print("提取完成!")
    print("=" * 60)

def generate_report(posts, batch_id, quality_stats, csv_filename):
    """生成采集报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = OUTPUT_DIR / f"LinkedIn_Collection_Report_{timestamp}.md"
    
    # 统计业务类型
    business_types = {}
    for post in posts:
        bt = post.get('business_type', 'Unknown')
        business_types[bt] = business_types.get(bt, 0) + 1
    
    # 统计公司分布
    companies = {}
    for post in posts:
        company = post.get('company', 'Unknown')
        companies[company] = companies.get(company, 0) + 1
    
    total = quality_stats['valid'] + quality_stats['invalid']
    quality_rate = (quality_stats['valid'] / total * 100) if total > 0 else 0
    
    report = f"""# LinkedIn 高质量信息采集报告

**采集时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**批次 ID**: {batch_id}

## 采集统计

| 指标 | 数值 |
|------|------|
| 总采集帖子数 | {len(posts)} |
| 质量合格率 | {quality_rate:.1f}% |
| 目标公司数 | {len(companies)} |
| 输出文件 | {csv_filename} |

## 业务类型分布

"""
    
    for bt, count in sorted(business_types.items(), key=lambda x: -x[1]):
        report += f"- {bt}: {count} 条\n"
    
    report += "\n## 公司分布\n\n"
    
    for company, count in sorted(companies.items(), key=lambda x: -x[1]):
        report += f"- {company}: {count} 条\n"
    
    report += f"""
## 质量标准

- [x] author_name: 真实公司名（无 Unknown）
- [x] content: 干净的业务文本（无 UI 元素）
- [x] business_type: 中文业务分类（无乱码）
- [x] source_url: 真实 LinkedIn URL

## 下一步

1. 运行合并脚本更新总表
2. 验证数据质量
3. 分析业务机会

---
*报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] 报告已保存：{report_path.name}")

if __name__ == "__main__":
    main()
