from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from browser_relay_health import check_browser_relay_health
from state_store import RunState, StateStore
from supplier_filter import SupplierCandidate, filter_suppliers

OPENCLAW = "openclaw.cmd"


def now_ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def run_json_command(cmd: List[str], retries: int = 3, backoff: float = 1.5) -> dict:
    last_err = ""
    for i in range(retries):
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0:
            try:
                return json.loads(p.stdout)
            except Exception:
                return {"raw": p.stdout}
        last_err = (p.stderr or p.stdout).strip()
        time.sleep(backoff ** i)
    raise RuntimeError(f"command failed: {' '.join(cmd)} => {last_err}")


def log_jsonl(path: Path, item: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def find_stockmarket_tab(tabs: List[dict]) -> Optional[str]:
    for t in tabs:
        if "stockmarket.aero" in (t.get("url", "").lower()):
            return t.get("targetId")
    return None


def parse_suppliers(snapshot_text: str, pn: str, page: int) -> List[SupplierCandidate]:
    items: List[SupplierCandidate] = []
    for m in re.finditer(r'row "([^"]+)" \[ref=(e\d+)\]', snapshot_text):
        row = m.group(1)
        if pn.replace("-", "") not in row.replace("-", ""):
            continue
        cond_m = re.search(r"\b(NE|FN|NS|OH|SV|AR)\b", row)
        qty_m = re.search(r"\b(\d+|RQST)\b", row)
        cond = cond_m.group(1) if cond_m else None
        qty = qty_m.group(1) if qty_m else "1"
        vendor = row.split(pn)[0].strip()[:120] or "unknown-vendor"
        items.append(SupplierCandidate(vendor=vendor, pn=pn, qty=qty, condition=cond, source_page=page, raw=row))
    return items


def main() -> int:
    ap = argparse.ArgumentParser(description="RFQ auto runner")
    ap.add_argument("--pn", action="append", required=False)
    ap.add_argument("--condition", default=None)
    ap.add_argument("--qty", default="1")
    ap.add_argument("--max-pages", type=int, default=20)
    args = ap.parse_args()

    pns = args.pn or ["10037-0770"]
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_jsonl = Path(f"outputs/rfq_auto_run_{run_id}.jsonl")
    state_store = StateStore("outputs/rfq_auto_state.json")
    state = state_store.load(RunState(run_id=run_id, current_index=0, completed=False, meta={"pns": pns}))

    health = check_browser_relay_health()
    log_jsonl(out_jsonl, {"ts": now_ts(), "event": "health", **asdict(health)})

    try:
        run_json_command([OPENCLAW, "browser", "start", "--json"])
        tabs = run_json_command([OPENCLAW, "browser", "tabs", "--json"]).get("tabs", [])
        target = find_stockmarket_tab(tabs)
        if not target:
            run_json_command([OPENCLAW, "browser", "open", "https://www.stockmarket.aero/StockMarket/Welcome.do", "--json"])
            tabs = run_json_command([OPENCLAW, "browser", "tabs", "--json"]).get("tabs", [])
            target = find_stockmarket_tab(tabs)
    except Exception as e:
        log_jsonl(out_jsonl, {"ts": now_ts(), "event": "fatal", "reason": f"browser init failed: {e}"})
        print(str(out_jsonl))
        return 2

    if not target:
        log_jsonl(out_jsonl, {"ts": now_ts(), "event": "fatal", "reason": "no stockmarket tab", "retry": health.retry_commands})
        print(str(out_jsonl))
        return 2

    for idx in range(state.current_index, len(pns)):
        pn = pns[idx]
        state.current_index = idx
        state_store.save(state)
        log_jsonl(out_jsonl, {"ts": now_ts(), "event": "pn_start", "pn": pn, "qty": args.qty, "condition": args.condition})

        try:
            run_json_command([OPENCLAW, "browser", "focus", target, "--json"])
            snap = run_json_command([OPENCLAW, "browser", "snapshot", "--target-id", target, "--json", "--limit", "240"])
            refs = snap.get("refs", {})
            search_ref = None
            go_ref = None
            for ref, meta in refs.items():
                if meta.get("role") == "textbox" and not search_ref:
                    search_ref = ref
                if meta.get("name") == "Go" and meta.get("role") in ["textbox", "button", "link"]:
                    go_ref = ref
            if not search_ref:
                raise RuntimeError("search textbox not found")

            run_json_command([OPENCLAW, "browser", "type", search_ref, pn, "--target-id", target, "--json"])
            if go_ref:
                run_json_command([OPENCLAW, "browser", "click", go_ref, "--target-id", target, "--json"])
            else:
                run_json_command([OPENCLAW, "browser", "press", "Enter", "--target-id", target, "--json"])

            all_rows: List[SupplierCandidate] = []
            for page in range(1, args.max_pages + 1):
                snap = run_json_command([OPENCLAW, "browser", "snapshot", "--target-id", target, "--json", "--limit", "280"])
                page_rows = parse_suppliers(snap.get("snapshot", ""), pn, page)
                all_rows.extend(page_rows)
                log_jsonl(out_jsonl, {"ts": now_ts(), "event": "page_scan", "pn": pn, "page": page, "rows": len(page_rows)})

                next_ref = None
                for ref, meta in snap.get("refs", {}).items():
                    if meta.get("role") == "link" and meta.get("name") == "Next":
                        next_ref = ref
                        break
                if not next_ref:
                    break
                run_json_command([OPENCLAW, "browser", "click", next_ref, "--target-id", target, "--json"])

            selected = filter_suppliers(all_rows, pn=pn, requested_condition=args.condition, top_n=10)
            log_jsonl(out_jsonl, {"ts": now_ts(), "event": "supplier_selected", "pn": pn, "count": len(selected), "suppliers": [asdict(s) for s in selected]})

            submitted = 0
            failed = 0
            for s in selected:
                try:
                    snap = run_json_command([OPENCLAW, "browser", "snapshot", "--target-id", target, "--json", "--limit", "260"])
                    submit_ref = None
                    qty_ref = None
                    for ref, meta in snap.get("refs", {}).items():
                        name = (meta.get("name") or "").lower()
                        if meta.get("role") == "textbox" and not qty_ref:
                            qty_ref = ref
                        if meta.get("role") in ["button", "link"] and ("submit" in name or "rfq" in name or "send" in name):
                            submit_ref = ref
                    if qty_ref:
                        run_json_command([OPENCLAW, "browser", "type", qty_ref, args.qty or "1", "--target-id", target, "--json"])
                    if not submit_ref:
                        raise RuntimeError("submit button not found")
                    run_json_command([OPENCLAW, "browser", "click", submit_ref, "--target-id", target, "--json"])
                    submitted += 1
                    log_jsonl(out_jsonl, {"ts": now_ts(), "event": "submit_ok", "pn": pn, "vendor": s.vendor, "condition": s.condition, "qty": args.qty or "1"})
                except Exception as e:
                    failed += 1
                    log_jsonl(out_jsonl, {"ts": now_ts(), "event": "submit_fail", "pn": pn, "vendor": s.vendor, "reason": str(e)})

            if not selected:
                log_jsonl(out_jsonl, {"ts": now_ts(), "event": "pn_done", "pn": pn, "submitted": 0, "failed": 0, "reason": "no valid suppliers by condition rule"})
            else:
                log_jsonl(out_jsonl, {"ts": now_ts(), "event": "pn_done", "pn": pn, "submitted": submitted, "failed": failed, "reason": ""})

        except Exception as e:
            log_jsonl(out_jsonl, {
                "ts": now_ts(),
                "event": "pn_error",
                "pn": pn,
                "reason": str(e),
                "retry_commands": [
                    f"python scripts/rfq_auto/runner.py --pn {pn} --qty {args.qty}",
                    "openclaw browser start --json",
                    "openclaw browser tabs --json",
                ],
            })

    state.completed = True
    state_store.save(state)
    log_jsonl(out_jsonl, {"ts": now_ts(), "event": "run_done", "run_id": run_id, "completed": True})
    print(str(out_jsonl))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
