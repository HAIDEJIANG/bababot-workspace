import csv

existing_urls = set()
existing_content = set()

# 读取现有数据
try:
    with open('outputs/aviation_linkedin_master_20250301.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('source_url'):
                existing_urls.add(row['source_url'])
            key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
            existing_content.add(key)
    print(f'现有URL索引: {len(existing_urls)}')
    print(f'现有内容索引: {len(existing_content)}')
except Exception as e:
    print(f'读取现有数据: {e}')

# 读取新数据并去重
new_records = []
duplicate_count = 0
try:
    with open('outputs/aviation_linkedin_new_batch2.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
            if key not in existing_content:
                new_records.append(row)
                existing_content.add(key)
            else:
                duplicate_count += 1
    print(f'新记录中: {len(new_records)} 条非重复, {duplicate_count} 条重复')
except Exception as e:
    print(f'读取新数据: {e}')

# 追加到主文件
if new_records:
    file_exists = False
    try:
        with open('outputs/aviation_linkedin_master_20250301.csv', 'r', encoding='utf-8') as f:
            file_exists = True
    except:
        pass
    
    with open('outputs/aviation_linkedin_master_20250301.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp','author_name','author_title','author_company','post_content','hashtags','source_url','post_type','collected_at'])
        for row in new_records:
            writer.writerow([
                row['timestamp'], row['author_name'], row['author_title'],
                row['author_company'], row['post_content'], row['hashtags'],
                row['source_url'], row['post_type'], row['collected_at']
            ])
    print(f'已追加 {len(new_records)} 条记录')
else:
    print('无新增记录')

# 统计
print(f'\n统计:')
print(f'- 新增: {len(new_records)}')
print(f'- 去重: {duplicate_count}')
print(f'- 累计: {len(existing_content)}')
