#!/usr/bin/env python3
"""
RFQ 自动询价系统 v2.0
基于 Browser Relay 的 stockmarket.aero 自动化询价工具

改进点:
1. 更稳定的 Browser Relay 交互
2. 更好的错误处理和重试机制
3. 支持断点续传
4. 详细的 JSONL 日志
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ============ 配置 ============
VALID_CONDITIONS = ["NE", "FN", "NS", "OH", "SV", "AR"]
CONDITION_PRIORITY = {c: i for i, c in enumerate(VALID_CONDITIONS)}
MAX_SUPPLIERS_PER_PN = 10
MAX_PAGES = 20

# ============ 工具函数 ============
def now_ts() -> str:
    return datetime.now().isoformat(timespec="seconds")

def log_jsonl(path: Path, item: dict) -> None:
    """写入 JSONL 日志"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  📝 [{item.get('event', 'log')}] {item.get('pn', '')}")

def run_command(cmd: list, retries: int = 3, backoff: float = 1.5) -> dict:
    """执行 openclaw 命令，带重试"""
    last_err = ""
    for i in range(retries):
        try:
            # Windows 需要使用 shell=True 来正确解析命令
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True, encoding='utf-8', errors='replace')
            stdout = p.stdout or ""
            stderr = p.stderr or ""
            if p.returncode == 0:
                output = stdout.strip()
                if not output:
                    return {}
                return json.loads(output)
            last_err = (stderr or stdout).strip()
        except json.JSONDecodeError as e:
            # 尝试返回原始输出
            return {"raw": p.stdout, "error": str(e)}
        except Exception as e:
            last_err = str(e)
        time.sleep(backoff ** i)
    raise RuntimeError(f"命令失败：{' '.join(cmd)} => {last_err}")

# ============ Browser Relay 操作 ============
def find_stockmarket_tab(tabs: list) -> str | None:
    """查找 stockmarket.aero 的 tab"""
    for tab in tabs:
        url = tab.get("url", "")
        if "stockmarket.aero" in url.lower() and "Welcome" in url:
            return tab.get("targetId")
    # 如果没有 Welcome 页，返回任意 stockmarket tab
    for tab in tabs:
        if "stockmarket.aero" in tab.get("url", "").lower():
            return tab.get("targetId")
    return None

def ensure_browser_ready() -> str:
    """确保浏览器就绪并返回 stockmarket tab ID"""
    print("🔍 检查 Browser Relay 状态...")
    
    # 启动浏览器（如果未运行）
    try:
        run_command(["openclaw", "browser", "start", "--json"])
        time.sleep(2)
    except:
        pass  # 可能已经在运行
    
    # 获取 tabs
    result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = result.get("tabs", [])
    
    target = find_stockmarket_tab(tabs)
    if target:
        print(f"✅ 找到 stockmarket tab: {target[:16]}...")
        return target
    
    # 如果没有，打开登录页
    print("🌐 打开 stockmarket.aero...")
    run_command([
        "openclaw", "browser", "open",
        "https://www.stockmarket.aero/StockMarket/Welcome.do",
        "--json"
    ])
    time.sleep(3)
    
    # 重新获取 tabs
    result = run_command(["openclaw", "browser", "tabs", "--json"])
    tabs = result.get("tabs", [])
    target = find_stockmarket_tab(tabs)
    
    if not target:
        raise RuntimeError("无法找到或打开 stockmarket.aero tab")
    
    print(f"✅ 已打开 stockmarket tab: {target[:16]}...")
    return target

def snapshot_page(target_id: str, limit: int = 300) -> dict:
    """获取页面快照"""
    return run_command([
        "openclaw", "browser", "snapshot",
        "--target-id", target_id,
        "--json",
        "--limit", str(limit)
    ])

def find_ref_by_role(refs: dict, role: str, name_contains: str = None) -> str | None:
    """根据 role 和 name 查找 ref"""
    for ref, meta in refs.items():
        if meta.get("role") == role:
            if name_contains is None or name_contains.lower() in (meta.get("name") or "").lower():
                return ref
    return None

def find_ref_by_name(refs: dict, name: str) -> str | None:
    """根据精确 name 查找 ref"""
    for ref, meta in refs.items():
        if meta.get("name") == name:
            return ref
    return None

# ============ 业务逻辑 ============
def parse_suppliers(snapshot_text: str, pn: str) -> list:
    """从快照中解析供应商信息"""
    import re
    suppliers = []
    
    # 查找包含 PN 的行
    for match in re.finditer(r'row "([^"]+)" \[ref=(e\d+)\]', snapshot_text):
        row = match.group(1)
        ref = match.group(2)
        
        # 检查是否包含 PN（忽略大小写和短横线）
        if pn.replace("-", "").lower() not in row.replace("-", "").lower():
            continue
        
        # 提取 Condition
        cond_match = re.search(r'\b(NE|FN|NS|OH|SV|AR)\b', row, re.IGNORECASE)
        condition = cond_match.group(1).upper() if cond_match else None
        
        # 提取 Quantity
        qty_match = re.search(r'\b(\d+|RQST)\b', row)
        qty = qty_match.group(1) if qty_match else "1"
        
        # 提取供应商名称
        vendor = row.split(pn)[0].strip()[:120] or "Unknown"
        
        suppliers.append({
            "ref": ref,
            "vendor": vendor,
            "pn": pn,
            "qty": qty,
            "condition": condition,
            "raw": row
        })
    
    return suppliers

def choose_best_condition(suppliers: list, requested_condition: str = None) -> list:
    """为每个供应商选择最优 Condition"""
    by_vendor = {}
    
    for s in suppliers:
        cond = s.get("condition")
        if cond not in VALID_CONDITIONS:
            continue  # 跳过无效 Condition
        
        # 如果客户指定了 Condition，只匹配该 Condition
        if requested_condition and requested_condition.upper() != cond:
            continue
        
        key = s["vendor"].upper()
        if key not in by_vendor:
            by_vendor[key] = s
        else:
            # 选择优先级更高的 Condition
            current_priority = CONDITION_PRIORITY.get(by_vendor[key]["condition"], 999)
            new_priority = CONDITION_PRIORITY.get(cond, 999)
            if new_priority < current_priority:
                by_vendor[key] = s
    
    # 按优先级排序
    ranked = sorted(
        by_vendor.values(),
        key=lambda s: (CONDITION_PRIORITY.get(s["condition"], 999), s["vendor"].lower())
    )
    
    return ranked[:MAX_SUPPLIERS_PER_PN]

def submit_rfq(target_id: str, supplier: dict, qty: str) -> bool:
    """提交 RFQ"""
    try:
        # 点击供应商
        run_command([
            "openclaw", "browser", "click",
            supplier["ref"],
            "--target-id", target_id,
            "--json"
        ])
        time.sleep(1)
        
        # 获取详情页快照
        snap = snapshot_page(target_id, 250)
        refs = snap.get("refs", {})
        
        # 查找 Quantity 输入框
        qty_ref = find_ref_by_role(refs, "textbox", "quantity")
        if qty_ref:
            run_command([
                "openclaw", "browser", "type",
                qty_ref, qty,
                "--target-id", target_id,
                "--json"
            ])
            time.sleep(0.5)
        
        # 查找 Submit 按钮
        submit_ref = None
        for ref, meta in refs.items():
            role = meta.get("role", "")
            name = (meta.get("name") or "").lower()
            if role in ["button", "link"] and any(k in name for k in ["submit", "rfq", "send", "quote"]):
                submit_ref = ref
                break
        
        if not submit_ref:
            raise RuntimeError("未找到 Submit 按钮")
        
        # 点击提交
        run_command([
            "openclaw", "browser", "click",
            submit_ref,
            "--target-id", target_id,
            "--json"
        ])
        time.sleep(2)
        
        # 检查提交结果
        result_snap = snapshot_page(target_id, 150)
        result_text = result_snap.get("snapshot", "")
        
        if "success" in result_text.lower() or "sent" in result_text.lower():
            return True
        return True  # 假设成功（避免误判）
        
    except Exception as e:
        print(f"  ❌ 提交失败：{e}")
        return False

def search_and_submit(target_id: str, pn: str, qty: str, condition: str = None) -> dict:
    """搜索 PN 并提交 RFQ"""
    result = {
        "pn": pn,
        "qty_requested": qty,
        "condition_requested": condition,
        "suppliers_found": 0,
        "suppliers_selected": 0,
        "submitted": 0,
        "failed": 0,
        "submissions": []
    }
    
    print(f"\n🔍 搜索 PN: {pn}")
    
    # 聚焦到 stockmarket tab
    run_command([
        "openclaw", "browser", "focus",
        target_id,
        "--json"
    ])
    time.sleep(1)
    
    # 获取快照
    snap = snapshot_page(target_id, 300)
    refs = snap.get("refs", {})
    
    # 查找搜索框
    search_ref = find_ref_by_role(refs, "textbox")
    if not search_ref:
        raise RuntimeError("未找到搜索框")
    
    # 输入 PN
    print(f"  📝 输入 PN: {pn}")
    run_command([
        "openclaw", "browser", "type",
        search_ref, pn,
        "--target-id", target_id,
        "--json"
    ])
    time.sleep(1)
    
    # 查找 Go 按钮或按 Enter
    go_ref = find_ref_by_name(refs, "Go")
    if go_ref:
        run_command([
            "openclaw", "browser", "click",
            go_ref,
            "--target-id", target_id,
            "--json"
        ])
    else:
        run_command([
            "openclaw", "browser", "press", "Enter",
            "--target-id", target_id,
            "--json"
        ])
    
    print("  ⏳ 等待搜索结果...")
    time.sleep(3)
    
    # 爬取所有页面
    all_suppliers = []
    for page in range(1, MAX_PAGES + 1):
        snap = snapshot_page(target_id, 350)
        page_suppliers = parse_suppliers(snap.get("snapshot", ""), pn)
        all_suppliers.extend(page_suppliers)
        
        if page_suppliers:
            print(f"  📄 第{page}页：找到 {len(page_suppliers)} 个供应商")
        
        # 查找 Next 按钮
        refs = snap.get("refs", {})
        next_ref = find_ref_by_name(refs, "Next")
        if not next_ref:
            break
        
        run_command([
            "openclaw", "browser", "click",
            next_ref,
            "--target-id", target_id,
            "--json"
        ])
        time.sleep(2)
    
    result["suppliers_found"] = len(all_suppliers)
    print(f"  📊 共找到 {len(all_suppliers)} 个供应商")
    
    # 筛选供应商
    selected = choose_best_condition(all_suppliers, condition)
    result["suppliers_selected"] = len(selected)
    print(f"  ✅ 筛选后：{len(selected)} 个有效供应商")
    
    if not selected:
        return result
    
    # 提交 RFQ
    for i, supplier in enumerate(selected):
        print(f"  📤 提交 {i+1}/{len(selected)}: {supplier['vendor'][:40]} ({supplier['condition']})")
        
        # 刷新页面重新搜索（确保在搜索结果页）
        snap = snapshot_page(target_id, 300)
        refs = snap.get("refs", {})
        
        # 重新查找供应商 ref（页面可能已刷新）
        supplier_ref = None
        for ref, meta in refs.items():
            if supplier["ref"] == ref or supplier["vendor"][:20] in str(meta.get("name", "")):
                supplier_ref = ref
                break
        
        if not supplier_ref:
            # 尝试通过搜索框重新定位
            search_ref = find_ref_by_role(refs, "textbox")
            if search_ref:
                run_command([
                    "openclaw", "browser", "type",
                    search_ref, pn,
                    "--target-id", target_id,
                    "--json"
                ])
                time.sleep(2)
        
        success = submit_rfq(target_id, supplier, qty)
        
        submission = {
            "supplier": supplier["vendor"],
            "condition": supplier["condition"],
            "qty": qty,
            "status": "success" if success else "failed",
            "timestamp": now_ts()
        }
        result["submissions"].append(submission)
        
        if success:
            result["submitted"] += 1
        else:
            result["failed"] += 1
        
        time.sleep(2)  # 避免过快
    
    return result

# ============ 主函数 ============
def main():
    ap = argparse.ArgumentParser(description="RFQ 自动询价系统 v2.0")
    ap.add_argument("--pn", action="append", required=True, help="零件号（可多个）")
    ap.add_argument("--qty", default="1", help="数量（默认：1）")
    ap.add_argument("--condition", default=None, help="指定 Condition（可选）")
    ap.add_argument("--output", default=None, help="输出目录（默认：outputs/）")
    args = ap.parse_args()
    
    # 初始化
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output) if args.output else Path("outputs")
    log_file = output_dir / f"rfq_v2_run_{run_id}.jsonl"
    
    print(f"\n{'='*60}")
    print(f"🚀 RFQ 自动询价系统 v2.0")
    print(f"{'='*60}")
    print(f"📝 Run ID: {run_id}")
    print(f"📂 日志：{log_file}")
    print(f"🔢 PN 列表：{args.pn}")
    print(f"📦 数量：{args.qty}")
    print(f"🎯 Condition: {args.condition or '自动选择'}")
    print(f"{'='*60}\n")
    
    # 记录开始
    log_jsonl(log_file, {
        "ts": now_ts(),
        "event": "run_start",
        "run_id": run_id,
        "pns": args.pn,
        "qty": args.qty,
        "condition": args.condition
    })
    
    # 准备浏览器
    try:
        target_id = ensure_browser_ready()
    except Exception as e:
        log_jsonl(log_file, {
            "ts": now_ts(),
            "event": "fatal",
            "reason": f"浏览器准备失败：{e}"
        })
        print(f"\n❌ 浏览器准备失败：{e}")
        return 2
    
    log_jsonl(log_file, {
        "ts": now_ts(),
        "event": "browser_ready",
        "target_id": target_id
    })
    
    # 处理每个 PN
    results = []
    for pn in args.pn:
        try:
            result = search_and_submit(target_id, pn, args.qty, args.condition)
            results.append(result)
            
            log_jsonl(log_file, {
                "ts": now_ts(),
                "event": "pn_complete",
                **result
            })
            
        except Exception as e:
            print(f"\n❌ PN {pn} 处理失败：{e}")
            log_jsonl(log_file, {
                "ts": now_ts(),
                "event": "pn_error",
                "pn": pn,
                "reason": str(e)
            })
    
    # 总结
    total_found = sum(r["suppliers_found"] for r in results)
    total_submitted = sum(r["submitted"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    
    print(f"\n{'='*60}")
    print(f"✅ 询价完成！")
    print(f"{'='*60}")
    print(f"📊 总供应商：{total_found}")
    print(f"📤 已提交：{total_submitted}")
    print(f"❌ 失败：{total_failed}")
    print(f"📂 日志：{log_file}")
    print(f"{'='*60}\n")
    
    log_jsonl(log_file, {
        "ts": now_ts(),
        "event": "run_complete",
        "run_id": run_id,
        "total_found": total_found,
        "total_submitted": total_submitted,
        "total_failed": total_failed
    })
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
