#!/usr/bin/env python3
"""
RFQ batch entrypoint hardened to use strict verification flow.
Rule: success means RFQ history verified, not just UI clicked.
Rule: NEVER click Respond.
"""

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VERIFY_PATH = BASE_DIR / "rfq_verify.py"
OUTPUT_DIR = BASE_DIR / "outputs"


def load_verify_module():
    spec = importlib.util.spec_from_file_location("rfq_verify", VERIFY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier module from {VERIFY_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_rfq_automation(part_number: str, quantity: str = "1"):
    module = load_verify_module()

    # Reuse the strict verified flow.
    module.PART_NUMBER = part_number
    module.QUANTITY = quantity

    print(f"[INFO] Starting strict RFQ automation for part: {part_number}")
    print(f"[INFO] Target quantity: {quantity}")
    print("[INFO] Mode: strict verification via RFQ history")

    success = module.run_with_verification()

    result_path = OUTPUT_DIR / f"rfq_result_{part_number}.json"
    payload = {
        "part_number": part_number,
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "strict_history_required": True,
        "verifier_result_path": str(result_path),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUTPUT_DIR / f"rfq_part2_summary_{part_number}.json"
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[INFO] Summary saved to: {summary_path}")
    print(f"[INFO] Success: {success}")
    return payload


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="S1820612-02")
    ap.add_argument("--qty", default="1")
    args = ap.parse_args()
    run_rfq_automation(args.part, args.qty)
