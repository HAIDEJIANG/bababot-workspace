#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge 浏览器启动脚本 - 带远程调试端口
用于 LinkedIn 采集（CDP 协议）

用法：
  python start_edge_for_linkedin.py
"""

import subprocess
import sys
import time
from pathlib import Path

# Edge 配置
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DEBUG_PORT = 9222
USER_DATA_DIR = r"C:\Users\Haide\AppData\Local\Microsoft\Edge\User Data\OpenClawProfile"

def check_edge_running():
    """检查 Edge 是否已在运行"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq msedge.exe", "/FO", "CSV"],
            capture_output=True, text=True
        )
        return "msedge.exe" in result.stdout
    except:
        return False

def start_edge():
    """启动 Edge 浏览器"""
    print("=" * 60)
    print("Edge 浏览器启动 - LinkedIn 采集准备")
    print("=" * 60)
    
    # 检查是否已运行
    if check_edge_running():
        print("⚠️  Edge 已在运行")
        print(f"   请确保已添加启动参数：--remote-debugging-port={DEBUG_PORT}")
        print("\n建议：关闭所有 Edge 窗口后重新运行此脚本")
        return False
    
    # 创建用户数据目录
    Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)
    print(f"✅ 用户数据目录：{USER_DATA_DIR}")
    
    # 启动命令
    args = [
        EDGE_PATH,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--disable-blink-features=AutomationControlled",
        "--disable-features=TranslateUI",
        "--disable-features=PrivacySandboxSettings4",
    ]
    
    print(f"\n🚀 启动 Edge...")
    print(f"   调试端口：{DEBUG_PORT}")
    
    try:
        subprocess.Popen(args)
        time.sleep(2)
        
        print("\n✅ Edge 已启动")
        print("\n下一步操作：")
        print("1. 在 Edge 中访问：https://www.linkedin.com/feed")
        print("2. 登录 LinkedIn 账号")
        print("3. 运行采集脚本：")
        print("   python scripts/linkedin_v9_cdp.py --duration 30")
        
        return True
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        return False

if __name__ == "__main__":
    success = start_edge()
    sys.exit(0 if success else 1)
