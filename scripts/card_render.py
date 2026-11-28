"""Render scripts/card.html to social-preview.png at exactly 1200x630."""
from playwright.sync_api import sync_playwright
from PIL import Image

HTML = "file:///home/simon/projects/dashelectrify/scripts/card.html"
OUT = "/home/simon/projects/dashelectrify/social-preview.png"

with sync_playwright() as p:
    b = p.chromium.launch(
        executable_path="/usr/bin/google-chrome-stable",
        args=["--no-sandbox", "--disable-dev-shm-usage",
              "--allow-file-access-from-files", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=2)
    pg.goto(HTML, wait_until="load")
    pg.wait_for_timeout(1400)
    pg.screenshot(path="/tmp/card-2x.png")
    b.close()

im = Image.open("/tmp/card-2x.png").convert("RGB")
im.resize((1200, 630), Image.LANCZOS).save(OUT, optimize=True)
print("saved", Image.open(OUT).size)
