#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行并行批次分析 - 简化版
"""

import subprocess
import time
from datetime import datetime

def run_single_batch(batch_num):
    """运行单个批次"""
    print(f"启动批次{batch_num}分析...")
    
    # 使用批处理控制器运行单个批次
    cmd = ["python", "batch_analysis_controller.py", "--batch", str(batch_num)]
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"批次{batch_num}完成 - 耗时: {elapsed:.1f}秒")
            return True
        else:
            print(f"批次{batch_num}失败")
            if result.stderr:
                print(f"错误信息: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"批次{batch_num}异常: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("LinkedIn联系人批量分析 - 并行模式")
    print("=" * 60)
    
    # 当前状态
    print("当前状态:")
    print("- 总联系人: 3,185位")
    print("- 已分析: 529位 (批次10已完成)")
    print("- 剩余: 2,656位")
    print("- 需要批次: 约27个批次 (每批100人)")
    
    # 运行多个批次
    batches_to_run = [11, 12, 13, 14, 15]  # 先运行5个批次
    
    print(f"\n准备运行批次: {batches_to_run}")
    print("预计新增分析: 500位联系人")
    print("预计完成进度: 约32.3%")
    
    # 运行批次
    successful_batches = []
    failed_batches = []
    
    for batch_num in batches_to_run:
        success = run_single_batch(batch_num)
        
        if success:
            successful_batches.append(batch_num)
        else:
            failed_batches.append(batch_num)
        
        # 批次间短暂暂停
        if batch_num != batches_to_run[-1]:
            print("批次间暂停3秒...")
            time.sleep(3)
    
    # 统计结果
    print(f"\n分析完成统计:")
    print(f"成功批次: {len(successful_batches)}个 - {successful_batches}")
    print(f"失败批次: {len(failed_batches)}个 - {failed_batches}")
    
    # 更新汇总
    print("\n更新分析汇总...")
    try:
        update_result = subprocess.run(
            ["python", "batch_analysis_controller.py", "--update-summary"],
            capture_output=True, text=True, encoding='utf-8'
        )
        
        if update_result.returncode == 0:
            print("汇总更新完成")
        else:
            print("汇总更新失败")
    except Exception as e:
        print(f"更新汇总时出错: {str(e)}")
    
    # 最终状态
    estimated_analyzed = 529 + (len(successful_batches) * 100)
    estimated_percentage = (estimated_analyzed / 3185) * 100
    
    print(f"\n预计最终状态:")
    print(f"- 已分析联系人: ~{estimated_analyzed}位")
    print(f"- 完成进度: ~{estimated_percentage:.1f}%")
    print(f"- 剩余联系人: ~{3185 - estimated_analyzed}位")
    
    print("\n" + "=" * 60)
    print("批量分析任务完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()