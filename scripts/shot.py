#!/usr/bin/env python3
"""Screenshot a local page with Playwright, collecting console errors.

Usage: python3 scripts/shot.py <url> <out.png> [width] [height] [full]
"""
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
out = sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 1440
h = int(sys.argv[4]) if len(sys.argv) > 4 else 1200
full = (len(sys.argv) > 5 and sys.argv[5] == "full")

msgs = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/google-chrome-stable",
        args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader"],
    )
    page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    page.on("console", lambda m: msgs.append(f"{m.type}: {m.text}"[:300]))
    page.on("pageerror", lambda e: msgs.append(f"pageerror: {e}"[:300]))
    page.goto(url, wait_until="load", timeout=45000)
    page.wait_for_timeout(2500)
    info = page.evaluate("""() => ({
      vw: innerWidth, vh: innerHeight,
      kpis: document.querySelectorAll('#kpis .kpi').length,
      mapPaths: document.querySelectorAll('#c-map path').length,
      canvases: document.querySelectorAll('canvas').length,
      chartCanvases: document.querySelectorAll('.cv canvas').length,
      title: document.title,
      scrollH: document.body.scrollHeight
    })""")
    page.screenshot(path=out, full_page=full)
    browser.close()

print("PAGE", info)
for m in msgs[:12]:
    print("LOG", m)
