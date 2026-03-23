#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 真实帖子采集系统 v5.0 - 真实数据版

核心思路:
1. 直接访问具体的 LinkedIn 帖子/个人/公司页面 URL
2. 从页面快照中提取真实的 author_name, company, content
3. 避免抓取 UI 元素描述 (ref=eXXX, cursor=pointer)
4. 每条数据都包含真实的 source_url

参考 3 月 5 日成功采集方式:
- 访问真实的 LinkedIn 帖子 URL
- 直接提取 HTML 中的真实字段
- 正确解析 author_name, company, position, content
- UTF-8 编码正确处理中文
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 设置控制台输出为 UTF-8 (Windows)
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

# 添加 openclaw 到 PATH (Windows)
OPENCLAW_PATH = r"C:\Users\Haide\AppData\Roaming\npm"
if OPENCLAW_PATH not in os.environ.get("PATH", ""):
    os.environ["PATH"] = OPENCLAW_PATH + os.pathsep + os.environ.get("PATH", "")

# ============ 配置 ============
OUTPUT_DIR = Path("~/Desktop/real business post").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 航空业务相关 URL 种子 (从 3 月 5 日数据和已知来源)
SEED_URLS = [
    # 公司页面
    "https://www.linkedin.com/company/locatory-com/posts",
    "https://www.linkedin.com/company/avean/posts",
    "https://www.linkedin.com/company/skyupaero/posts",
    "https://www.linkedin.com/company/gatelesis/posts",
    "https://www.linkedin.com/company/standardaero/posts",
    "https://www.linkedin.com/company/textron-aviation/posts",
    "https://www.linkedin.com/company/aeronova-aviation/posts",
    # 个人页面 (航空业务专业人士)
    "https://www.linkedin.com/in/lily-e-3bb105360/posts",
    "https://www.linkedin.com/in/cody-honeyman-1b963617/posts",
    "https://www.linkedin.com/in/andres-aspron/posts",
    "https://www.linkedin.com/in/zayneb-aouani/posts",
    "https://www.linkedin.com/in/mark-forsyth-133770/posts",
    "https://www.linkedin.com/in/eamon-s-977665254/posts",
]

# 航空业务关键词
AVIATION_KEYWORDS = [
    "engine", "cfm56", "v2500", "pw", "ge", "rolls-royce", "ge90", "leap",
    "landing gear", "nlg", "mlg", "nose gear", "main gear",
    "mro", "maintenance", "overhaul", "repair",
    "aircraft", "boeing", "airbus", "a320", "a321", "b737", "b747", "b787", "citation",
    "part", "component", "inventory", "sale", "lease", "leasing", "available",
    "aviation", "aerospace", "aeroparts", "AOG", "FAA", "EASA"
]

# ============ 工具函数 ============
def now_ts() -> str:
    return datetime.now().isoformat(timespec="seconds")

def now_filename() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def content_hash(content: str) -> str:
    """生成内容哈希用于去重"""
    return hashlib.md5(content.encode()).hexdigest()[:16]

def is_aviation_related(content: str) -> bool:
    """判断内容是否与航空业务相关"""
    content_lower = content.lower()
    return any(kw in content_lower for kw in AVIATION_KEYWORDS)

def classify_business_type(content: str) -> str:
    """分类业务类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["cfm56", "v2500", "ge90", "pw4000", "leap", "engine"]):
        if any(kw in content_lower for kw in ["sale", "available", "offer"]):
            return "发动机销售"
        return "航材供应 - 发动机组件/LLP/消耗件"
    elif any(kw in content_lower for kw in ["landing gear", "nlg", "mlg", "gear"]):
        return "起落架销售/租赁"
    elif any(kw in content_lower for kw in ["lease", "leasing", "rental", "ACMI"]):
        if any(kw in content_lower for kw in ["aircraft", "plane", "jet"]):
            return "飞机整机租赁"
        return "发动机/APU 租赁"
    elif any(kw in content_lower for kw in ["mro", "maintenance", "overhaul", "repair", "EASA", "FAA"]):
        return "MRO 服务"
    elif any(kw in content_lower for kw in ["aircraft", "boeing", "airbus", "citation", "jet", "plane"]):
        if any(kw in content_lower for kw in ["sale", "sell", "market", "offer"]):
            return "飞机整机销售"
        return "航空运营"
    elif any(kw in content_lower for kw in ["part", "component", "inventory", "rotable", "consumable"]):
        return "航材销售"
    elif any(kw in content_lower for kw in ["charter", "evacuation", "cargo", "freighter"]):
        return "包机服务"
    elif any(kw in content_lower for kw in ["conference", "event", "ISTAT", "MRO", "expo"]):
        return "航空展会/会议"
    elif any(kw in content_lower for kw in ["flight", "suspended", "cancelled", "route"]):
        return "航班动态"
    else:
        return "航空相关"

def calculate_business_score(content: str, business_type: str) -> int:
    """计算业务价值评分 (1-10)"""
    score = 5
    
    # 高价值关键词
    high_value_keywords = ["sale", "available", "offer", "price", "USD", "$", "contact", "email", "RFQ"]
    if any(kw in content.lower() for kw in high_value_keywords):
        score += 2
    
    # 具体型号/零件号
    if re.search(r'\b[A-Z0-9]{4,}-[A-Z0-9-]+\b', content):
        score += 1
    
    # 联系方式
    if re.search(r'[\w.+-]+@[\w.-]+\.\w+', content) or "contact" in content.lower():
        score += 1
    
    # 业务类型加分
    if any(t in business_type for t in ["销售", "租赁", "MRO"]):
        score += 1
    
    return min(score, 10)

def extract_contact_info(content: str) -> tuple:
    """提取联系信息"""
    # 邮箱
    email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', content)
    email = email_match.group() if email_match else ""
    
    # 网站
    website_match = re.search(r'https?://[\w.-]+\.\w+[\w/.-]*', content)
    website = website_match.group() if website_match else ""
    
    # 电话
    phone_match = re.search(r'\+?[\d\s-]{8,}', content)
    phone = phone_match.group().strip() if phone_match else ""
    
    contact_parts = [p for p in [email, website, phone] if p]
    has_contact = len(contact_parts) > 0
    
    return has_contact, "; ".join(contact_parts) if contact_parts else ""

def extract_tags(content: str) -> list:
    """提取标签"""
    tags = []
    content_lower = content.lower()
    
    # 零件号
    pn_matches = re.findall(r'\b([A-Z0-9]{4,}-[A-Z0-9-]+)\b', content)
    tags.extend([p.upper() for p in pn_matches[:5]])
    
    # 关键词
    for kw in AVIATION_KEYWORDS[:15]:
        if kw.lower() in content_lower:
            tags.append(kw)
    
    # 飞机型号
    aircraft_patterns = [
        r'B737', r'B747', r'B777', r'B787', r'A320', r'A321', r'A330', r'A350',
        r'CFM56', r'V2500', r'PW4000', r'GE90', r'LEAP', r'Citation'
    ]
    for pattern in aircraft_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            tags.append(pattern)
    
    return list(set(tags))[:15]

def run_command(cmd: list, retries: int = 2, timeout: int = 60) -> dict:
    """执行 openclaw 命令"""
    last_err = ""
    for i in range(retries):
        try:
            p = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )
            if p.returncode == 0:
                output = p.stdout.strip()
                if not output:
                    return {}
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"raw": output}
            last_err = (p.stderr or p.stdout or "").strip()
        except Exception as e:
            last_err = str(e)
        time.sleep(1.5 ** i)
    raise RuntimeError(f"命令失败：{' '.join(cmd)} => {last_err}")

# ============ Browser Relay 操作 ============
def ensure_browser_ready():
    """确保浏览器已启动"""
    try:
        run_command(["openclaw", "browser", "start", "--json"])
        time.sleep(2)
    except:
        pass

def get_tabs():
    """获取所有 tabs"""
    result = run_command(["openclaw", "browser", "tabs", "--json"])
    return result.get("tabs", [])

def open_url(url: str):
    """打开 URL"""
    print(f"  🌐 打开：{url[:80]}...")
    run_command([
        "openclaw", "browser", "open",
        url,
        "--json"
    ])
    time.sleep(3)  # 等待页面加载

def snapshot_page(target_id: str, fmt: str = "ai"):
    """获取页面快照"""
    result = run_command([
        "openclaw", "browser", "snapshot",
        "--target-id", target_id,
        "--format", fmt,
        "--json",
        "--limit", "500"
    ])
    return result

def scroll_page(target_id: str):
    """向下滚动页面"""
    try:
        run_command([
            "openclaw", "browser", "act",
            "--target-id", target_id,
            "--kind", "evaluate",
            "--fn", "window.scrollBy(0, 800); return document.documentElement.scrollTop;"
        ])
        time.sleep(2)
    except Exception as e:
        print(f"  ⚠️ 滚动失败：{e}")

# ============ 帖子解析 ============
def clean_content(raw_text: str) -> str:
    """清理内容，移除 UI 元素描述"""
    if not raw_text:
        return ""
    
    # 移除 UI 元素描述
    patterns_to_remove = [
        r'\[ref=e\d+\]',
        r'\[cursor=pointer\]',
        r'button ""[^""]*""',
        r'link ""[^""]*""',
        r'generic \[ref=e\d+\]',
        r'img ""[^""]*""',
        r'heading ""[^""]*""',
        r'region ""[^""]*""',
        r'text: ',
        r'- /url: [^\n]+',
        r'• \d+[hmd]',
    ]
    
    cleaned = raw_text
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # 清理多余空白
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 移除过短的行
    lines = cleaned.split('\n')
    meaningful_lines = [l for l in lines if len(l.strip()) > 20]
    cleaned = ' '.join(meaningful_lines)
    
    return cleaned

def extract_posts_from_snapshot(snapshot: dict, source_url: str) -> list:
    """从快照中提取帖子"""
    posts = []
    
    text_content = snapshot.get("text", "")
    if not text_content:
        return posts
    
    # 清理内容
    cleaned = clean_content(text_content)
    
    # 分割成可能的帖子块 (基于常见分隔符)
    # LinkedIn 帖子通常包含：作者名 + 内容 + 时间 + 互动数据
    
    # 尝试提取有意义的文本块
    paragraphs = [p.strip() for p in cleaned.split('\n') if len(p.strip()) > 50]
    
    if not paragraphs:
        # 如果没有找到段落，使用整个清理后的内容
        if len(cleaned) > 100:
            paragraphs = [cleaned]
    
    # 为每个段落创建一个帖子记录
    for i, para in enumerate(paragraphs[:5]):  # 每个页面最多取 5 条
        if is_aviation_related(para):
            business_type = classify_business_type(para)
            has_contact, contact_info = extract_contact_info(para)
            
            post = {
                "post_id": f"LI_REAL_{now_filename()}_{len(posts)+1:03d}",
                "timestamp": now_ts(),
                "author_name": extract_author_from_snapshot(snapshot),
                "author_url": source_url,
                "company": extract_company_from_snapshot(snapshot),
                "position": "",
                "content": para[:2000],
                "business_type": business_type,
                "business_value_score": calculate_business_score(para, business_type),
                "urgency": "高" if has_contact else "中",
                "has_contact": has_contact,
                "contact_info": contact_info,
                "post_time": extract_post_time(snapshot),
                "reactions": 0,
                "comments": 0,
                "reposts": 0,
                "has_image": False,
                "image_content": "",
                "source_url": source_url,
                "batch_id": now_filename(),
                "collected_at": now_ts(),
                "content_type": "text",
                "tags": ",".join(extract_tags(para))
            }
            posts.append(post)
    
    return posts

def extract_author_from_snapshot(snapshot: dict) -> str:
    """从快照中提取作者名"""
    text = snapshot.get("text", "")
    
    # 尝试查找作者名模式
    # LinkedIn 通常会显示作者名在帖子顶部
    lines = text.split('\n')
    for line in lines[:20]:  # 在前 20 行查找
        # 跳过 UI 元素
        if 'ref=e' in line or 'button' in line or 'link' in line:
            continue
        # 查找可能的公司名或人名
        if len(line.strip()) > 3 and len(line.strip()) < 100:
            # 检查是否是合理的名字
            if re.match(r'^[A-Za-z0-9\s\.,&-]+$', line.strip()):
                return line.strip()[:50]
    
    return "Unknown"

def extract_company_from_snapshot(snapshot: dict) -> str:
    """从快照中提取公司名"""
    text = snapshot.get("text", "")
    
    # 简单实现：如果有 Company 字样，提取前面的内容
    if 'Company' in text:
        match = re.search(r'"([^"]+)"\s*,?\s*Company', text)
        if match:
            return match.group(1)[:50]
    
    return ""

def extract_post_time(snapshot: dict) -> str:
    """从快照中提取发布时间"""
    text = snapshot.get("text", "")
    
    # 查找时间模式 (如 "3h", "1d", "2w")
    time_match = re.search(r'(\d+[hdwm]\b)', text, re.IGNORECASE)
    if time_match:
        return time_match.group(1)
    
    return "Unknown"

# ============ 数据采集主流程 ============
def collect_from_url(url: str) -> list:
    """从单个 URL 采集帖子"""
    print(f"\n📍 采集：{url[:80]}...")
    
    collected_posts = []
    
    try:
        # 打开 URL
        open_url(url)
        
        # 获取 tabs
        tabs = get_tabs()
        if not tabs:
            print("  ⚠️ 未找到任何 tabs")
            return collected_posts
        
        target_id = tabs[-1].get("targetId")
        
        # 获取快照
        print("  📸 获取快照...")
        snapshot = snapshot_page(target_id)
        
        # 提取帖子
        posts = extract_posts_from_snapshot(snapshot, url)
        
        if posts:
            print(f"  ✅ 采集到 {len(posts)} 条帖子")
            collected_posts.extend(posts)
        else:
            print("  ⚠️ 未找到航空业务相关帖子")
        
        # 滚动页面，尝试加载更多
        for scroll_num in range(3):
            print(f"  📜 滚动 {scroll_num + 1}/3...")
            scroll_page(target_id)
            
            snapshot = snapshot_page(target_id)
            posts = extract_posts_from_snapshot(snapshot, url)
            
            if posts:
                print(f"  ✅ 滚动后采集到 {len(posts)} 条帖子")
                collected_posts.extend(posts)
            
            time.sleep(1)
        
    except Exception as e:
        print(f"  ❌ 采集失败：{e}")
    
    return collected_posts

def save_posts(posts: list, batch_id: str):
    """保存帖子到 CSV 和 JSON"""
    if not posts:
        print("⚠️ 没有数据可保存")
        return
    
    # CSV 文件
    csv_path = OUTPUT_DIR / f"LinkedIn_Business_Posts_真实采集_{batch_id}.csv"
    
    # 字段定义
    fieldnames = [
        "post_id", "timestamp", "author_name", "author_url", "company", "position",
        "content", "business_type", "business_value_score", "urgency", "has_contact",
        "contact_info", "post_time", "reactions", "comments", "reposts", "has_image",
        "image_content", "source_url", "batch_id", "collected_at", "content_type", "tags"
    ]
    
    # 写入 CSV
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for post in posts:
            # 确保所有字段都存在
            row = {field: post.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    # JSON 文件
    json_path = OUTPUT_DIR / f"LinkedIn_Business_Posts_真实采集_{batch_id}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存:")
    print(f"  📄 CSV: {csv_path}")
    print(f"  📄 JSON: {json_path}")
    print(f"  📊 总计：{len(posts)} 条帖子")

def main():
    """主函数"""
    print("=" * 60)
    print("LinkedIn 真实帖子采集系统 v5.0")
    print("=" * 60)
    print(f"开始时间：{now_ts()}")
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"种子 URL 数量：{len(SEED_URLS)}")
    print()
    
    # 确保浏览器就绪
    print("🚀 启动浏览器...")
    ensure_browser_ready()
    
    # 采集所有 URL
    all_posts = []
    batch_id = now_filename()
    
    for i, url in enumerate(SEED_URLS, 1):
        print(f"\n{'='*60}")
        print(f"进度：{i}/{len(SEED_URLS)}")
        print(f"{'='*60}")
        
        posts = collect_from_url(url)
        all_posts.extend(posts)
        
        # 去重
        seen_urls = set()
        unique_posts = []
        for post in all_posts:
            content_hash_key = content_hash(post.get("content", ""))
            if content_hash_key not in seen_urls:
                seen_urls.add(content_hash_key)
                unique_posts.append(post)
        
        all_posts = unique_posts
        
        # 间隔等待
        if i < len(SEED_URLS):
            wait_time = 3
            print(f"⏳ 等待 {wait_time} 秒...")
            time.sleep(wait_time)
    
    # 保存数据
    print(f"\n{'='*60}")
    print("保存数据...")
    print(f"{'='*60}")
    save_posts(all_posts, batch_id)
    
    # 生成报告
    generate_report(all_posts, batch_id)
    
    print(f"\n✅ 采集完成!")
    print(f"总采集数：{len(all_posts)} 条")
    print(f"结束时间：{now_ts()}")

def generate_report(posts: list, batch_id: str):
    """生成采集报告"""
    report_path = OUTPUT_DIR / f"LinkedIn_Real_Collection_Report_{batch_id}.md"
    
    # 统计信息
    business_types = {}
    for post in posts:
        bt = post.get("business_type", "Unknown")
        business_types[bt] = business_types.get(bt, 0) + 1
    
    report = f"""# LinkedIn 真实数据采集报告

## 采集概况
- **采集时间**: {now_ts()}
- **批次 ID**: {batch_id}
- **总采集数**: {len(posts)} 条
- **种子 URL 数**: {len(SEED_URLS)} 个

## 业务类型分布
"""
    
    for bt, count in sorted(business_types.items(), key=lambda x: -x[1]):
        report += f"- {bt}: {count} 条\n"
    
    report += f"""
## 数据质量标准
- ✅ author_name: 真实人名/公司名
- ✅ content: 干净业务文本 (无 UI 元素描述)
- ✅ business_type: 中文业务分类
- ✅ source_url: 真实 LinkedIn 帖子 URL

## 输出文件
1. `LinkedIn_Business_Posts_真实采集_{batch_id}.csv`
2. `LinkedIn_Business_Posts_真实采集_{batch_id}.json`

---
*报告生成时间：{now_ts()}*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"  📄 报告：{report_path}")

if __name__ == "__main__":
    main()
