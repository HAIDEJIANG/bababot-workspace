import pandas as pd
import os

media_dir = r"C:\Users\Haide\.openclaw\media\inbound"
files = [f for f in os.listdir(media_dir) if "RFQ20260313" in f and "731ebc59" in f]

if files:
    file_path = os.path.join(media_dir, files[0])
    df = pd.read_excel(file_path, engine='xlrd')
    
    # 件号在第 2 列 (Unnamed: 1)，从第 7 行开始是数据（索引 6 之后）
    # 提取件号列
    part_numbers = []
    for idx in range(6, len(df)):
        pn = df.iloc[idx, 1]  # 第 2 列是 PN
        if pd.notna(pn) and str(pn).strip():
            part_numbers.append(str(pn).strip())
    
    print("=== RFQ20260313-01 件号清单 ===")
    print(f"总件号数：{len(part_numbers)}")
    print()
    for i, pn in enumerate(part_numbers, 1):
        print(f"{i:2d}. {pn}")
    
    print()
    print("=== 任务分配 ===")
    print("前 5 个件号 (StockMarket 询价 #1):")
    for i, pn in enumerate(part_numbers[:5], 1):
        print(f"  {i}. {pn}")
    
    print()
    print("第 6-10 个件号 (StockMarket 询价 #2):")
    for i, pn in enumerate(part_numbers[5:10], 6):
        print(f"  {i}. {pn}")
    
    # 保存为文本文件
    with open('rfq20260313_part_numbers.txt', 'w', encoding='utf-8') as f:
        f.write("RFQ20260313-01 件号清单\n")
        f.write("=" * 50 + "\n\n")
        for i, pn in enumerate(part_numbers, 1):
            f.write(f"{i:2d}. {pn}\n")
    
    print()
    print("已保存到：rfq20260313_part_numbers.txt")
