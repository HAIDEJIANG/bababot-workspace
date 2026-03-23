import csv
import shutil
from pathlib import Path

# 路径设置
workspace = Path("C:/Users/Haide/.openclaw/workspace")
source_file = workspace / "outputs" / "aviation_linkedin_master_20250301.csv"
master_file = workspace / "Desktop" / "real business post" / "LinkedIn_Business_Posts_Master_Table.csv"

# 确保目录存在
master_file.parent.mkdir(parents=True, exist_ok=True)

# 读取源文件数据
source_rows = []
with open(source_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        source_rows.append(row)

print(f"源文件记录数: {len(source_rows)}")

# 如果主表不存在，直接复制
if not master_file.exists():
    shutil.copy(source_file, master_file)
    print(f"主表不存在，已创建: {master_file}")
    print(f"合并完成: {len(source_rows)} 条记录")
else:
    # 读取主表现有索引
    existing_content = set()
    with open(master_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
            existing_content.add(key)
    
    print(f"主表现在有: {len(existing_content)} 条记录")
    
    # 追加新记录
    new_count = 0
    with open(master_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in source_rows:
            key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
            if key not in existing_content:
                writer.writerow([
                    row['timestamp'], row['author_name'], row['author_title'],
                    row['author_company'], row['post_content'], row['hashtags'],
                    row['source_url'], row['post_type'], row['collected_at']
                ])
                new_count += 1
    
    print(f"已向主表追加: {new_count} 条新记录")

print("\n合并完成!")
