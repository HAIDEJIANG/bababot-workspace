#!/usr/bin/env python3
"""
RFQ batch processing for parts 11-70 from inquiry list RFQ20260305-01
"""

from pathlib import Path
import json
import sys
import time
import importlib.util

BASE_DIR = Path(__file__).resolve().parent
VERIFY_PATH = BASE_DIR / "rfq_verify.py"

# Parts 11-20 from the Excel file
PART_NUMBERS = [
    "046-69-999-0931",  # 11
    "AC931621A",         # 12
    "LA5P0P0TENT0000",   # 13
    "T330D336K035AS",    # 14
    "65-52807-73",       # 15
    "24605038",          # 16
    "AM79C961AVI",       # 17
    "410-0346-050",      # 18
    "100603-04-01",      # 19
    "MS90451-7152",      # 20
]

QUANTITY = "1"
OUTPUT_DIR = BASE_DIR / "outputs"

def load_verify_module():
    spec = importlib.util.spec_from_file_location("rfq_verify", VERIFY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier module from {VERIFY_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_batch():
    print(f"[BATCH] Starting RFQ for {len(PART_NUMBERS)} parts (parts 11-20)")
    print(f"[INFO] Parts: {', '.join(PART_NUMBERS)}")
    
    module = load_verify_module()
    results = []
    
    for i, pn in enumerate(PART_NUMBERS, 11):
        print(f"\n{'='*60}")
        print(f"[{i}/70] Processing {pn}")
        print(f"{'='*60}")
        
        # Update module variables
        module.PART_NUMBER = pn
        module.QUANTITY = QUANTITY
        
        try:
            success = module.run_with_verification()
            result = {
                "part_number": pn,
                "quantity": QUANTITY,
                "success": success,
                "index": i,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"[ERROR] {pn}: {e}")
            result = {
                "part_number": pn,
                "quantity": QUANTITY,
                "success": False,
                "index": i,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        results.append(result)
        
        # Brief pause between parts
        if i < len(PART_NUMBERS) + 10:
            print(f"\n[INFO] Waiting 5 seconds before next part...")
            time.sleep(5)
    
    # Save batch summary
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUTPUT_DIR / "rfq_batch_parts_11-20.json"
    summary = {
        "batch": "parts_11-20",
        "total": len(PART_NUMBERS),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\n{'='*60}")
    print(f"[BATCH COMPLETE]")
    print(f"[INFO] Total: {len(PART_NUMBERS)}")
    print(f"[INFO] Successful: {summary['successful']}")
    print(f"[INFO] Failed: {summary['failed']}")
    print(f"[INFO] Summary saved to: {summary_path}")
    print(f"{'='*60}")
    
    return summary

if __name__ == "__main__":
    run_batch()
