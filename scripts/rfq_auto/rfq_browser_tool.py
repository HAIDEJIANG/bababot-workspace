#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFQ20260318-01 使用 OpenClaw Browser Tool 自动化
直接使用已打开的浏览器，不启动新的 Playwright 实例
"""

import json
import time
import requests
import sys
from datetime import datetime
from pathlib import Path

# 修复编码问题
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# OpenClaw Browser API
BROWSER_API = "http://127.0.0.1:18800"

# 42 个零件清单 (前 10 个测试)
PARTS = [
    ("S1820612-02", "1", "NE"),
    ("X-A1B", "1", "NE"),
    ("9BG407572-70", "1", "NE"),
    ("2LA006823-70", "1", "SV"),
    ("091595-01", "1", "NE"),
    ("091595-02", "1", "NE"),
    ("00712226-0002", "5", "NE"),
    ("00712226-0001", "1", "NE"),
    ("30090331-0502", "1", "NE"),
    ("30060173-0502", "1", "NE"),
]

def log_event(event_type, data):
    """记录事件到 JSONL"""
    log_file = OUTPUT_DIR / f"rfq_browser_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    entry = {
        "ts": datetime.now().isoformat(),
        "event": event_type,
        **data
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_file

def get_tabs():
    """获取所有标签页"""
    try:
        resp = requests.get(f"{BROWSER_API}/json/list", timeout=10)
        return resp.json()
    except Exception as e:
        print(f"[ERROR] 获取标签页失败: {e}")
        return []

def get_page_html(target_id):
    """获取页面 HTML"""
    try:
        # 使用 CDP 获取页面内容
        ws_url = f"ws://127.0.0.1:18800/devtools/page/{target_id}"
        # 这里需要 WebSocket 连接，简化起见直接返回成功
        return True
    except Exception as e:
        print(f"[ERROR] 获取页面失败: {e}")
        return False

def main():
    print("="*60)
    print("RFQ20260318-01 自动化 (Browser Tool)")
    print("="*60)
    
    # 获取当前标签页
    tabs = get_tabs()
    stockmarket_tabs = [t for t in tabs if "stockmarket.aero" in t.get("url", "")]
    
    if not stockmarket_tabs:
        print("[ERROR] 没有找到 stockmarket.aero 标签页")
        print("[INFO] 请先打开 stockmarket.aero 并登录")
        return
    
    target_id = stockmarket_tabs[0]["id"]
    print(f"[OK] 找到 stockmarket.aero 标签页: {target_id}")
    
    results = []
    
    for i, (pn, qty, cond) in enumerate(PARTS, 1):
        print(f"\n[{i}/{len(PARTS)}] 处理 {pn}...")
        print(f"[INFO] PN={pn}, Qty={qty}, Condition={cond}")
        
        # 记录结果
        results.append({
            "index": i,
            "pn": pn,
            "qty": qty,
            "condition": cond,
            "success": False,
            "message": "Manual step required",
            "timestamp": datetime.now().isoformat()
        })
        
        # 等待用户操作
        print(f"[WAIT] 请手动处理 {pn}...")
        time.sleep(5)
    
    # 保存报告
    report = {
        "rfq_id": "RFQ20260318-01",
        "total": len(PARTS),
        "success": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results,
        "note": "Browser Tool 方案 - 需要手动配合"
    }
    
    report_file = OUTPUT_DIR / "rfq20260318_01_browser_tool_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {len(PARTS)}")
    print(f"Report: {report_file}")

if __name__ == "__main__":
    main()