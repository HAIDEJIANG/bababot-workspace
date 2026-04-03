#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取最新供应商报价并汇总到报价总表
"""

import fitz  # pymupdf
import pandas as pd
import os
import re
from datetime import datetime
from pathlib import Path

# 下载目录
DOWNLOAD_DIR = Path(r"C:\Users\Haide\Downloads")

# 报价总表路径
MASTER_TABLE = r"C:\Users\Haide\Desktop\Quotes_Master_Table.csv"

# 需要处理的 PDF 文件（最新的报价）
PDF_FILES = [
    "Quotation #Q381377 Cust Ref#9DX404700-01 4-1-2026 3-57-02 PM.pdf",  # 1720726315 - Michelle Smith
    "Quotation #Q351095 4-1-2026 11-26-31 AM.pdf",  # 1720726311 - MGT Group
    "Quotation #Q179177  01-04-2026 14-33-20.pdf",  # 1720726226 - Claire World
    "QU-3825291.pdf",  # 1720726223 - Pacific Aerospace
    "Quotation #C10232278 01-04-2026 15-13-49.pdf",  # 1720726221 - Hubert JUBAULT
    "Quotation #622648 Cust Ref#2G916-1039  01-04-2026 13-06-52.pdf",  # 1720726138 - Fleur Woodage
]

def extract_text_from_pdf(pdf_path):
    """从 PDF 提取文本"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def parse_quote(text, pdf_filename):
    """解析报价文本，提取结构化数据"""
    quotes = []
    
    # 尝试提取供应商信息
    supplier = "Unknown"
    contact = ""
    email = ""
    
    # 常见供应商邮箱模式
    email_patterns = [
        r'[\w\.-]+@[\w\.-]+\.\w+',
        r'From:\s*([\w\s]+)<([\w\.-]+@[\w\.-]+\.\w+)>',
    ]
    
    for pattern in email_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            if isinstance(matches[0], tuple):
                contact = matches[0][0].strip()
                email = matches[0][1].strip()
            else:
                email = matches[0].strip()
            break
    
    # 从文件名提取线索
    if "Michelle Smith" in pdf_filename or "Q381377" in pdf_filename:
        supplier = "Unknown Supplier (Michelle Smith)"
        email = "michelle@example.com"
    elif "MGT" in text or "Q351095" in pdf_filename:
        supplier = "MGT Group"
        email = "sales.us@mgt-group.aero"
    elif "Q179177" in pdf_filename:
        supplier = "Claire World"
    elif "QU-3825291" in pdf_filename or "Pac-Air" in text:
        supplier = "Pacific Aerospace"
        email = "aq@sales.pac-air.com"
    elif "C10232278" in pdf_filename:
        supplier = "Unknown (Hubert JUBAULT)"
        email = "hubert@example.com"
    elif "622648" in pdf_filename:
        supplier = "Unknown (Fleur Woodage)"
    
    # 提取 PN、价格、条件等关键信息
    # PN 模式
    pn_patterns = [
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'Part\s*(?:Number|No)[:\s]*([A-Z0-9\-]+)',
        r'([A-Z0-9]{3,}-[A-Z0-9\-]+)',
    ]
    
    # 价格模式
    price_patterns = [
        r'USD\s*\$?([\d,]+\.?\d*)',
        r'\$([\d,]+\.?\d*)\s*USD',
        r'Price[:\s]*\$?([\d,]+\.?\d*)',
        r'Unit\s*Price[:\s]*\$?([\d,]+\.?\d*)',
    ]
    
    # 条件模式
    condition_patterns = [
        r'(?:Condition[:\s]*)(FN|NE|NS|OH|RP|SV|TESTED|INSPECTED|AR|USED)',
        r'\b(FN|NE|NS|OH|RP|SV|TESTED|INSPECTED|AR|USED)\b',
    ]
    
    # 尝试提取 PN
    pn_found = None
    for pattern in pn_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pn_found = match.group(1).strip()
            break
    
    # 尝试提取价格
    price_found = None
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                price_found = float(price_str)
            except:
                pass
            break
    
    # 尝试提取条件
    condition_found = ""
    for pattern in condition_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            condition_found = match.group(1).upper()
            break
    
    # 如果找到了 PN，添加报价记录
    if pn_found:
        quotes.append({
            '需求编号': 'RFQ20260401-01',  # 最新的 RFQ
            '序号': '',
            '供应商': supplier,
            '联系人': contact,
            '邮箱': email,
            '件号': pn_found,
            '描述': '',
            '条件': condition_found,
            '数量 (需求)': '',
            '数量 (可供)': '',
            '单价 USD': price_found if price_found else '',
            '总价 USD': price_found if price_found else '',
            '交期': '',
            '发货地': '',
            'S/N': '',
            'Trace To': '',
            'Tag Type': '',
            '报价日期': datetime.now().strftime('%Y-%m-%d'),
            '备注': f'From PDF: {pdf_filename}'
        })
    
    return quotes

def main():
    all_quotes = []
    
    print("开始提取最新报价...")
    
    for pdf_file in PDF_FILES:
        pdf_path = DOWNLOAD_DIR / pdf_file
        if pdf_path.exists():
            print(f"\n处理：{pdf_file}")
            text = extract_text_from_pdf(pdf_path)
            quotes = parse_quote(text, pdf_file)
            all_quotes.extend(quotes)
            print(f"  找到 {len(quotes)} 条报价")
        else:
            print(f"\n文件不存在：{pdf_file}")
    
    print(f"\n总计找到 {len(all_quotes)} 条报价")
    
    # 读取现有总表
    if os.path.exists(MASTER_TABLE):
        df_existing = pd.read_csv(MASTER_TABLE)
        print(f"现有总表记录数：{len(df_existing)}")
        
        # 合并新报价
        if all_quotes:
            df_new = pd.DataFrame(all_quotes)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            # 去重（基于件号 + 供应商 + 单价）
            df_combined = df_combined.drop_duplicates(subset=['件号', '供应商', '单价 USD'], keep='last')
            
            print(f"合并后总记录数：{len(df_combined)}")
            
            # 保存
            df_combined.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
            print(f"\n[OK] 已更新报价总表：{MASTER_TABLE}")
    else:
        # 创建新总表
        if all_quotes:
            df_new = pd.DataFrame(all_quotes)
            df_new.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
            print(f"\n[OK] 已创建报价总表：{MASTER_TABLE}")
    
    # 输出提取结果
    if all_quotes:
        print("\n[DATA] 新提取的报价明细:")
        for q in all_quotes:
            print(f"  PN: {q['件号']} | Supplier: {q['供应商']} | Price: ${q['单价 USD']} | Cond: {q['条件']}")

if __name__ == "__main__":
    main()
