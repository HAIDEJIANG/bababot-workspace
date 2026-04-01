# V2500 联系人批量搜索脚本（CDP 协议）
# 基于 Browser Relay CDP 协议自动搜索 LinkedIn 联系人

import asyncio
import json
import requests
import time
from datetime import datetime

# CDP 配置
CDP_BASE = "http://localhost:9222"

# 目标公司列表（从 v2500_companies.txt 提取优先级公司）
TARGET_COMPANIES = [
    "IndiGo", "Wizz Air", "Spirit Airlines", "JetBlue", "Vietjet Air",
    "Scoot", "Finnair", "TAP Air Portugal", "Lufthansa", "British Airways",
    "AirAsia", "Frontier Airlines", "Volaris", "PLAY", "Norse Atlantic",
    "Aegean Airlines", "SAS", "Thai Airways", "Philippine Airlines",
    "South African Airways", "LATAM Airlines", "Avianca", "Gol Linhas Aereas",
    "Cebu Pacific", "Air Arabia", "Flydubai", "Pegasus Airlines",
    "Turkish Airlines", "EgyptAir", "Royal Jordanian", "Gulf Air",
    "Oman Air", "Qatar Airways", "Etihad Airways", "Emirates",
    "Singapore Airlines", "Cathay Pacific", "Hong Kong Airlines",
    "China Eastern", "China Southern", "Air China", "Hainan Airlines",
    "Japan Airlines", "ANA", "Korean Air", "Asiana Airlines"
]

# 搜索职位关键词
JOB_TITLES = [
    "Fleet Management", "Engine Asset Management", "Technical Director",
    "VP Fleet", "Head of Engine", "Aircraft Leasing", "Asset Manager",
    "Technical Manager", "Engineering Director", "Maintenance Director"
]

def get_cdp_target():
    """获取 CDP 目标"""
    try:
        resp = requests.get(f"{CDP_BASE}/json/list", timeout=5)
        tabs = resp.json()
        for tab in tabs:
            if "linkedin.com" in tab.get("url", ""):
                return tab.get("id")
        # 如果没有 LinkedIn 标签，返回第一个
        return tabs[0].get("id") if tabs else None
    except Exception as e:
        print(f"获取 CDP 目标失败：{e}")
        return None

def search_linkedin_people(company, title):
    """在 LinkedIn 搜索特定公司的人员"""
    target_id = get_cdp_target()
    if not target_id:
        print(f"❌ 无法获取 CDP 目标")
        return []
    
    # 构建搜索 URL
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={company} {title}&origin=GLOBAL_SEARCH_HEADER"
    
    try:
        # 导航到搜索页面
        requests.post(f"{CDP_BASE}/json/{target_id}", json={
            "id": 1,
            "method": "Page.navigate",
            "params": {"url": search_url}
        }, timeout=10)
        
        # 等待页面加载
        time.sleep(5)
        
        # 执行 JavaScript 提取搜索结果
        extract_script = """
        (() => {
            const results = [];
            const cards = document.querySelectorAll('ul[role=\"list\"] li');
            
            cards.forEach((card, idx) => {
                if (idx >= 10) return; // 只取前 10 个结果
                
                const nameEl = card.querySelector('span.entity-result__title-line');
                const titleEl = card.querySelector('div.entity-result__primary-subtitle');
                const locationEl = card.querySelector('div.entity-result__secondary-subtitle');
                const linkEl = card.querySelector('a.app-aware-link');
                
                if (nameEl && linkEl) {
                    results.push({
                        name: nameEl.textContent.trim(),
                        title: titleEl ? titleEl.textContent.trim() : '',
                        location: locationEl ? locationEl.textContent.trim() : '',
                        linkedin_url: linkEl.href.split('?')[0]
                    });
                }
            });
            
            return results;
        })()
        """
        
        resp = requests.post(f"{CDP_BASE}/json/{target_id}", json={
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {"expression": extract_script}
        }, timeout=10)
        
        result = resp.json().get("result", {}).get("result", {}).get("value", [])
        return result
        
    except Exception as e:
        print(f"搜索失败 {company}: {e}")
        return []

def main():
    print("=== V2500 联系人批量搜索 ===")
    print(f"目标公司数：{len(TARGET_COMPANIES)}")
    print(f"搜索职位：{len(JOB_TITLES)} 类")
    print("")
    
    all_contacts = []
    
    for i, company in enumerate(TARGET_COMPANIES[:20]):  # 先搜索前 20 家公司
        print(f"[{i+1}/20] 搜索：{company}")
        
        # 每家公司搜索 2-3 个职位关键词
        for title in JOB_TITLES[:3]:
            contacts = search_linkedin_people(company, title)
            for contact in contacts:
                contact['company'] = company
                contact['search_title'] = title
                all_contacts.append(contact)
                print(f"  ✓ {contact['name']} - {contact['title']} @ {company}")
            
            time.sleep(2)  # 避免频率限制
        
        time.sleep(3)
    
    # 保存结果
    output_file = f"v2500_contacts_batch_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_contacts, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 搜索完成！")
    print(f"总联系人：{len(all_contacts)}")
    print(f"已保存：{output_file}")
    
    # 追加到现有文件
    append_to_markdown(all_contacts)

def append_to_markdown(contacts):
    """追加到 Markdown 文件"""
    md_file = "v2500_linkedin_contacts.md"
    
    # 读取现有内容
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            existing = f.read()
    except:
        existing = "# V2500 运营商/拥有者 - LinkedIn 联系人候选\n\n"
    
    # 追加新内容
    new_section = f"\n\n## 📋 批量搜索新增 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
    
    # 按公司分组
    by_company = {}
    for c in contacts:
        comp = c.get('company', 'Unknown')
        if comp not in by_company:
            by_company[comp] = []
        by_company[comp].append(c)
    
    for company, people in by_company.items():
        new_section += f"### {company}\n\n"
        new_section += "| 姓名 | 职位 | LinkedIn |\n|------|------|----------|\n"
        
        for p in people[:5]:  # 每家公司最多显示 5 位
            url = p.get('linkedin_url', '')
            name = p.get('name', 'Unknown')
            title = p.get('title', '')
            new_section += f"| {name} | {title} | `{url}` |\n"
        
        new_section += "\n"
    
    # 写入文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(existing + new_section)
    
    print(f"已追加到 {md_file}")

if __name__ == "__main__":
    main()
