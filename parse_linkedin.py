from html.parser import HTMLParser
import re

# 读取HTML文件
with open('C:\\Users\\Haide\\.openclaw\\media\\inbound\\file_1---844bc04a-e8b4-4e71-b971-eb19b06dbf57', 'r', encoding='utf-8') as f:
    html_content = f.read()

print(f'HTML文件大小: {len(html_content)} 字符')
print('开始解析...')

# 查找所有联系人链接和名字
contacts = []
seen = set()

# 使用正则表达式提取联系人信息
# 匹配LinkedIn个人主页链接
link_pattern = r'href="(https://www\.linkedin\.com/in/[^"]+)"'
links = re.findall(link_pattern, html_content)

print(f'找到 {len(links)} 个链接')

# 提取联系人名字和职位
# 查找包含名字的<p>标签
name_pattern = r'<p[^>]*class="[^"]*_2ef9145d[^"]*"[^>]*>\s*<a[^>]*href="https://www\.linkedin\.com/in/[^"]+"[^>]*>([^<]+)</a>\s*</p>'
names = re.findall(name_pattern, html_content)

print(f'找到 {len(names)} 个名字')

# 提取职位信息
title_pattern = r'<p[^>]*class="[^"]*d09f7b3e[^"]*"[^>]*>([^<]+)</p>'
titles = re.findall(title_pattern, html_content)

print(f'找到 {len(titles)} 个职位')

# 合并信息
for i, name in enumerate(names[:50]):  # 先处理前50个
    if i < len(titles):
        title = titles[i]
        if name not in seen:
            seen.add(name)
            # 解析公司和职位
            company = ''
            job_title = title
            if ' at ' in title:
                parts = title.split(' at ')
                job_title = parts[0].strip()
                company = parts[1].strip()
            elif ' @ ' in title:
                parts = title.split(' @ ')
                job_title = parts[0].strip()
                company = parts[1].strip()
            
            contacts.append({
                'name': name.strip(),
                'company': company,
                'title': job_title,
                'link': links[i] if i < len(links) else ''
            })

print(f'\\n成功提取 {len(contacts)} 位联系人')
print('\\n前10位联系人:')
for c in contacts[:10]:
    print(f"- {c['name']}: {c['title']} @ {c['company']}")
