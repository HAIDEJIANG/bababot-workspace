#!/usr/bin/env python3
"""Extract LinkedIn cookies from the connected OpenClaw browser relay and save env vars.

Outputs:
  scripts/.linkedin-cli.env with:
    LINKEDIN_LI_AT=...
    LINKEDIN_JSESSIONID=...
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18792"
OUT = Path(__file__).resolve().parent / ".linkedin-cli.env"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        if not browser.contexts:
            raise RuntimeError("No browser context found on CDP relay")
        ctx = browser.contexts[0]
        cookies = ctx.cookies("https://www.linkedin.com")

    li_at = None
    jsid = None
    for c in cookies:
        if c.get("name") == "li_at":
            li_at = c.get("value")
        elif c.get("name") == "JSESSIONID":
            jsid = c.get("value")

    if not li_at or not jsid:
        missing = []
        if not li_at:
            missing.append("li_at")
        if not jsid:
            missing.append("JSESSIONID")
        raise RuntimeError("Missing LinkedIn cookie(s): " + ", ".join(missing))

    OUT.write_text(
        "LINKEDIN_LI_AT=" + li_at + "\n" +
        "LINKEDIN_JSESSIONID=" + jsid + "\n",
        encoding="utf-8"
    )
    print(f"Saved LinkedIn CLI env to: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
