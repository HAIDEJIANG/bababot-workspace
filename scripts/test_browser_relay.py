#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser Relay 连接测试 - CDP 协议版
测试 OpenClaw Browser Relay Gateway 连接

用法：
  python scripts/test_browser_relay.py
"""

import sys
import io
import websocket
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Browser Relay Gateway 配置
GATEWAY_WS_URL = "ws://127.0.0.1:18792"
AUTH_TOKEN = "f2139bc84b38325ade4ed7a3cc3f5006f36bbddf"

def test_relay_connection():
    print("=" * 60)
    print("Browser Relay 连接测试")
    print("=" * 60)
    print(f"Gateway: {GATEWAY_WS_URL}")
    print(f"Token: {AUTH_TOKEN[:20]}...")
    
    try:
        # 首先尝试 HTTP 接口获取标签页列表
        import requests
        
        print("\n尝试 HTTP 接口...")
        response = requests.get(
            f"http://127.0.0.1:18792/json",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=5
        )
        
        if response.status_code == 200:
            tabs = response.json()
            print(f"✅ HTTP 连接成功")
            print(f"找到 {len(tabs)} 个标签页")
            
            for i, tab in enumerate(tabs[:10]):
                title = tab.get('title', 'N/A')[:60]
                url = tab.get('url', 'N/A')[:80]
                print(f"  [{i}] {title}")
                print(f"      {url}")
                if 'linkedin.com' in url:
                    print(f"      ✅ LinkedIn 页面！")
            
            return True
        else:
            print(f"❌ HTTP 失败：{response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Gateway")
        print("\n请检查：")
        print("1. Browser Relay 扩展是否已安装")
        print("2. Gateway 是否已启动（端口 18792）")
        print("3. Token 是否正确配置")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == "__main__":
    try:
        success = test_relay_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
