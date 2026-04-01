#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 登录检查脚本 - CDP 协议版

用法：
  python scripts/linkedin_login_check.py
"""

import sys
import io
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from cdp_client import CDPClient

def check_login():
    print("=" * 60)
    print("LinkedIn 登录状态检查")
    print("=" * 60)
    
    client = CDPClient(port=9222)
    
    # 查找 LinkedIn Feed 页面
    linkedin_tab = client.find_linkedin_feed()
    
    if not linkedin_tab:
        print("\n❌ 未找到已登录的 LinkedIn Feed 页面")
        print("\n请执行以下步骤：")
        print("1. 启动 Edge 带远程调试端口：")
        print("   python scripts/start_edge_for_linkedin.py")
        print("2. 在 Edge 中访问：https://www.linkedin.com/feed")
        print("3. 登录 LinkedIn 账号")
        print("4. 重新运行此检查脚本")
        return False
    
    print(f"\n✅ 找到 LinkedIn 页面")
    print(f"   标题：{linkedin_tab.get('title', 'N/A')}")
    print(f"   URL: {linkedin_tab.get('url', 'N/A')[:100]}")
    
    # 连接并检查登录状态
    ws_url = linkedin_tab.get('webSocketDebuggerUrl')
    if not client.connect(ws_url):
        print("❌ 无法连接到页面")
        return False
    
    # 检查是否包含登录相关关键词
    content = client.get_page_content()
    
    if "Sign in" in content or "登录" in content or "sign-in" in linkedin_tab.get('url', '').lower():
        print("\n⚠️ 检测到未登录状态")
        print("请在浏览器中手动登录 LinkedIn")
        print("\n等待 60 秒...")
        for i in range(60, 0, -10):
            print(f"  剩余 {i} 秒...")
            time.sleep(10)
        
        # 重新检查
        linkedin_tab = client.find_linkedin_feed()
        if not linkedin_tab or "sign-in" in linkedin_tab.get('url', '').lower():
            print("\n❌ 仍未登录，退出")
            client.disconnect()
            return False
    
    print("\n✅ 登录状态正常")
    print("\n可以运行采集脚本：")
    print("  python scripts/linkedin_v9_cdp.py --duration 30")
    
    client.disconnect()
    return True

if __name__ == "__main__":
    try:
        success = check_login()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 检查失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
