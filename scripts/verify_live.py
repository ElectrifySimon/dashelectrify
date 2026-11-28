"""Unlock the live gated page and measure the phone layout fixes."""
import json
from playwright.sync_api import sync_playwright

URL = "https://electrifysimon.github.io/dashelectrify/"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable",
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 412, "height": 839}, device_scale_factor=1)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:150]))
    pg.on("console", lambda m: errs.append("console: " + m.text[:120]) if m.type == "error" else None)
    pg.goto(URL, wait_until="load", timeout=60000)
    pg.wait_for_timeout(1200)
    pg.fill("input[type=password]", "electrify")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(3500)
    out = pg.evaluate("""() => {
      const g = s => { const e = document.querySelector(s); if (!e) return null;
        const r = e.getBoundingClientRect();
        return {y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height)}; };
      const t = document.querySelector('.tabs');
      return {
        theme: document.documentElement.dataset.theme,
        kpis: document.querySelectorAll('#kpis .kpi').length,
        mapPaths: document.querySelectorAll('#c-map path').length,
        tabrow: g('.tabrow'), cmap: g('#c-map'), legend: g('.mapwrap .legend'),
        tabsOverflow: t ? t.scrollWidth - t.clientWidth : null,
        dl: g('#dl'), docW: document.documentElement.scrollWidth, vw: innerWidth,
        tableCols: document.querySelectorAll('#tbl thead th').length,
        og: !!document.querySelector('meta[property="og:image"]'),
        scrollH: document.body.scrollHeight,
      };
    }""")
    print("LIVE", json.dumps(out))
    pg.evaluate("document.getElementById('tab-econ').click()")
    pg.wait_for_timeout(1200)
    print("ECON canvases", pg.evaluate("document.querySelectorAll('#econ canvas').length"))
    pg.evaluate("document.getElementById('tab-table').click()")
    pg.wait_for_timeout(800)
    pg.evaluate("""() => { const w=document.querySelector('#tblwrap'); w.scrollIntoView(); w.scrollTop=300; }""")
    pg.wait_for_timeout(400)
    print("STICKY", pg.evaluate("""() => {
      const w=document.querySelector('#tblwrap'); const th=w.querySelector('thead th');
      const r=th.getBoundingClientRect(); const el=document.elementFromPoint(r.x+12, r.y+6);
      return {hit: el ? el.tagName : null, thY: Math.round(r.y)}; }"""))
    pg.screenshot(path="/tmp/live-412.png", full_page=False)
    print("ERRS", errs[:6])
    b.close()
