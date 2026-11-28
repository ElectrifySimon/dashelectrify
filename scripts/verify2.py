"""Verify the phone fixes on the live page: tabs, table header, legend, charts."""
import json
from playwright.sync_api import sync_playwright

URL = "https://electrifysimon.github.io/dashelectrify/"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable",
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 412, "height": 839})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
    pg.goto(URL, wait_until="load", timeout=60000)
    pg.wait_for_timeout(900)
    pg.fill("input[type=password]", "electrify")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(3200)

    base = pg.evaluate("""() => {
      const t = document.querySelector('.tabs'), tr = document.querySelector('.tabrow');
      const tabs = [...document.querySelectorAll('.tab')];
      const lg = document.querySelector('.mapwrap .legend');
      return {theme: document.documentElement.dataset.theme,
              tabrowH: Math.round(tr.getBoundingClientRect().height),
              tabsOverflow: t.scrollWidth - t.clientWidth,
              tabLabels: tabs.map(x => x.textContent.trim()),
              tabRects: tabs.map(x => Math.round(x.getBoundingClientRect().right)),
              vw: innerWidth,
              legendBg: getComputedStyle(lg).backgroundColor,
              legendColor: getComputedStyle(lg.querySelector('.lg-k')).color,
              firstCellPos: getComputedStyle(document.querySelector('#tbl tbody td')).position,
              thSticky: getComputedStyle(document.querySelector('#tbl thead th')).position,
              kpi: [...document.querySelectorAll('#kpis .kpi')].map(k => k.querySelector('.n').textContent)};
    }""")
    print("BASE", json.dumps(base))

    # table header vs first row with the page scrolled so the table is in view
    pg.evaluate("document.querySelector('#tblwrap').scrollIntoView()")
    pg.wait_for_timeout(300)
    pg.evaluate("window.scrollBy(0, -70)")
    pg.evaluate("document.querySelector('#tblwrap').scrollTop = 260")
    pg.wait_for_timeout(300)
    print("TABLE", pg.evaluate("""() => {
      const w = document.querySelector('#tblwrap'), th = w.querySelector('thead th');
      const r = th.getBoundingClientRect();
      const hit = document.elementFromPoint(r.x + 10, r.y + 6);
      const rowUnder = document.elementFromPoint(r.x + 10, r.y + r.height + 8);
      return {thY: Math.round(r.y), hit: hit && hit.tagName, hitText: hit && hit.textContent.trim().slice(0, 14),
              under: rowUnder && rowUnder.tagName, underText: rowUnder && rowUnder.textContent.trim().slice(0, 14)};
    }"""))

    pg.evaluate("document.getElementById('tab-econ').click()")
    pg.wait_for_timeout(1200)
    print("ECON", pg.evaluate("""() => [...document.querySelectorAll('#econ canvas')].length"""))
    print("LEGEND", pg.evaluate("""() => {
      const el = document.querySelector('#c-scatter');
      const opt = window.echarts ? echarts.getInstanceByDom(el).getOption() : null;
      const l = opt && opt.legend && opt.legend[0];
      return l ? {bottom: l.bottom, top: l.top, type: l.type} : null;
    }"""))
    pg.screenshot(path="/tmp/live2-412.png")
    print("ERRS", errs[:4])
    b.close()
