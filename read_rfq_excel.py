import pandas as pd
import os

# 找到正确的文件路径
media_dir = r"C:\Users\Haide\.openclaw\media\inbound"
files = [f for f in os.listdir(media_dir) if "RFQ20260313" in f and "731ebc59" in f]

if files:
    file_path = os.path.join(media_dir, files[0])
    print(f"找到文件：{files[0]}")
    print(f"完整路径：{file_path}")
    print()
    
    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path, engine='xlrd')
        print("=== 询价单 RFQ20260313-01 内容 ===")
        print(df.to_string())
        print()
        print("=== 件号列表 (Part Numbers) ===")
        
        # 尝试识别件号列
        for col in df.columns:
            col_str = str(col).lower()
            if 'part' in col_str or '件号' in col_str or 'pn' in col_str or 'item' in col_str.lower():
                part_numbers = df[col].dropna().tolist()
                for i, pn in enumerate(part_numbers, 1):
                    print(f"{i}. {pn}")
                break
        else:
            # 如果没有找到明确的件号列，输出第一列
            print("（输出第一列数据）")
            for i, val in enumerate(df.iloc[:, 0].dropna().tolist(), 1):
                print(f"{i}. {val}")
                
    except Exception as e:
        print(f"读取错误：{e}")
        # 尝试用 xlrd 直接读取
        import xlrd
        wb = xlrd.open_workbook(file_path)
        print(f"\nExcel 工作簿包含 {wb.nsheets} 个工作表")
        for sheet in wb.sheets():
            print(f"\n工作表：{sheet.name}")
            for row_idx in range(min(20, sheet.nrows)):
                row = sheet.row_values(row_idx)
                print(f"  行{row_idx+1}: {row}")
else:
    print("未找到询价单文件")
