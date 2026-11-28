import sys
from playwright.sync_api import sync_playwright

url = "http://127.0.0.1:8811/index.html"
w = int(sys.argv[1]) if len(sys.argv) > 1 else 412
h = int(sys.argv[2]) if len(sys.argv) > 2 else 839
tag = sys.argv[3] if len(sys.argv) > 3 else "412"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable",
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
    pg.goto(url, wait_until="load", timeout=45000)
    pg.wait_for_timeout(2000)
    pg.screenshot(path=f"/tmp/vp-{tag}.png")
    for sel, name in [(".mapwrap", "map"), (".tabrow", "tabrow"), (".kpis", "kpis")]:
        el = pg.query_selector(sel)
        if el:
            el.screenshot(path=f"/tmp/el-{name}-{tag}.png")
    info = pg.evaluate("""() => {
      const g = s => { const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect();
        return {x:Math.round(r.x), y:Math.round(r.y+scrollY), w:Math.round(r.width), h:Math.round(r.height)}; };
      return {doc: document.documentElement.scrollWidth, vw: innerWidth,
              tabrow: g('.tabrow'), map: g('.mapwrap'), cmap: g('#c-map'), svg: g('#c-map svg'),
              legend: g('.legend'), dl: g('#dl'),
              tabsOverflow: (()=>{const t=document.querySelector('.tabs'); return t? {sw:t.scrollWidth, cw:t.clientWidth}:null})()};
    }""")
    print(tag, info)
    b.close()
