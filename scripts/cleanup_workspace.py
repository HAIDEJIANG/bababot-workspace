#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Workspace Cleanup Script
清理系统垃圾和无效信息

用法：python scripts/cleanup_workspace.py --dry-run  # 预览
      python scripts/cleanup_workspace.py --execute  # 执行
"""

import os
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(r"C:\Users\Haide\.openclaw\workspace")
DESKTOP_REAL_POSTS = Path(r"C:\Users\Haide\Desktop\real business post")
DESKTOP_LINKEDIN = Path(r"C:\Users\Haide\Desktop\LINKEDIN")

def get_folder_size(path):
    """计算文件夹大小 (MB)"""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except:
        pass
    return total / (1024 * 1024)

def cleanup_subagent_logs(days_old=7, dry_run=True):
    """清理旧的 subagent 运行日志"""
    subagents_dir = WORKSPACE / "subagents"
    if not subagents_dir.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days_old)
    removed = []
    
    for run_dir in subagents_dir.iterdir():
        if not run_dir.is_dir():
            continue
        
        # 从目录名提取日期 (run_20260327_xxxxxx)
        try:
            date_str = run_dir.name.split('_')[1]
            run_date = datetime.strptime(date_str, '%Y%m%d')
            
            if run_date < cutoff:
                size_mb = get_folder_size(run_dir)
                removed.append((str(run_dir), size_mb))
                if not dry_run:
                    shutil.rmtree(run_dir)
        except:
            pass
    
    return removed

def cleanup_old_csv_files(folder, days_old=7, dry_run=True):
    """清理旧的 CSV 文件"""
    if not folder.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days_old)
    removed = []
    
    # 保留主表文件
    keep_patterns = ['Master_Table', '_Master_', 'latest', 'business_leads']
    
    for csv_file in folder.glob('*.csv'):
        # 跳过主表文件
        if any(pat in csv_file.name for pat in keep_patterns):
            continue
        
        if csv_file.stat().st_mtime < cutoff.timestamp():
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            removed.append((str(csv_file), size_mb))
            if not dry_run:
                csv_file.unlink()
    
    return removed

def cleanup_test_scripts(folder, dry_run=True):
    """清理测试脚本（包含 test, temp, backup, fixed, stable 等关键词）"""
    if not folder.exists():
        return []
    
    test_keywords = ['test_', '_test', 'temp_', '_temp', 'backup', '_backup', 
                     '_fixed', '_stable', '_simple', '_edge', '_running', 
                     '_direct', '_cdp_', 'check_', 'clean_']
    
    # 保留的关键脚本
    keep_scripts = [
        'linkedin_v8_enhanced.py',
        'linkedin_leads_monitor.py',
        'sync_linkedin_data.py',
        'linkedin_collection_v4_webtop.py',
        'stockmarket_rfq.py',
        'heartbeat_optimized.py',
    ]
    
    removed = []
    
    for py_file in folder.glob('*.py'):
        # 跳过保留的脚本
        if py_file.name in keep_scripts:
            continue
        
        # 检查是否包含测试关键词
        if any(kw in py_file.name.lower() for kw in test_keywords):
            size_mb = py_file.stat().st_size / (1024 * 1024)
            removed.append((str(py_file), size_mb))
            if not dry_run:
                py_file.unlink()
    
    return removed

def cleanup_old_memory_logs(folder, days_old=30, dry_run=True):
    """清理旧的内存日志文件（linkedin_collection_*.md）"""
    if not folder.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days_old)
    removed = []
    
    for md_file in folder.glob('linkedin_collection_*.md'):
        if md_file.stat().st_mtime < cutoff.timestamp():
            size_mb = md_file.stat().st_size / (1024 * 1024)
            removed.append((str(md_file), size_mb))
            if not dry_run:
                md_file.unlink()
    
    return removed

def main():
    parser = argparse.ArgumentParser(description='OpenClaw Workspace Cleanup')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际删除')
    parser.add_argument('--execute', action='store_true', help='执行清理')
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("请使用 --dry-run 预览或 --execute 执行")
        return
    
    dry_run = args.dry_run
    mode = "[DRY RUN]" if dry_run else "[EXECUTE]"
    
    print("=" * 70)
    print(f"OpenClaw Workspace Cleanup {mode}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作区：{WORKSPACE}")
    print("=" * 70)
    
    total_saved = 0
    
    # 1. 清理 subagent 日志（7 天前）
    print("\n[1] 清理 Subagent 运行日志 (>7 天)...")
    removed = cleanup_subagent_logs(days_old=7, dry_run=dry_run)
    for path, size in removed:
        print(f"    {Path(path).name} ({size:.2f} MB)")
        total_saved += size
    print(f"    小计：{total_saved:.2f} MB")
    
    # 2. 清理桌面旧 CSV（30 天前，保留主表）
    print("\n[2] 清理桌面旧 CSV 文件 (>30 天，保留主表)...")
    removed = cleanup_old_csv_files(DESKTOP_REAL_POSTS, days_old=30, dry_run=dry_run)
    for path, size in removed:
        print(f"    {Path(path).name} ({size:.2f} MB)")
        total_saved += size
    print(f"    小计：{total_saved:.2f} MB")
    
    # 3. 清理测试脚本
    print("\n[3] 清理测试脚本...")
    removed = cleanup_test_scripts(WORKSPACE / "scripts", dry_run=dry_run)
    for path, size in removed:
        print(f"    {Path(path).name} ({size:.2f} MB)")
        total_saved += size
    print(f"    小计：{total_saved:.2f} MB")
    
    # 4. 清理旧内存日志
    print("\n[4] 清理旧内存日志 (>30 天)...")
    removed = cleanup_old_memory_logs(WORKSPACE / "memory", days_old=30, dry_run=dry_run)
    for path, size in removed:
        print(f"    {Path(path).name} ({size:.2f} MB)")
        total_saved += size
    print(f"    小计：{total_saved:.2f} MB")
    
    print("\n" + "=" * 70)
    print(f"预计释放空间：{total_saved:.2f} MB")
    if dry_run:
        print("\n预览模式 - 未执行任何删除")
        print("确认无误后运行：python scripts/cleanup_workspace.py --execute")
    else:
        print(f"\n清理完成！实际释放：{total_saved:.2f} MB")
    print("=" * 70)

if __name__ == "__main__":
    main()
