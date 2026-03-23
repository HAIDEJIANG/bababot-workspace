#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单运行多个批次
"""

import subprocess
import time

def run_batch(batch_num):
    """运行单个批次"""
    print(f"正在运行批次 {batch_num}...")
    
    cmd = ["python", "batch_analysis_controller.py", "--batch", str(batch_num)]
    
    try:
        # 使用GBK编码避免中文乱码问题
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            # 从输出中提取关键信息
            for line in result.stdout.split('\n'):
                if "累计分析:" in line:
                    print(f"批次 {batch_num} 完成: {line.strip()}")
            return True
        else:
            print(f"批次 {batch_num} 失败")
            return False
    except Exception as e:
        print(f"批次 {batch_num} 错误: {str(e)}")
        return False

def main():
    print("开始运行多个LinkedIn分析批次")
    print("=" * 50)
    
    # 要运行的批次
    batches = [12, 13, 14, 15]
    
    successful = 0
    failed = 0
    
    for batch_num in batches:
        success = run_batch(batch_num)
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # 批次间暂停
        if batch_num != batches[-1]:
            print(f"等待3秒后继续下一个批次...")
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print(f"分析完成统计:")
    print(f"成功: {successful} 个批次")
    print(f"失败: {failed} 个批次")
    
    # 更新总进度
    print("\n更新总进度...")
    try:
        subprocess.run(["python", "batch_analysis_controller.py", "--update-summary"], 
                      capture_output=True, text=True, encoding='gbk')
        print("进度更新完成")
    except:
        print("进度更新失败")
    
    print("\n所有批次运行完成!")

if __name__ == '__main__':
    main()