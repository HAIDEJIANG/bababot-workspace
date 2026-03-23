import json
import pandas as pd
from datetime import datetime
import os

# 读取JSON文件
json_path = os.path.expanduser('~/Desktop/real business post/linkedin_real_business_posts.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

posts = data['posts']
print(f'Read {len(posts)} posts')

# 转换为DataFrame
df = pd.DataFrame(posts)

# 选择关键列并重命名
column_mapping = {
    'post_id': 'Post ID',
    'author': 'Author',
    'author_name': 'Author',
    'company': 'Company',
    'title': 'Title',
    'content': 'Content',
    'business_type': 'Business Type',
    'business_value_score': 'Value Score',
    'urgency': 'Urgent',
    'urgent': 'Urgent',
    'contact_info': 'Contact',
    'source_url': 'Source URL',
    'collected_at': 'Collected Time',
    'timestamp': 'Timestamp',
    'post_time': 'Post Time'
}

# 重命名存在的列
for old_col, new_col in column_mapping.items():
    if old_col in df.columns:
        df = df.rename(columns={old_col: new_col})

# 添加序号列
df.insert(0, 'No.', range(1, len(df) + 1))

# 保存为Excel
excel_path = os.path.expanduser('~/Desktop/real business post/LinkedIn_Business_Posts_Summary_Latest.xlsx')

# 使用openpyxl引擎
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Business Posts', index=False)
    
    # 获取工作表并调整列宽
    worksheet = writer.sheets['Business Posts']
    
    # 调整列宽
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        
        # 限制最大宽度，但确保足够显示
        adjusted_width = min(max_length + 2, 60)
        worksheet.column_dimensions[column_letter].width = adjusted_width

print(f'Excel file saved: {excel_path}')
print(f'Total posts: {len(df)}')
print(f'Columns: {len(df.columns)}')
print('Done!')
