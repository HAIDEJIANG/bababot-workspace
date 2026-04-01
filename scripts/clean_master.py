import csv

f = open('C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv', 'r', encoding='utf-8')
r = csv.DictReader(f)
rows = list(r)
fieldnames = r.fieldnames

# 过滤无效记录
valid_rows = []
invalid_patterns = ['Skip to search', 'Skip to main', 'LinkedIn Home', 'Messaging', 'Notifications', 'Unknown -']

for row in rows:
    author = row.get('author_name', '') or row.get('company', '')
    content = row.get('content', '') or row.get('content_summary', '')
    
    # 排除无效记录
    is_invalid = False
    for pattern in invalid_patterns:
        if pattern in author or pattern in content:
            is_invalid = True
            break
    
    # 排除空内容
    if not content or len(content) < 10:
        is_invalid = True
    
    if not is_invalid:
        valid_rows.append(row)

# 保存清理后的文件
with open('C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(valid_rows)

print(f"清理完成: {len(rows)} -> {len(valid_rows)} 条")
print(f"删除无效记录: {len(rows) - len(valid_rows)} 条")