import pandas as pd
import os

# 检查最新采集的 CSV 文件
csv_path = r'C:\Users\Haide\Desktop\real business post\linkedin_posts_20260402_101611.csv'
output_path = r'C:\Users\Haide\.openclaw\workspace\linkedin_collection_result.txt'

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('=== LinkedIn 采集结果 (2026-04-02) ===\n')
        f.write(f'总帖子数: {len(df)}\n\n')
        
        for idx, row in enumerate(df.itertuples()):
            f.write(f'--- Post {idx+1} ---\n')
            f.write(f'Author: {row.author if hasattr(row, "author") else "N/A"}\n')
            f.write(f'Text preview: {str(row.text if hasattr(row, "text") else "N/A")[:200]}...\n')
            f.write(f'Contact: {row.contact if hasattr(row, "contact") else "N/A"}\n')
            f.write(f'IsBusiness: {row.isBusiness if hasattr(row, "isBusiness") else "N/A"}\n\n')
    
    print(f'Result saved to: {output_path}')
    print(f'Total posts: {len(df)}')
else:
    print('CSV file not found')