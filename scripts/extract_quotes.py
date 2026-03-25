#!/usr/bin/env python3
"""
从 sale@aeroedgeglobal.com 邮箱提取 RFQ 报价信息
汇总到 Excel 表格供老板筛选最优报价
"""

import json
import os
from datetime import datetime

# 从邮件预览中手动提取的报价信息（根据截图）
QUOTES_DATA = [
    {
        "供应商": "深圳市兴广富电子有限公司",
        "联系人": "Frank Lau",
        "邮箱": "frank@xgf.com",  # 待确认
        "件号": "814462-1",
        "金额_USD": 1500,
        "数量": "待确认",
        "状态": "NEW",
        "交期": "STOCK",
        "发货地": "深圳",
        "备注": "COC only",
        "邮件时间": "2026-03-25 10:16"
    },
    {
        "供应商": "ITS",
        "联系人": "Derek Oeur",
        "邮箱": "derek.oeur@itsparts.com",
        "件号": "待查看邮件详情",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "RFQ #SYS10527586",
        "邮件时间": "2026-03-25 09:01"
    },
    {
        "供应商": "ITS",
        "联系人": "Derek Oeur",
        "邮箱": "derek.oeur@itsparts.com",
        "件号": "待查看邮件详情",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "RFQ #SYS10527648",
        "邮件时间": "2026-03-25 09:00"
    },
    {
        "供应商": "Jacaero Industries, LLC",
        "联系人": "Connor Jacobs",
        "邮箱": "connor@jacaero.com",
        "件号": "待查看邮件详情",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "RFQ #SYS10527574",
        "邮件时间": "2026-03-25 08:36"
    },
    {
        "供应商": "Jacaero Industries, LLC",
        "联系人": "Connor Jacobs",
        "邮箱": "connor@jacaero.com",
        "件号": "待查看邮件详情",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "RFQ #SYS10527590",
        "邮件时间": "2026-03-25 08:36"
    },
    {
        "供应商": "BROOKS & MALDINI CORPORATION",
        "联系人": "待确认",
        "邮箱": "sales@brooks-maldini.net",
        "件号": "TS30176",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "REF# BMA 5761992",
        "邮件时间": "2026-03-25 08:12"
    },
    {
        "供应商": "Aeroned",
        "联系人": "待确认",
        "邮箱": "待确认",
        "件号": "2G916-1039",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "RFQ from AEROEDGE",
        "邮件时间": "2026-03-25 08:10"
    },
    {
        "供应商": "AOG Logistics",
        "联系人": "Brittney Thomas",
        "邮箱": "待确认",
        "件号": "待查看邮件详情",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "RFQ #SYS10526819",
        "邮件时间": "2026-03-25 06:37"
    },
    {
        "供应商": "RIM Alliance",
        "联系人": "Jim Fagan",
        "邮箱": "jim@rimalliance.com",
        "件号": "待查看附件",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "QU-1071540, 带 PDF 附件",
        "邮件时间": "2026-03-25 03:20"
    },
    {
        "供应商": "BROOKS & MALDINI CORPORATION",
        "联系人": "待确认",
        "邮箱": "sales@brooks-maldini.net",
        "件号": "STD3359-2",
        "金额_USD": "待确认",
        "数量": "待确认",
        "状态": "待确认",
        "交期": "待确认",
        "发货地": "待确认",
        "备注": "REF# BMA 5760623",
        "邮件时间": "2026-03-25 02:32"
    },
]

# StockMarket 自动确认邮件（非真实报价，排除）
STOCKMARKET_CONFIRMATIONS = [
    "8-995-02",
    "CS203-04",
    "7517832-4",
    "40-656-5043",
    "501-1-14713-000",
    "CE2A26",
    "796880-5-006",
]

def main():
    print("=" * 60)
    print("RFQ20260324-02 报价汇总")
    print("邮箱：sale@aeroedgeglobal.com")
    print("提取时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    output_dir = os.path.join(os.path.dirname(__file__), "..")
    
    # 保存 JSON
    json_path = os.path.join(output_dir, "rfq_quotes_extracted.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(QUOTES_DATA, f, indent=2, ensure_ascii=False)
    print(f"\n详细数据已保存：{json_path}")
    
    # 打印表格
    print("\n" + "=" * 120)
    print(f"{'序号':<4} {'供应商':<35} {'PN':<15} {'金额':<10} {'状态':<8} {'交期':<10} {'联系人':<20}")
    print("=" * 120)
    
    for i, q in enumerate(QUOTES_DATA, 1):
        print(f"{i:<4} {q['供应商']:<35} {q['件号']:<15} {str(q['金额_USD']):<10} {q['状态']:<8} {q['交期']:<10} {q['联系人']:<20}")
    
    print("=" * 120)
    print(f"\n总计：{len(QUOTES_DATA)} 封报价邮件")
    print(f"StockMarket 自动确认：{len(STOCKMARKET_CONFIRMATIONS)} 封（已排除）")
    
    # 生成 CSV
    csv_path = os.path.join(output_dir, "rfq_quotes_summary.csv")
    with open(csv_path, "w", encoding="utf-8-sig") as f:
        headers = ["序号", "供应商", "联系人", "邮箱", "件号", "金额_USD", "数量", "状态", "交期", "发货地", "备注", "邮件时间"]
        f.write(",".join(headers) + "\n")
        for i, q in enumerate(QUOTES_DATA, 1):
            row = [
                str(i),
                q["供应商"],
                q["联系人"],
                q["邮箱"],
                q["件号"],
                str(q["金额_USD"]),
                q["数量"],
                q["状态"],
                q["交期"],
                q["发货地"],
                q["备注"],
                q["邮件时间"]
            ]
            f.write(",".join([f'"{x}"' if "," in str(x) else str(x) for x in row]) + "\n")
    
    print(f"CSV 表格已保存：{csv_path}")
    print("\n[!] 注意：部分详情需要逐封打开邮件获取，当前为预览提取")
    print("下一步：打开每封邮件获取完整报价详情（金额/数量/交期/附件）")

if __name__ == "__main__":
    main()
