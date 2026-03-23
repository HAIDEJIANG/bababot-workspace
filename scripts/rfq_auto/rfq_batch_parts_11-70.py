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

# Parts 11-70 from the Excel file (60 parts total)
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
    "837-7009-010",      # 21
    "M39016-27-029L",    # 22
    "421D18A",           # 23
    "01716070-0001",     # 24
    "01716069-0001",     # 25
    "12051334-0002",     # 26
    "12051347-0002",     # 27
    "120-02487-0004",    # 28
    "316-7075-001",      # 29
    "12051267-0002",     # 30
    "2039162-0506",      # 31
    "30060195-0510",     # 32
    "201-0005-000",      # 33
    "330-1854-040",      # 34
    "343-0174-000",      # 35
    "355-0355-040",      # 36
    "435-0002-050",      # 37
    "827-3387-053",      # 38
    "827-3387-055",      # 39
    "827-3387-083",      # 40
    "827-3387-084",      # 41
    "827-3387-085",      # 42
    "827-3387-086",      # 43
    "829-0438-007",      # 44
    "S41",               # 45
    "S39-3",             # 46
    "S37-3",             # 47
    "230-0660-010",      # 48
    "042147-4",          # 49
    "622-4717-004",      # 50
    "4058650-904",       # 51
    "COL4C-0087-0003",   # 52
    "BCG27-U000-0730",   # 53
    "447611-1",          # 54
    "447615-1",          # 55
    "835-0045-020",      # 56
    "351-5470-010",      # 57
    "011-2657-001",      # 58
    "4001750-55",        # 59
    "372-2601-747",      # 60
    "755SUE2-4",         # 61
    "767584K",           # 62
    "312BS801-1",        # 63
    "E41498BA01",        # 64
    "C19755BA01",        # 65
    "328-303DP28V",      # 66
    "327-403D28V",       # 67
    "HI8444PSI10",       # 68
    "852-6005-010",      # 69
    "353-1994-000",      # 70
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
    print(f"[BATCH] Starting RFQ for {len(PART_NUMBERS)} parts (parts 11-70)")
    print(f"[INFO] Parts: {', '.join(PART_NUMBERS[:10])}... (total {len(PART_NUMBERS)})")
    
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
    summary_path = OUTPUT_DIR / "rfq_batch_parts_11-70.json"
    summary = {
        "batch": "parts_11-70",
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
    
    # Auto cleanup screenshots to save disk space
    print(f"\n[CLEANUP] Cleaning up screenshots to save disk space...")
    import shutil
    screenshots_dir = Path(__file__).resolve().parent / "outputs" / "screenshots"
    if screenshots_dir.exists():
        try:
            shutil.rmtree(screenshots_dir)
            print(f"[OK] Screenshots directory deleted: {screenshots_dir}")
        except Exception as e:
            print(f"[WARN] Failed to delete screenshots: {e}")
    else:
        print(f"[INFO] No screenshots directory to clean")
    
    print(f"{'='*60}")
    
    return summary

if __name__ == "__main__":
    run_batch()
