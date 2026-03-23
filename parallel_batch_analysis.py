#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行批量分析控制器
同时运行多个批次的分析，提高处理效率
"""

import subprocess
import threading
import time
from datetime import datetime
import os

def run_batch(batch_num):
    """运行单个批次的分析"""
    print(f"🚀 启动批次{batch_num}分析...")
    
    # 构建命令
    cmd = ["python", "batch_analysis_controller.py", "--batch", str(batch_num)]
    
    try:
        # 运行命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ 批次{batch_num}分析完成")
            return True
        else:
            print(f"❌ 批次{batch_num}分析失败: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ 批次{batch_num}执行错误: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("LinkedIn联系人并行批量分析系统")
    print("=" * 60)
    
    # 检查当前进度
    print("📊 检查当前分析进度...")
    check_cmd = ["python", "batch_analysis_controller.py", "--check-progress"]
    result = subprocess.run(check_cmd, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode != 0:
        print("❌ 无法检查进度，请先修复问题")
        return
    
    # 解析进度信息
    output = result.stdout
    if "累计分析:" in output:
        # 提取已分析数量
        for line in output.split('\n'):
            if "累计分析:" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    analyzed = parts[1].strip().split(" ")[0]
                    print(f"📈 当前已分析: {analyzed}位联系人")
    
    # 计算需要运行的批次
    total_contacts = 3185
    analyzed = 529  # 从刚才的输出中获取
    remaining = total_contacts - analyzed
    
    print(f"📋 剩余联系人: {remaining}位")
    
    # 计算批次
    batch_size = 100
    batches_needed = (remaining + batch_size - 1) // batch_size
    
    print(f"📦 需要运行 {batches_needed} 个批次")
    
    # 询问用户要运行多少个批次
    print("\n🔧 配置并行分析:")
    print("1. 单批次分析 (安全模式)")
    print("2. 双批次并行 (平衡模式)")
    print("3. 三批次并行 (快速模式)")
    print("4. 自定义批次数量")
    
    try:
        choice = input("请选择模式 (1-4): ").strip()
        
        if choice == "1":
            parallel_count = 1
            batches_to_run = min(3, batches_needed)  # 先运行3个批次
        elif choice == "2":
            parallel_count = 2
            batches_to_run = min(6, batches_needed)  # 先运行6个批次
        elif choice == "3":
            parallel_count = 3
            batches_to_run = min(9, batches_needed)  # 先运行9个批次
        elif choice == "4":
            parallel_count = int(input("请输入并行批次数量 (1-5): "))
            batches_to_run = int(input(f"请输入要运行的总批次数量 (1-{batches_needed}): "))
        else:
            print("使用默认模式: 双批次并行")
            parallel_count = 2
            batches_to_run = min(6, batches_needed)
        
        print(f"\n⚡ 启动 {parallel_count} 个并行分析进程")
        print(f"📊 总共运行 {batches_to_run} 个批次")
        
        # 计算批次号
        start_batch = 11  # 批次10已完成，从11开始
        batch_numbers = list(range(start_batch, start_batch + batches_to_run))
        
        # 创建线程运行批次
        threads = []
        results = []
        
        # 分批运行
        for i in range(0, len(batch_numbers), parallel_count):
            current_batches = batch_numbers[i:i+parallel_count]
            
            print(f"\n🔧 运行批次: {current_batches}")
            
            # 为每个批次创建线程
            batch_threads = []
            for batch_num in current_batches:
                thread = threading.Thread(target=lambda b=batch_num, r=results: r.append((b, run_batch(b))))
                thread.start()
                batch_threads.append(thread)
            
            # 等待当前批次完成
            for thread in batch_threads:
                thread.join()
            
            print(f"✅ 批次 {current_batches} 完成")
            
            # 短暂暂停，避免资源竞争
            time.sleep(2)
        
        # 统计结果
        successful = sum(1 for _, success in results if success)
        failed = len(results) - successful
        
        print(f"\n📊 分析完成统计:")
        print(f"✅ 成功: {successful} 个批次")
        print(f"❌ 失败: {failed} 个批次")
        
        if failed > 0:
            print("失败的批次:")
            for batch_num, success in results:
                if not success:
                    print(f"  - 批次{batch_num}")
        
        # 更新总进度
        print("\n🔄 更新总进度...")
        subprocess.run(["python", "batch_analysis_controller.py", "--update-summary"])
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断分析")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

if __name__ == '__main__':
    main()