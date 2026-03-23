import re
import csv
from datetime import datetime

# 读取HTML文件
file_path = r'C:\Users\Haide\.openclaw\media\inbound\file_1---844bc04a-e8b4-4e71-b971-eb19b06dbf57'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

print(f'文件大小: {len(html)} 字符')
print('开始解析联系人数据...')

contacts = []
seen = set()

# 方法1: 提取LinkedIn个人链接和名字
# 匹配模式: href="https://www.linkedin.com/in/xxx" ... >Name</a>
pattern1 = r'href="(https://www\.linkedin\.com/in/[^"]+)"[^>]*data-view-name="connections-profile"[^>]*>[^<]*<[^>]*>[^<]*<p[^>]*>([^<]+)</p>'

matches = re.findall(pattern1, html)
print(f'模式1找到 {len(matches)} 个匹配')

for link, name in matches:
    name = name.strip()
    if name and name not in seen and len(name) > 2:
        seen.add(name)
        contacts.append({
            'name': name,
            'link': link.split('?')[0],
            'title': '',
            'company': ''
        })

# 方法2: 如果不够，尝试更宽松的模式
if len(contacts) < 100:
    pattern2 = r'href="https://www\.linkedin\.com/in/([^"]+)"[^>]*>([^<]+)</a>'
    matches2 = re.findall(pattern2, html)
    print(f'模式2找到 {len(matches2)} 个匹配')
    
    for profile_id, name in matches2:
        name = name.strip()
        if name and name not in seen and len(name) > 2 and ' ' in name:
            seen.add(name)
            contacts.append({
                'name': name,
                'link': f'https://www.linkedin.com/in/{profile_id}',
                'title': '',
                'company': ''
            })

# 提取职位信息
title_pattern = r'<p[^>]*class="[^"]*d09f7b3e[^"]*"[^>]*>([^<]+)</p>'
titles = re.findall(title_pattern, html)
print(f'找到 {len(titles)} 个职位描述')

# 合并职位信息到联系人
for i, contact in enumerate(contacts):
    if i < len(titles):
        title_text = titles[i].strip()
        # 解析职位和公司
        if ' at ' in title_text:
            parts = title_text.split(' at ', 1)
            contact['title'] = parts[0].strip()
            contact['company'] = parts[1].strip()
        elif ' @ ' in title_text:
            parts = title_text.split(' @ ', 1)
            contact['title'] = parts[0].strip()
            contact['company'] = parts[1].strip()
        else:
            contact['title'] = title_text

print(f'\\n成功提取 {len(contacts)} 位联系人')

# 保存为CSV
output_file = r'C:\Users\Haide\.openclaw\workspace\linkedin_contacts_FULL.csv'
with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', '公司', '职位', '联系方式', 'LinkedIn链接', '抓取时间'])
    for c in contacts:
        writer.writerow([c['name'], c['company'], c['title'], '', c['link'], '2025-01-21'])

print(f'\\n数据已保存到: {output_file}')
print(f'\\n前5位联系人:')
for c in contacts[:5]:
    print(f"  - {c['name']}: {c['title']} @ {c['company']}")
    print(f"    {c['link']}")
