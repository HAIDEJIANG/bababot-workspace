#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 高质量信息采集 - 3 月 6 日整改版
访问真实公司页面，采集真实帖子数据
"""

import csv
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 设置 UTF-8 输出
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 目标公司列表（航空业务相关）
TARGET_COMPANIES = [
    {"name": "StandardAero", "url": "https://www.linkedin.com/company/standardaero/posts/"},
    {"name": "GA Telesis", "url": "https://www.linkedin.com/company/gatelesis/posts/"},
    {"name": "Textron Aviation", "url": "https://www.linkedin.com/company/textron-aviation/posts/"},
    {"name": "Lufthansa Technik", "url": "https://www.linkedin.com/company/lufthansa-technik/posts/"},
    {"name": "Rolls-Royce", "url": "https://www.linkedin.com/company/rolls-royce/posts/"},
    {"name": "GE Aerospace", "url": "https://www.linkedin.com/company/ge-aerospace/posts/"},
    {"name": "Honeywell Aerospace", "url": "https://www.linkedin.com/company/honeywell-aerospace/posts/"},
    {"name": "Pratt & Whitney", "url": "https://www.linkedin.com/company/pratt-whitney/posts/"},
    {"name": "Safran", "url": "https://www.linkedin.com/company/safran/posts/"},
    {"name": "Airbus", "url": "https://www.linkedin.com/company/airbus/posts/"},
]

AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce", "ge90", "leap",
    "landing gear", "nlg", "mlg", "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787",
    "part", "component", "inventory", "sale", "lease", "leasing", "available",
    "aviation", "aerospace", "AOG", "FAA", "EASA"
]

def run_browser_cmd(cmd_list, timeout=60):
    """执行 browser 命令"""
    try:
        cmd = ["openclaw", "browser"] + cmd_list + ["--json"]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        if p.returncode == 0 and p.stdout.strip():
            try:
                return json.loads(p.stdout.strip())
            except:
                return {"raw": p.stdout.strip()}
        return {}
    except Exception as e:
        print(f"  命令失败：{e}")
        return {}

def open_url(url):
    """打开 URL"""
    result = run_browser_cmd(["open", url], timeout=30)
    return result.get("targetId")

def wait_for_page_load(seconds=5):
    """等待页面加载"""
    time.sleep(seconds)

def get_snapshot(target_id=None, limit=600):
    """获取页面快照"""
    cmd = ["snapshot", "--format", "ai", "--limit", str(limit)]
    if target_id:
        cmd.extend(["--target-id", target_id])
    result = run_browser_cmd(cmd, timeout=90)
    return result.get("snapshot", "")

def extract_posts_from_snapshot(snapshot_text, source_url, company_name):
    """从快照中提取帖子"""
    posts = []
    
    # 清理 UI 元素标记
    text = snapshot_text
    text = re.sub(r'\[ref=e\d+\]', '', text)
    text = re.sub(r'\[cursor=pointer\]', '', text)
    text = re.sub(r'\[button\]', '', text)
    text = re.sub(r'\[link\]', '', text)
    text = re.sub(r'\[img\]', '', text)
    
    lines = text.split('\n')
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
                if len(current_post['content']) > 50:  # 内容长度要求
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
            
            # 累积内容（跳过明显的 UI 元素）
            if len(line_stripped) > 30:
                # 跳过 UI 元素行
                if any(x in line_stripped.lower() for x in ['generic', 'heading', 'region', 'button', 'link', 'img', 'view', 'followers', 'see more']):
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

def is_aviation_related(content):
    """判断是否与航空相关"""
    content_lower = content.lower()
    return any(kw in content_lower for kw in AVIATION_KEYWORDS)

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

def validate_post(post):
    """验证帖子质量"""
    errors = []
    
    if not post.get('author_name') or post['author_name'] == 'Unknown':
        errors.append("author_name missing")
    
    content = post.get('content', '')
    if 'ref=e' in content or 'cursor=pointer' in content:
        errors.append("content contains UI elements")
    
    # 检查乱码
    business_type = post.get('business_type', '')
    if has_garbage_chars(business_type):
        errors.append("encoding issue in business_type")
    
    source_url = post.get('source_url', '')
    if not source_url.startswith('https://www.linkedin.com/'):
        errors.append("invalid source_url")
    
    if len(content) < 50:
        errors.append("content too short")
    
    return len(errors) == 0, errors

def has_garbage_chars(text):
    """检查是否有乱码"""
    if not text:
        return False
    # 检查是否有异常的 Unicode 字符
    garbage_pattern = re.compile(r'[\ufffd\u0000-\u001f]')
    return bool(garbage_pattern.search(text))

def format_posts(posts, batch_id, company_name):
    """格式化帖子为标准格式"""
    formatted = []
    
    for i, post in enumerate(posts, 1):
        content = post.get('content', '')[:2000]
        business_type = classify_business_type(content)
        
        # 提取联系方式
        email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
        contact = email_match.group() if email_match else ""
        
        formatted.append({
            "post_id": f"LI_REAL_{batch_id}_{company_name.replace(' ', '_')}_{i:03d}",
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

def save_posts(posts, batch_id):
    """保存帖子到 CSV"""
    if not posts:
        print("⚠️ 没有数据可保存")
        return 0
    
    fieldnames = [
        "post_id", "timestamp", "author_name", "author_url", "company", "position",
        "content", "business_type", "business_value_score", "urgency", "has_contact",
        "contact_info", "post_time", "reactions", "comments", "reposts", "has_image",
        "image_content", "source_url", "batch_id", "collected_at", "content_type", "tags"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUTPUT_DIR / f"LinkedIn_Business_Posts_真实采集_{timestamp}.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    print(f"✅ 保存成功：{csv_path.name}")
    print(f"   总计：{len(posts)} 条帖子")
    
    return len(posts)

def main():
    print("=" * 60)
    print("LinkedIn 高质量信息采集 - 3 月 6 日整改版")
    print("=" * 60)
    
    batch_id = datetime.now().strftime("%Y%m%d_%H%M")
    all_posts = []
    quality_stats = {"valid": 0, "invalid": 0}
    
    for i, company in enumerate(TARGET_COMPANIES, 1):
        print(f"\n[{i}/{len(TARGET_COMPANIES)}] 采集：{company['name']}")
        print(f"   URL: {company['url']}")
        
        # 打开公司页面
        target_id = open_url(company['url'])
        if not target_id:
            print(f"   ❌ 无法打开页面")
            continue
        
        # 等待页面加载
        print("   等待页面加载...")
        wait_for_page_load(8)
        
        # 获取快照
        print("   获取页面快照...")
        snapshot = get_snapshot(target_id, limit=800)
        
        if not snapshot:
            print("   ⚠️ 快照为空")
            continue
        
        # 提取帖子
        raw_posts = extract_posts_from_snapshot(snapshot, company['url'], company['name'])
        print(f"   原始帖子数：{len(raw_posts)}")
        
        if raw_posts:
            # 格式化
            formatted = format_posts(raw_posts, batch_id, company['name'])
            
            # 质量验证
            valid_posts = []
            for post in formatted:
                is_valid, errors = validate_post(post)
                if is_valid:
                    valid_posts.append(post)
                    quality_stats["valid"] += 1
                else:
                    quality_stats["invalid"] += 1
                    print(f"     无效帖子：{errors}")
            
            all_posts.extend(valid_posts)
            print(f"   ✅ 有效帖子：{len(valid_posts)} 条")
        else:
            print("   ⚠️ 未找到帖子")
        
        # 短暂等待
        time.sleep(2)
    
    # 去重（基于 content 前 100 字符）
    seen = set()
    unique_posts = []
    for post in all_posts:
        key = post['content'][:100]
        if key not in seen:
            seen.add(key)
            unique_posts.append(post)
    
    print(f"\n{'='*60}")
    print(f"📊 采集统计:")
    print(f"   总帖子数：{len(all_posts)}")
    print(f"   去重后：{len(unique_posts)}")
    print(f"   质量合格：{quality_stats['valid']}")
    print(f"   质量不合格：{quality_stats['invalid']}")
    
    # 保存
    if unique_posts:
        save_posts(unique_posts, batch_id)
        
        # 生成报告
        generate_report(unique_posts, batch_id, quality_stats)
    else:
        print("\n❌ 没有有效数据可保存")
    
    print("\n✅ 采集任务完成!")

def generate_report(posts, batch_id, quality_stats):
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
    
    report = f"""# LinkedIn 高质量信息采集报告

**采集时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**批次 ID**: {batch_id}

## 采集统计

| 指标 | 数值 |
|------|------|
| 总采集帖子数 | {len(posts)} |
| 质量合格率 | {quality_stats['valid']/(quality_stats['valid']+quality_stats['invalid'])*100:.1f}% |
| 目标公司数 | {len(TARGET_COMPANIES)} |

## 业务类型分布

"""
    
    for bt, count in sorted(business_types.items(), key=lambda x: -x[1]):
        report += f"- {bt}: {count} 条\n"
    
    report += "\n## 公司分布\n\n"
    
    for company, count in sorted(companies.items(), key=lambda x: -x[1]):
        report += f"- {company}: {count} 条\n"
    
    report += f"""
## 质量标准

- ✅ author_name: 真实公司名（无 Unknown）
- ✅ content: 干净的业务文本（无 UI 元素）
- ✅ business_type: 中文业务分类（无乱码）
- ✅ source_url: 真实 LinkedIn URL

## 输出文件

- `LinkedIn_Business_Posts_真实采集_{batch_id}.csv` - 新采集数据
- `LinkedIn_Business_Posts_Master_Table_CLEAN.csv` - 更新后的总表（需运行合并脚本）

---
*报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存：{report_path.name}")

if __name__ == "__main__":
    main()
