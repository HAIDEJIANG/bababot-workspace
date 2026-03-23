# -*- coding: utf-8 -*-
"""
数据质量检查和清洗脚本
检查汇总表中各列内容是否与列名匹配，清理不符合要求的行
"""

import csv
import re
from pathlib import Path

# 文件列表
FILES_TO_CHECK = [
    r'C:\Users\Haide\Desktop\OPENCLAW\航材供应商报价汇总_2026-03-01_至今.csv',
    r'C:\Users\Haide\Desktop\OPENCLAW\客户询价汇总_2026-03-16_至今.csv',
    r'C:\Users\Haide\Desktop\OPENCLAW\邮箱报价信息汇总_2026-03-16_至今.csv',
]

# 件号验证模式
PART_NUMBER_PATTERNS = [
    r'^[A-Za-z0-9]{2,}[-][A-Za-z0-9]{2,}[-][A-Za-z0-9]{1,}$',  # 如 12345-AB-1
    r'^[A-Za-z0-9]{4,}[-][A-Za-z0-9]{2,}$',  # 如 1234-AB
    r'^[A-Za-z]{2,}[0-9]{4,}$',  # 如 PN12345
    r'^[0-9]{4,}[A-Za-z]{1,}[A-Za-z0-9]*$',  # 如 1234AB
    r'^[A-Za-z0-9]{6,}$',  # 长串字母数字
]

# 条件验证
VALID_CONDITIONS = ['SV', 'NS', 'NE', 'AR', 'OH', 'FN', 'AS', 'SV', 'NEW', 'NEW', 'NEW', 'OH', 'OH']

def is_valid_part_number(value):
    """验证是否为有效件号"""
    if not value or len(value) < 3:
        return False
    
    value = value.strip()
    
    # 排除明显非件号的内容
    exclude_patterns = [
        r'^image\d*$',  # image, image002
        r'^signature',  # signature_
        r'^SYS\d+$',  # SYS10463532 (系统编号)
        r'^\d{11,}$',  # 纯数字11位以上(电话号码)
        r'^\d{4}-\d{4}$',  # 年份范围
        r'^cid:',  # cid:.png
        r'^\[cid:',  # [cid:
        r'^number$',  # "number"
        r'^Part$',  # "Part"
        r'^Description$',  # "Description"
        r'^Phone',  # Phone:
        r'^Powered by',  # Powered by
        r'^\d{1,3}--$',  # 008--, 156--
    ]
    
    for pattern in exclude_patterns:
        if re.match(pattern, value, re.IGNORECASE):
            return False
    
    # 检查是否匹配件号模式
    for pattern in PART_NUMBER_PATTERNS:
        if re.match(pattern, value):
            return True
    
    # 如果包含常见的航空件号特征，也可能是件号
    if re.search(r'[A-Za-z]', value) and re.search(r'[0-9]', value):
        return True
    
    return False

def is_valid_condition(value):
    """验证是否为有效条件"""
    if not value:
        return True  # 空值允许
    
    value = value.strip().upper()
    return value in [c.upper() for c in VALID_CONDITIONS]

def is_valid_price(value):
    """验证是否为有效价格"""
    if not value:
        return True  # 空值允许
    
    # 提取数字
    numbers = re.findall(r'[\d,]+\.?\d*', value.replace(',', ''))
    return len(numbers) > 0

def check_row_quality(row, headers):
    """检查单行数据质量，返回问题列表"""
    issues = []
    
    for i, (header, value) in enumerate(zip(headers, row.values())):
        if not value:
            continue
        
        header_lower = header.lower()
        value = str(value).strip()
        
        # 检查 PartNumber 列
        if 'partnumber' in header_lower or 'part' in header_lower:
            if value and not is_valid_part_number(value):
                issues.append(f"PartNumber列包含非件号内容: '{value[:30]}'")
        
        # 检查 Condition 列
        elif 'condition' in header_lower:
            if value and not is_valid_condition(value):
                issues.append(f"Condition列包含无效条件: '{value}'")
        
        # 检查 Price 列
        elif 'price' in header_lower:
            if value and not is_valid_price(value):
                issues.append(f"Price列包含无效价格: '{value}'")
        
        # 检查 Description 列
        elif 'description' in header_lower:
            # 描述列允许较自由的内容，但检查一些明显错误
            if re.match(r'^\[cid:', value) or re.match(r'^signature', value, re.IGNORECASE):
                issues.append(f"Description列包含无效内容: '{value[:30]}'")
    
    return issues

def clean_file(filepath):
    """清洗单个文件"""
    print(f"\n{'='*60}")
    print(f"检查文件: {Path(filepath).name}")
    print('='*60)
    
    # 读取文件
    rows = []
    headers = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            rows.append(row)
    
    print(f"总行数: {len(rows)}")
    print(f"列名: {', '.join(headers)}")
    
    # 检查每行
    good_rows = []
    bad_rows = []
    
    for row in rows:
        issues = check_row_quality(row, headers)
        
        if issues:
            bad_rows.append((row, issues))
        else:
            good_rows.append(row)
    
    print(f"\n有效行: {len(good_rows)}")
    print(f"问题行: {len(bad_rows)}")
    
    # 显示问题行示例
    if bad_rows:
        print(f"\n问题行示例 (前5条):")
        for i, (row, issues) in enumerate(bad_rows[:5]):
            pn = row.get('PartNumber', row.get('PartNumbers', ''))[:30]
            desc = row.get('Description', row.get('Summary', ''))[:30]
            print(f"  {i+1}. PartNumber: '{pn}' | Issues: {'; '.join(issues[:2])}")
    
    # 保存清洗后的数据
    if bad_rows:
        output_path = filepath.replace('.csv', '_cleaned.csv')
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(good_rows)
        
        print(f"\n清洗后文件已保存: {Path(output_path).name}")
        print(f"删除了 {len(bad_rows)} 行问题数据")
        
        return output_path
    
    return None

def main():
    print("="*60)
    print("数据质量检查和清洗工具")
    print("="*60)
    
    cleaned_files = []
    
    for filepath in FILES_TO_CHECK:
        try:
            result = clean_file(filepath)
            if result:
                cleaned_files.append(result)
        except Exception as e:
            print(f"处理文件失败 {filepath}: {e}")
    
    print("\n" + "="*60)
    print("清洗完成")
    print("="*60)
    
    if cleaned_files:
        print(f"共生成 {len(cleaned_files)} 个清洗后的文件")
        for f in cleaned_files:
            print(f"  - {Path(f).name}")
    else:
        print("所有文件数据质量良好，无需清洗")

if __name__ == '__main__':
    main()