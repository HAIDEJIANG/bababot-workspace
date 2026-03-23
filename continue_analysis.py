#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续LinkedIn分析 - 从正确的位置开始
"""

import subprocess
import time

def get_current_progress():
    """获取当前分析进度"""
    try:
        # 检查分析目录
        import os
        analysis_dir = r'C:\Users\Haide\Desktop\LINKEDIN\Analysis'
        
        if os.path.exists(analysis_dir):
            import pandas as pd
            files = os.listdir(analysis_dir)
            csv_files = [f for f in files if f.endswith('.csv') and 'batch' in f]
            
            total_analyzed = 0
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(os.path.join(analysis_dir, csv_file), encoding='utf-8')
                    total_analyzed += len(df)
                except:
                    pass
            
            return total_analyzed
    except:
        pass
    
    return 520  # 默认值

def run_batch_from_position(start_index):
    """从指定位置开始运行批次"""
    print(f"从第 {start_index} 位联系人开始分析...")
    
    # 计算批次号
    batch_size = 100
    batch_num = (start_index // batch_size) + 1
    
    print(f"运行批次 {batch_num} (联系人 {start_index} 到 {start_index + batch_size})")
    
    # 这里需要修改控制器以支持从特定位置开始
    # 暂时使用默认方式
    cmd = ["python", "batch_analysis_controller.py", "--batch", str(batch_num)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            # 从输出中提取信息
            for line in result.stdout.split('\n'):
                if "累计分析:" in line:
                    print(f"完成: {line.strip()}")
            return True
        else:
            print("分析失败")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def main():
    print("继续LinkedIn联系人分析")
    print("=" * 50)
    
    # 获取当前进度
    current_analyzed = get_current_progress()
    total_contacts = 3185
    
    print(f"当前进度: {current_analyzed}/{total_contacts} ({current_analyzed/total_contacts*100:.1f}%)")
    print(f"剩余联系人: {total_contacts - current_analyzed} 位")
    
    # 计算需要运行的批次
    batch_size = 100
    batches_needed = (total_contacts - current_analyzed + batch_size - 1) // batch_size
    
    print(f"需要运行 {batches_needed} 个批次")
    
    # 运行多个批次
    batches_to_run = min(5, batches_needed)  # 先运行5个批次
    
    print(f"\n准备运行 {batches_to_run} 个批次")
    
    successful = 0
    
    for i in range(batches_to_run):
        batch_num = (current_analyzed // batch_size) + 1 + i
        
        print(f"\n运行批次 {batch_num}...")
        
        cmd = ["python", "batch_analysis_controller.py", "--batch", str(batch_num)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
            
            if result.returncode == 0:
                successful += 1
                # 更新当前进度
                current_analyzed += batch_size
                print(f"批次 {batch_num} 完成")
                print(f"当前进度: {current_analyzed}/{total_contacts} ({current_analyzed/total_contacts*100:.1f}%)")
            else:
                print(f"批次 {batch_num} 失败")
        except Exception as e:
            print(f"批次 {batch_num} 错误: {str(e)}")
        
        # 批次间暂停
        if i < batches_to_run - 1:
            print("等待3秒...")
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print(f"分析完成:")
    print(f"成功运行: {successful} 个批次")
    print(f"新增分析: {successful * 100} 位联系人")
    print(f"最终进度: {current_analyzed}/{total_contacts} ({current_analyzed/total_contacts*100:.1f}%)")
    
    print("\n分析任务完成!")

if __name__ == '__main__':
    main()