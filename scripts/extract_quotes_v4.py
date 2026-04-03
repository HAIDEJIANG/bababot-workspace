#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取最新供应商报价 v4 - 精确解析 PDF 格式
"""

import fitz  # pymupdf
import pandas as pd
import os
import re
from datetime import datetime
from pathlib import Path

DOWNLOAD_DIR = Path(r"C:\Users\Haide\Downloads")
MASTER_TABLE = r"C:\Users\Haide\Desktop\Quotes_Master_Table.csv"

# 最新报价 PDF 列表（邮件 ID 对应）
PDF_FILES = [
    {"file": "Quotation #Q381377 Cust Ref#9DX404700-01 4-1-2026 3-57-02 PM.pdf", "supplier": "Tiger Enterprises", "contact": "Michelle Smith", "email": ""},
    {"file": "Quotation #Q351095 4-1-2026 11-26-31 AM.pdf", "supplier": "MGT Group", "contact": "", "email": "sales.us@mgt-group.aero"},
    {"file": "Quotation #Q179177  01-04-2026 14-33-20.pdf", "supplier": "Claire World", "contact": "Claire", "email": ""},
    {"file": "QU-3825291.pdf", "supplier": "Pacific Aerospace", "contact": "", "email": "aq@sales.pac-air.com"},
    {"file": "Quotation #C10232278 01-04-2026 15-13-49.pdf", "supplier": "Unknown", "contact": "Hubert JUBAULT", "email": ""},
    {"file": "Quotation #622648 Cust Ref#2G916-1039  01-04-2026 13-06-52.pdf", "supplier": "Unknown", "contact": "Fleur Woodage", "email": ""},
]

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def parse_quote_detailed(text, pdf_info):
    """精确解析报价单"""
    quotes = []
    
    # 提取 PN 和价格（格式：PN \n 描述 \n 条件 \n 数量 \n 价格）
    # 模式 1: 9DX404700-01   FLASH TUBE \n NE \n $1, 100.00EA
    pn_price_pattern = r'([A-Z0-9\-]{6,})\s+([A-Z\s]+)\n?\s*(NE|NS|FN|OH|RP|SV|TESTED|INSPECTED|AR|USED)?\s*\n?\s*\$?([\d,]+\.?\d*)\s*(EA|EACH)?'
    
    matches = re.findall(pn_price_pattern, text, re.IGNORECASE)
    
    for match in matches:
        pn = match[0].strip()
        desc = match[1].strip()
        condition = match[2].strip().upper() if match[2] else ""
        price_str = match[3].replace(',', '').strip()
        
        try:
            price = float(price_str)
        except:
            price = ""
        
        # 提取数量（如果有）
        qty_pattern = rf'{re.escape(pn)}.*?\n.*?(\d+)\s+NE'
        qty_match = re.search(qty_pattern, text, re.IGNORECASE)
        qty = qty_match.group(1) if qty_match else ""
        
        # 提取交期
        delivery = ""
        if "IN STOCK" in text:
            delivery = "IN STOCK"
        elif "Delivery" in text:
            del_match = re.search(r'Delivery[^:]*:\s*(.+)', text)
            if del_match:
                delivery = del_match.group(1).strip()
        
        # 提取参考号
        ref_match = re.search(r'Ref\s*#[:\s]*([A-Z0-9\-]+)', text)
        ref_num = ref_match.group(1) if ref_match else ""
        
        quote = {
            '需求编号': f'RFQ20260401-01',
            '序号': '',
            '供应商': pdf_info['supplier'],
            '联系人': pdf_info['contact'],
            '邮箱': pdf_info['email'],
            '件号': pn,
            '描述': desc,
            '条件': condition,
            '数量 (需求)': qty,
            '数量 (可供)': qty,
            '单价 USD': price,
            '总价 USD': price,
            '交期': delivery,
            '发货地': '',
            'S/N': '',
            'Trace To': '',
            'Tag Type': '',
            '报价日期': datetime.now().strftime('%Y-%m-%d'),
            '备注': f"Quote: {pdf_info['file'][:50]}"
        }
        quotes.append(quote)
    
    return quotes

def main():
    all_quotes = []
    
    print("Starting quote extraction...")
    
    for pdf_info in PDF_FILES:
        pdf_path = DOWNLOAD_DIR / pdf_info['file']
        if pdf_path.exists():
            print(f"\nProcessing: {pdf_info['file'][:60]}...")
            text = extract_text_from_pdf(pdf_path)
            quotes = parse_quote_detailed(text, pdf_info)
            all_quotes.extend(quotes)
            print(f"  Found {len(quotes)} quote(s)")
            for q in quotes:
                print(f"    PN: {q['件号']} | {q['描述']} | Cond: {q['条件']} | Price: ${q['单价 USD']}")
        else:
            print(f"\nFile not found: {pdf_info['file']}")
    
    print(f"\nTotal: {len(all_quotes)} quotes extracted")
    
    # 读取现有总表
    if os.path.exists(MASTER_TABLE):
        df_existing = pd.read_csv(MASTER_TABLE)
        print(f"Existing records: {len(df_existing)}")
        
        if all_quotes:
            df_new = pd.DataFrame(all_quotes)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            # 去重
            df_combined = df_combined.drop_duplicates(subset=['件号', '供应商', '单价 USD'], keep='last')
            
            print(f"Combined records: {len(df_combined)}")
            
            df_combined.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
            print(f"\n[OK] Updated master table: {MASTER_TABLE}")
    else:
        if all_quotes:
            df_new = pd.DataFrame(all_quotes)
            df_new.to_csv(MASTER_TABLE, index=False, encoding='utf-8-sig')
            print(f"\n[OK] Created master table: {MASTER_TABLE}")
    
    # 汇总统计
    if all_quotes:
        print("\n" + "="*60)
        print("SUMMARY - New Quotes Added:")
        print("="*60)
        for q in all_quotes:
            print(f"PN: {q['件号']} | Supplier: {q['供应商']} | Price: ${q['单价 USD']} | Cond: {q['条件']}")

if __name__ == "__main__":
    main()
