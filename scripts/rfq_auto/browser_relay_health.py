from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class HealthResult:
    ok: bool
    browser_running: bool
    tabs: int
    stockmarket_tabs: int
    blocker: str = ""
    retry_commands: List[str] | None = None


OPENCLAW = "openclaw.cmd"


def _run_json(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip())
    return json.loads(p.stdout)


def check_browser_relay_health() -> HealthResult:
    retry = [
        "openclaw browser start --json",
        "openclaw browser tabs --json",
        "openclaw browser open https://www.stockmarket.aero/StockMarket/Welcome.do --json",
    ]
    try:
        status = _run_json([OPENCLAW, "browser", "status", "--json"])
    except Exception as e:
        return HealthResult(False, False, 0, 0, f"browser status失败: {e}", retry)

    running = bool(status.get("running") and status.get("cdpReady"))
    try:
        tabs_obj = _run_json([OPENCLAW, "browser", "tabs", "--json"])
        tabs = tabs_obj.get("tabs", [])
    except Exception as e:
        return HealthResult(False, running, 0, 0, f"browser tabs失败: {e}", retry)

    stock_tabs = [t for t in tabs if "stockmarket.aero" in (t.get("url", "").lower())]
    if not running:
        return HealthResult(False, False, len(tabs), len(stock_tabs), "Browser未运行", retry)
    if not tabs:
        return HealthResult(False, running, 0, 0, "无可用标签页（可能未Attach）", retry)

    return HealthResult(True, running, len(tabs), len(stock_tabs), "", retry)


if __name__ == "__main__":
    hr = check_browser_relay_health()
    print(json.dumps(asdict(hr), ensure_ascii=False, indent=2))
