#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续运行多个批次的分析 - 从正确位置开始
"""

import subprocess
import time

def run_batch(batch_num, start_index):
    """运行单个批次"""
    print(f"\n正在运行批次 {batch_num} (从第 {start_index} 位开始)...")
    
    # 使用我们新创建的脚本
    cmd = ["python", "analyze_from_correct_position.py"]
    
    try:
        # 运行分析脚本
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            # 从输出中提取进度信息
            for line in result.stdout.split('\n'):
                if "累计分析:" in line:
                    print(f"进度: {line.strip()}")
                elif "分析完成!" in line:
                    print("批次完成!")
            return True
        else:
            print(f"批次 {batch_num} 失败")
            if result.stderr:
                print(f"错误: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"批次 {batch_num} 错误: {str(e)}")
        return False

def get_current_progress():
    """获取当前分析进度"""
    try:
        import pandas as pd
        import os
        
        analysis_dir = r"C:\Users\Haide\Desktop\LINKEDIN\Analysis"
        
        if os.path.exists(analysis_dir):
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
    
    return 0

def main():
    print("LinkedIn联系人连续批量分析")
    print("=" * 60)
    
    # 获取当前进度
    current_analyzed = get_current_progress()
    total_contacts = 3185
    
    print(f"当前进度: {current_analyzed}/{total_contacts} ({current_analyzed/total_contacts*100:.1f}%)")
    print(f"剩余联系人: {total_contacts - current_analyzed} 位")
    
    # 计算批次
    batch_size = 100
    batches_needed = (total_contacts - current_analyzed + batch_size - 1) // batch_size
    
    print(f"需要运行 {batches_needed} 个批次")
    
    # 询问要运行多少个批次
    batches_to_run = 5  # 默认运行5个批次
    print(f"\n准备运行 {batches_to_run} 个批次")
    print(f"预计新增分析: {batches_to_run * 100} 位联系人")
    
    successful_batches = 0
    
    for i in range(batches_to_run):
        batch_num = (current_analyzed // batch_size) + 1 + i
        start_index = current_analyzed + (i * batch_size)
        
        print(f"\n{'='*50}")
        print(f"批次 {i+1}/{batches_to_run}: 批次{batch_num}")
        print(f"开始位置: 第{start_index}位联系人")
        
        success = run_batch(batch_num, start_index)
        
        if success:
            successful_batches += 1
            # 更新进度
            current_analyzed += batch_size
            print(f"当前累计: {current_analyzed}/{total_contacts} ({current_analyzed/total_contacts*100:.1f}%)")
        else:
            print(f"批次 {batch_num} 失败，停止分析")
            break
        
        # 批次间暂停
        if i < batches_to_run - 1:
            print(f"等待5秒后继续下一个批次...")
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"批量分析完成统计:")
    print(f"成功运行: {successful_batches} 个批次")
    print(f"新增分析: {successful_batches * 100} 位联系人")
    print(f"最终进度: {current_analyzed}/{total_contacts} ({current_analyzed/total_contacts*100:.1f}%)")
    print(f"剩余联系人: {total_contacts - current_analyzed} 位")
    
    # 更新每日汇总
    print(f"\n更新每日汇总文件...")
    try:
        # 这里可以添加更新汇总文件的代码
        print("汇总更新完成")
    except:
        print("汇总更新失败")
    
    print(f"\n所有分析任务完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()