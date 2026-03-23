import csv
from datetime import datetime

# 路径定义
source_path = r'C:\Users\Haide\.openclaw\workspace\outputs\aviation_linkedin_master_20250301.csv'
master_path = r'C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv'

# 读取总表获取最大ID
def get_max_post_id(master_file):
    max_id = 0
    with open(master_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get('post_id', '')
            if pid.startswith('linkedin_'):
                try:
                    num = int(pid.replace('linkedin_', ''))
                    max_id = max(max_id, num)
                except:
                    pass
            elif pid.startswith('航空_'):
                try:
                    num = int(pid.replace('航空_', ''))
                    max_id = max(max_id, num)
                except:
                    pass
    return max_id

# 分类映射（从简短描述到业务类型）
def map_business_type(content, category):
    content_lower = content.lower()
    category_lower = category.lower() if category else ''
    
    if 'engine' in content_lower or 'cfm' in content_lower or 'leap' in content_lower or 'v2500' in content_lower:
        return '发动机销售/租赁'
    elif 'landing gear' in content_lower or '起落架' in content_lower:
        return '起落架销售/租赁'
    elif 'aircraft' in content_lower and ('sale' in content_lower or '出售' in content_lower or '销售' in content_lower):
        return '飞机销售'
    elif ('lease' in content_lower or '租赁' in content_lower) and 'aircraft' in content_lower:
        return '飞机租赁'
    elif 'mro' in content_lower or 'maintenance' in content_lower or '维修' in content_lower:
        return '飞机维修'
    elif 'part' in content_lower or 'component' in content_lower or '零件' in content_lower or '航材' in content_lower:
        return '航材销售'
    elif 'charter' in content_lower or '包机' in content_lower:
        return '飞机包机'
    elif 'cargo' in content_lower or '航空物流' in content_lower:
        return '航空物流'
    elif 'news' in category_lower or 'advisory' in category_lower or '通告' in category_lower:
        return '行业新闻'
    elif 'hire' in category_lower or '招聘' in category_lower or 'career' in category_lower:
        return '招聘信息'
    else:
        return '其他'

# 价值评分映射（启发式规则）
def score_business_value(content, category, has_contact):
    score = 1
    content_lower = content.lower()
    
    # 高价值词汇
    high_value_words = ['urgent', 'immediate', 'available now', 'ready', 'stock', '现货', '紧急', '急需', '立即']
    high_value_parts = ['engine', 'cfm', 'leap', 'aircraft', 'boeing', 'airbus', '航材', '发动机']
    contact_words = ['contact', 'email', 'phone', 'dm', '联系', '邮箱', '电话']
    
    # 检查高价值特征
    if any(word in content_lower for word in high_value_words):
        score += 2
    if any(part in content_lower for part in high_value_parts):
        score += 1
    if has_contact:
        score += 1
    if len(content) > 100:  # 详细描述
        score += 1
        
    return min(score, 5)  # 最高5分

# 提取联系人信息（简单提取邮箱和电话）
def extract_contact_info(content):
    import re
    # 提取邮箱
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', content)
    # 提取电话号码（简单模式）
    phones = re.findall(r'(\+\d{1,3}[\s\-]?)?\(?\d{3,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}', content)
    
    contacts = []
    if emails:
        contacts.extend(emails[:2])  # 最多取2个邮箱
    if phones:
        contacts.extend(phones[:2])
    
    return '; '.join(contacts) if contacts else ''

# 读取源数据
source_data = []
with open(source_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        source_data.append(row)

# 读取总表ID基数
max_id = get_max_post_id(master_path)
new_id_start = max_id + 1

# 准备新记录
new_records = []
for idx, item in enumerate(source_data):
    # 原始字段
    timestamp = item.get('timestamp', '')
    author_name = item.get('author_name', '')
    author_title = item.get('author_title', '')
    author_company = item.get('author_company', '')
    post_content = item.get('post_content', '')
    hashtags = item.get('hashtags', '')
    source_url = item.get('source_url', '')
    post_type = item.get('post_type', '')
    collected_at = item.get('collected_at', '')
    
    # 衍生字段
    business_type = map_business_type(post_content, post_type)
    has_contact = 'True' if '@' in post_content or 'contact' in post_content.lower() or '邮箱' in post_content else 'False'
    contact_info = extract_contact_info(post_content)
    business_value_score = str(score_business_value(post_content, post_type, has_contact))
    urgency = '高' if any(word in post_content.lower() for word in ['urgent', 'immediate', '紧急', '急需']) else '中' if 'soon' in post_content.lower() else '低'
    post_time = ''  # 可留空
    reactions = ''
    comments = ''
    reposts = ''
    has_image = 'True' if 'image' in hashtags.lower() else 'False'
    image_content = ''
    author_url = source_url.split('/in/')[0] if '/in/' in source_url else ''
    posted_time = ''
    content_summary = post_content[:200] if len(post_content) > 200 else post_content
    is_repost = ''
    original_author = ''
    batch_id = '20250301_aviation_30min'
    aircraft_type = ''  # 可后续提取
    
    # 构建记录
    new_id = f'航空_{new_id_start + idx:03d}'
    record = {
        'post_id': new_id,
        'timestamp': timestamp,
        'author_name': author_name,
        'company': author_company,
        'position': author_title,
        'content': post_content,
        'business_type': business_type,
        'business_value_score': business_value_score,
        'urgency': urgency,
        'has_contact': has_contact,
        'contact_info': contact_info,
        'post_time': post_time,
        'reactions': reactions,
        'comments': comments,
        'reposts': reposts,
        'has_image': has_image,
        'image_content': image_content,
        'source_url': source_url,
        '_source_file': source_path,
        'author_url': author_url,
        'posted_time': posted_time,
        'content_summary': content_summary,
        'is_repost': is_repost,
        'original_author': original_author,
        'category': post_type,
        'aircraft_type': aircraft_type,
        'batch_id': batch_id,
        'author_title': author_title,
        'content_type': '',
        'tags': hashtags
    }
    new_records.append(record)

# 字段顺序（与总表一致）
fieldnames = [
    'post_id', 'timestamp', 'author_name', 'company', 'position', 'content',
    'business_type', 'business_value_score', 'urgency', 'has_contact', 'contact_info',
    'post_time', 'reactions', 'comments', 'reposts', 'has_image', 'image_content',
    'source_url', '_source_file', 'author_url', 'posted_time', 'content_summary',
    'is_repost', 'original_author', 'category', 'aircraft_type', 'batch_id',
    'author_title', 'content_type', 'tags'
]

# 追加到总表
with open(master_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerows(new_records)

# 统计业务类型
by_type = {}
for rec in new_records:
    btype = rec.get('business_type', '')
    by_type[btype] = by_type.get(btype, 0) + 1

# 输出结果
print("OK. Merged", len(new_records), "records to master table")
print("New ID range:", f"航空_{new_id_start:03d} - 航空_{new_id_start + len(new_records) - 1:03d}")

print("\n--- Business Type Stats ---")
for btype, cnt in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
    print(f"  {btype}: {cnt} records")
