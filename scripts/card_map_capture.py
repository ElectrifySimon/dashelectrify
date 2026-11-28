"""Capture the bare world map SVG from the local build, no HTML overlays."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable",
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 1600, "height": 1100}, device_scale_factor=2)
    pg = ctx.new_page()
    pg.add_init_script("localStorage.setItem('de-theme','dark')")
    pg.goto("http://127.0.0.1:8811/index.html", wait_until="load")
    pg.wait_for_timeout(2500)
    pg.evaluate("""() => {
      for (const s of ['.mapbar', '.legend', '.mapnote', '.maptip', '#panel'])
        document.querySelectorAll(s).forEach(e => e.style.display = 'none');
      const m = document.querySelector('.mapwrap');
      if (m) m.style.background = 'transparent';
    }""")
    pg.wait_for_timeout(300)
    pg.query_selector("#c-map svg").screenshot(path="/tmp/card-map-svg.png")
    print("captured")
    b.close()
