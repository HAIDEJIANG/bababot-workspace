import json
import pandas as pd
from datetime import datetime
import os

# 读取JSON文件
json_path = os.path.expanduser('~/Desktop/real business post/linkedin_real_business_posts.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

posts = data['posts']

# 转换为DataFrame
df = pd.DataFrame(posts)

# 统计业务类型
business_type_counts = df['business_type'].value_counts().reset_index()
business_type_counts.columns = ['Business Type', 'Count']

# 统计紧急帖子
urgent_posts = df[df['urgency'] == True] if 'urgency' in df.columns else pd.DataFrame()

# 统计高价值帖子 (评分>=4)
high_value_posts = df[df['business_value_score'] >= 4] if 'business_value_score' in df.columns else pd.DataFrame()

# 保存为多工作表Excel
excel_path = os.path.expanduser('~/Desktop/real business post/LinkedIn_Business_Posts_Analysis.xlsx')

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    # 工作表1：所有帖子
    df.to_excel(writer, sheet_name='All Posts', index=False)
    
    # 工作表2：业务类型统计
    business_type_counts.to_excel(writer, sheet_name='Business Type Stats', index=False)
    
    # 工作表3：高价值帖子
    if not high_value_posts.empty:
        high_value_posts.to_excel(writer, sheet_name='High Value (4-5)', index=False)
    
    # 工作表4：紧急帖子
    if not urgent_posts.empty:
        urgent_posts.to_excel(writer, sheet_name='Urgent Posts', index=False)
    
    # 调整所有工作表的列宽
    for sheet_name in writer.sheets:
        worksheet = writer.sheets[sheet_name]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 60)
            worksheet.column_dimensions[column_letter].width = adjusted_width

print(f'Analysis Excel saved: {excel_path}')
print(f'Total posts: {len(df)}')
print(f'Business types: {len(business_type_counts)}')
print(f'High value posts (>=4): {len(high_value_posts)}')
print(f'Urgent posts: {len(urgent_posts)}')
print('Analysis done!')
