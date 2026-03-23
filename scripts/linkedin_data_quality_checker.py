# -*- coding: utf-8 -*-
"""
LinkedIn 数据质量检查脚本
检查 LinkedIn_Business_Posts_Master_Table.csv 中各列内容是否与列名匹配
"""

import csv
import re
from pathlib import Path

# 主表文件
LINKEDIN_FILE = r'C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv'

# 有效的业务类别
VALID_CATEGORIES = ['engine', 'aircraft', 'landing_gear', 'mro', 'parts', 'helicopter', 'service', 'training', 'other']

# 有效的业务类型
VALID_BUSINESS_TYPES = ['supply', 'demand', 'service', 'news', 'education', 'other']

# 有效的业务价值
VALID_BUSINESS_VALUES = ['high', 'medium', 'low', '']

def validate_date(value):
    """验证日期格式"""
    if not value:
        return True
    # YYYY-MM-DD 格式
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', value))

def validate_category(value):
    """验证类别"""
    if not value:
        return True
    return value.lower().strip() in VALID_CATEGORIES

def validate_business_type(value):
    """验证业务类型"""
    if not value:
        return True
    return value.lower().strip() in VALID_BUSINESS_TYPES

def validate_business_value(value):
    """验证业务价值"""
    if not value:
        return True
    return value.lower().strip() in VALID_BUSINESS_VALUES

def validate_source_url(value):
    """验证来源URL"""
    if not value:
        return False  # source_url 不能为空
    return value.startswith('http://') or value.startswith('https://') or value.startswith('www.')

def validate_contact_info(value):
    """验证联系方式"""
    if not value:
        return True  # 联系方式可以为空
    
    # 应该包含邮箱、电话或其他联系方式
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', value))
    has_phone = bool(re.search(r'[\+]?[\d\s\-\(\)]{7,}', value))
    has_linkedin = 'linkedin.com' in value.lower()
    has_website = bool(re.search(r'https?://', value))
    
    return has_email or has_phone or has_linkedin or has_website or value.lower() in ['dm on linkedin', 'dm', '']

def check_row_quality(row):
    """检查单行数据质量"""
    issues = []
    
    # 检查 post_id
    if not row.get('post_id'):
        issues.append("post_id 为空")
    
    # 检查 post_date
    if not validate_date(row.get('post_date', '')):
        issues.append(f"post_date 格式错误: '{row.get('post_date')}'")
    
    # 检查 author
    if not row.get('author'):
        issues.append("author 为空")
    
    # 检查 category
    if row.get('category') and not validate_category(row.get('category', '')):
        issues.append(f"category 无效: '{row.get('category')}'")
    
    # 检查 business_type
    if row.get('business_type') and not validate_business_type(row.get('business_type', '')):
        issues.append(f"business_type 无效: '{row.get('business_type')}'")
    
    # 检查 business_value
    if row.get('business_value') and not validate_business_value(row.get('business_value', '')):
        issues.append(f"business_value 无效: '{row.get('business_value')}'")
    
    # 检查 source_url (重要!)
    if not validate_source_url(row.get('source_url', '')):
        issues.append(f"source_url 无效或为空: '{row.get('source_url', '')[:50]}'")
    
    # 检查 verified
    verified = row.get('verified', '').lower()
    if verified not in ['true', 'false', '']:
        issues.append(f"verified 值异常: '{verified}'")
    
    return issues

def main():
    print("="*60)
    print("LinkedIn Data Quality Checker")
    print("="*60)
    
    # 读取文件
    rows = []
    headers = []
    
    with open(LINKEDIN_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            rows.append(row)
    
    print(f"\nFile: {Path(LINKEDIN_FILE).name}")
    print(f"Total rows: {len(rows)}")
    print(f"Columns: {len(headers)}")
    print(f"Column names: {', '.join(headers)}")
    
    # 检查每行
    good_rows = []
    bad_rows = []
    
    for row in rows:
        issues = check_row_quality(row)
        
        if issues:
            bad_rows.append((row, issues))
        else:
            good_rows.append(row)
    
    print(f"\n{'='*60}")
    print("Quality Report")
    print('='*60)
    print(f"Valid rows: {len(good_rows)}")
    print(f"Problem rows: {len(bad_rows)}")
    
    if bad_rows:
        print(f"\nProblem row examples (first 10):")
        for i, (row, issues) in enumerate(bad_rows[:10]):
            post_id = row.get('post_id', '')[:30]
            author = row.get('author', '')[:20]
            print(f"  {i+1}. post_id: '{post_id}' | author: '{author}'")
            print(f"     Issues: {'; '.join(issues)}")
        
        # 统计问题类型
        issue_counts = {}
        for _, issues in bad_rows:
            for issue in issues:
                key = issue.split(':')[0] if ':' in issue else issue
                issue_counts[key] = issue_counts.get(key, 0) + 1
        
        print(f"\nIssue distribution:")
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {issue}: {count} rows")
    
    # 保存清洗后的数据
    if bad_rows:
        output_path = LINKEDIN_FILE.replace('.csv', '_cleaned.csv')
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(good_rows)
        
        print(f"\nCleaned file saved: {Path(output_path).name}")
        print(f"Removed {len(bad_rows)} problem rows")
    else:
        print("\nAll data is valid! No cleaning needed.")
    
    print("\n" + "="*60)
    print("Check complete")
    print("="*60)

if __name__ == '__main__':
    main()