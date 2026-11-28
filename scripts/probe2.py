import sys
from playwright.sync_api import sync_playwright

w = int(sys.argv[1]) if len(sys.argv) > 1 else 412
h = int(sys.argv[2]) if len(sys.argv) > 2 else 839
tag = str(w)
tabs = ["tblwrap", "country", "econ", "access", "renew", "weto", "plans"]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable",
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    errs = []
    pg.on("console", lambda m: errs.append(m.type + ": " + m.text[:120]) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)[:120]))
    pg.goto("http://127.0.0.1:8811/index.html", wait_until="load", timeout=45000)
    pg.wait_for_timeout(1800)
    pg.screenshot(path=f"/tmp/p2-top-{tag}.png")
    pg.query_selector(".mapwrap").screenshot(path=f"/tmp/p2-map-{tag}.png")
    for t in tabs:
        pg.eval_on_selector(f"#tab-{t.replace('tblwrap','table')}", "e => e.click()")
        pg.wait_for_timeout(900)
        pg.screenshot(path=f"/tmp/p2-{t}-{tag}.png")
        info = pg.evaluate("""() => {
          const c = document.querySelector('#c-map'); return {h: document.body.scrollHeight, ov: !document.getElementById('overview').hidden};
        }""")
        print(t, info)
    print("ERRS", errs[:8])
    b.close()
