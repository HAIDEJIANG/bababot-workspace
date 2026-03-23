from pathlib import Path
import os
from playwright.sync_api import sync_playwright

EDGE_MAIN_USER_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "User Data"
WELCOME_URL = "https://www.stockmarket.aero/StockMarket/Welcome.do"

print(f"[TEST] Main Edge user data dir: {EDGE_MAIN_USER_DATA_DIR}")

with sync_playwright() as p:
    context = None
    try:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(EDGE_MAIN_USER_DATA_DIR),
            channel="msedge",
            headless=False,
            slow_mo=300,
            viewport={"width": 1280, "height": 1000},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(WELCOME_URL, wait_until="domcontentloaded", timeout=30000)
        content = page.content()
        if "Welcome," in content:
            print("[OK] Main Edge profile opened and login state appears present")
        else:
            print("[INFO] Main Edge profile opened, but login state not confirmed")
    except Exception as e:
        print(f"[FAIL] {e}")
    finally:
        if context:
            context.close()
