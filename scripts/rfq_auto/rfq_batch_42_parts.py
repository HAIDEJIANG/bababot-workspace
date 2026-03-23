#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFQ20260318-01 批量处理脚本 - 42 个零件
Condition 映射：全新件=NE/NS/FN, 可用件=SV/OH/AR
"""

import subprocess
import time
import sys
from datetime import datetime

# 修复 Windows 控制台编码问题
sys.stdout.reconfigure(encoding='utf-8')

# 42 个零件清单 (从 RFQ20260318-01 提取)
PARTS = [
    # 序号, PN, Qty, Condition 类型 (NEW=全新件, SVC=可用件)
    ("S1820612-02", "1", "NEW"),
    ("X-A1B", "1", "NEW"),
    ("9BG407572-70", "1", "NEW"),
    ("2LA006823-70", "1", "SVC"),
    ("091595-01", "1", "NEW"),
    ("091595-02", "1", "NEW"),
    ("00712226-0002", "5", "NEW"),
    ("00712226-0001", "1", "NEW"),
    ("30090331-0502", "1", "NEW"),
    ("30060173-0502", "1", "NEW"),
    ("066-50007-0111", "1", "SVC"),
    ("7600091", "1", "NEW"),
    ("7500060", "1", "NEW"),
    ("7601408", "1", "NEW"),
    ("7500598-001", "1", "NEW"),
    ("7700619", "1", "NEW"),
    ("7600987", "1", "NEW"),
    ("7550053", "1", "NEW"),
    ("549-1548-01", "12", "NEW"),
    ("9DX404700-01", "5", "NEW"),
    ("TCF53WF-150KK-500V", "10", "NEW"),
    ("00712238-0003", "10", "NEW"),
    ("00712175-0002", "10", "NEW"),
    ("01716061-0001", "5", "NEW"),
    ("837-2005-010", "10", "NEW"),
    ("837-2005-020", "10", "NEW"),
    ("9BG404994-00", "5", "NEW"),
    ("9EL404660-00", "5", "NEW"),
    ("SL211-06-1", "30", "NEW"),
    ("NAS602-7P", "30", "NEW"),
    ("E43134-1", "1", "NEW"),
    ("10173-0401-0201", "1", "NEW"),
    ("10173-0202", "1", "SVC"),
    ("367-027-006", "1", "SVC"),
    ("546-667-006", "1", "NEW"),
    ("800-631-8083", "2", "NEW"),
    ("2117342-19", "1", "SVC"),
    ("2117342-20", "1", "SVC"),
    ("62608", "20", "NEW"),
    ("2108616-4", "1", "NEW"),
    ("2J1665", "1", "NEW"),
    ("XLR4-31", "1", "NEW"),
]

def run_rfq(pn, qty, cond_type):
    """运行单个零件的 RFQ 提交"""
    # Condition 参数：NEW 不指定（自动选 NE/NS/FN），SVC 指定可用件
    if cond_type == "NEW":
        cmd = ["python", "scripts/rfq_auto/runner.py", "--pn", pn, "--qty", qty]
    else:
        # SVC 可用件：让脚本自动选择 SV/OH/AR
        cmd = ["python", "scripts/rfq_auto/runner.py", "--pn", pn, "--qty", qty]
    
    print(f"\n{'='*60}")
    print(f"[{pn}] Qty={qty}, Condition={cond_type}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {pn} 完成")
            return True
        else:
            print(f"❌ {pn} 失败：{result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {pn} 超时")
        return False
    except Exception as e:
        print(f"❌ {pn} 错误：{e}")
        return False

def main():
    print(f"🚀 RFQ20260318-01 批量处理开始")
    print(f"📦 总零件数：{len(PARTS)}")
    print(f"⏰ 开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for i, (pn, qty, cond_type) in enumerate(PARTS, 1):
        print(f"\n[{i}/{len(PARTS)}] 处理 {pn}...")
        success = run_rfq(pn, qty, cond_type)
        results.append({
            "index": i,
            "pn": pn,
            "qty": qty,
            "condition": cond_type,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
        # 每个零件之间等待 5 秒
        if i < len(PARTS):
            print(f"⏳ 等待 5 秒...")
            time.sleep(5)
    
    # 汇总报告
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    
    print(f"\n{'='*60}")
    print(f"📊 汇总报告")
    print(f"{'='*60}")
    print(f"总零件数：{len(PARTS)}")
    print(f"✅ 成功：{success_count}")
    print(f"❌ 失败：{fail_count}")
    print(f"⏰ 结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 保存报告
    report_path = "outputs/rfq20260318_01_report.json"
    import json
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "rfq_id": "RFQ20260318-01",
            "total_parts": len(PARTS),
            "success": success_count,
            "failed": fail_count,
            "start_time": results[0]["timestamp"] if results else None,
            "end_time": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📄 报告已保存：{report_path}")

if __name__ == "__main__":
    main()
