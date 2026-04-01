#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 调试脚本 - CDP 协议版
分析页面结构，查找帖子容器的类名

用法：
  python scripts/debug_linkedin.py
"""

import sys
import io
import time
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from cdp_client import CDPClient

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 60)
    log("LinkedIn 页面结构调试")
    log("=" * 60)
    
    client = CDPClient(port=9222)
    
    # 查找 LinkedIn Feed 页面
    linkedin_tab = client.find_linkedin_feed()
    if not linkedin_tab:
        log("❌ 未找到 LinkedIn Feed 页面")
        return
    
    log(f"✅ 找到页面：{linkedin_tab.get('title', 'N/A')}")
    
    # 连接
    ws_url = linkedin_tab.get('webSocketDebuggerUrl')
    if not client.connect(ws_url):
        log("❌ 连接失败")
        return
    
    # 分析页面结构
    log("\n分析页面结构...")
    
    # 获取所有相关类名
    js_code = """
    () => {
        var all = document.querySelectorAll('*');
        var classMap = {};
        for(var i=0; i<all.length; i++) {
            var cn = all[i].className;
            if(cn && typeof cn === 'string' && cn.length > 0) {
                if(cn.indexOf('feed') >= 0 || cn.indexOf('update') >= 0 || cn.indexOf('post') >= 0 || cn.indexOf('activity') >= 0) {
                    classMap[cn] = (classMap[cn] || 0) + 1;
                }
            }
        }
        return classMap;
    }
    """
    
    result = client.evaluate(js_code)
    classes = result.get('result', {}).get('value', {})
    
    log("\n找到相关类名 (前 20 个):")
    for cn, count in list(classes.items())[:20]:
        log(f"  {cn}: {count}个")
    
    # 查找包含"Feed post"文本的元素
    log("\n查找 Feed 帖子元素...")
    # 这个需要更复杂的 JS，暂时简化
    
    log("\n✅ 分析完成")
    log("\n提示：可以使用以下选择器测试采集：")
    log("  article")
    log("  div[role='article']")
    log("  div.update-v2")
    
    client.disconnect()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
