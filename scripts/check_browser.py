#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器检查脚本 - CDP 协议版
检查 Edge 浏览器连接状态和 LinkedIn 页面

用法：
  python scripts/check_browser.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from cdp_client import CDPClient

def main():
    print("=" * 60)
    print("浏览器检查 - CDP 协议版")
    print("=" * 60)
    
    client = CDPClient(port=9222)
    
    # 检查浏览器连接
    tabs = client.get_browser_tabs()
    if not tabs:
        print("[ERROR] 无法连接到浏览器")
        print("请确保 Edge 已启动并添加参数：--remote-debugging-port=9222")
        return
    
    print(f"[OK] 浏览器已连接")
    print(f"标签页数量：{len(tabs)}")
    
    linkedin_pages = []
    
    print("\n标签页列表:")
    for i, tab in enumerate(tabs):
        title = tab.get('title', 'N/A')[:60]
        url = tab.get('url', 'N/A')[:80]
        print(f"  {i+1}. {title}")
        print(f"     {url}")
        
        if 'linkedin.com' in url and 'sign-in' not in url:
            linkedin_pages.append(tab)
            print(f"     ✅ LinkedIn 页面！")
    
    if linkedin_pages:
        print(f"\n✅ 找到 {len(linkedin_pages)} 个 LinkedIn 页面")
        print("\n可以运行采集脚本：")
        print("  python scripts/linkedin_v9_cdp.py --duration 30")
    else:
        print(f"\n⚠️ 未找到已登录的 LinkedIn 页面")
        print("\n建议操作：")
        print("1. 在 Edge 中访问：https://www.linkedin.com/feed")
        print("2. 登录账号")
        print("3. 重新运行此检查脚本")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] 检查失败：{e}")
        import traceback
        traceback.print_exc()
