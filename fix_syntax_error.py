#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复analyze_linkedin_batch_100.py中的语法错误
"""

import re

def fix_syntax_error():
    # 读取文件
    with open('analyze_linkedin_batch_100.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找有问题的f-string部分
    # 从第351行开始的问题
    pattern = r'(report \+= f""".*?---\s*\*报告生成时间: \{datetime\.now\(\)\.strftime\(\'%Y-%m-%d %H:%M:%S\'\)\}\*\s*\*累计分析进度: \{end_index\}/\{total_contacts\}\*)'
    
    # 更简单的修复：确保f-string正确闭合
    # 找到所有未正确闭合的f-string
    lines = content.split('\n')
    fixed_lines = []
    
    in_fstring = False
    fstring_start = 0
    
    for i, line in enumerate(lines):
        if 'report += f"""' in line and not in_fstring:
            in_fstring = True
            fstring_start = i
            fixed_lines.append(line)
        elif in_fstring and '"""' in line:
            in_fstring = False
            fixed_lines.append(line)
        elif in_fstring:
            # 在f-string内部，确保变量引用正确
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # 重新组合
    fixed_content = '\n'.join(fixed_lines)
    
    # 写入修复后的文件
    with open('analyze_linkedin_batch_100_fixed.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("已创建修复后的文件: analyze_linkedin_batch_100_fixed.py")
    
    # 测试修复后的文件
    try:
        exec(compile(fixed_content, 'analyze_linkedin_batch_100_fixed.py', 'exec'))
        print("语法检查通过!")
    except SyntaxError as e:
        print(f"语法错误: {e}")
        print(f"错误位置: 第{e.lineno}行")

if __name__ == '__main__':
    fix_syntax_error()