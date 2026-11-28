from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable",
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 412, "height": 839})
    pg.goto("http://127.0.0.1:8811/index.html", wait_until="load")
    pg.wait_for_timeout(1500)

    def check(wrap_sel):
        return pg.evaluate("""(sel) => {
          const w = document.querySelector(sel); if (!w) return null;
          w.scrollTop = 400; w.scrollLeft = 0;
          const th = w.querySelector('thead th');
          const td = w.querySelector('tbody td');
          const thR = th.getBoundingClientRect(), tdR = td.getBoundingClientRect();
          const ths = [...w.querySelectorAll('thead th')].map(e => e.textContent.trim());
          const tds = [...w.querySelectorAll('tbody tr:first-child td')].map(e => e.textContent.trim());
          return {sw: w.scrollWidth, cw: w.clientWidth, thText: th.textContent.trim(),
                  thBottom: Math.round(thR.bottom), tdTop: Math.round(tdR.top),
                  overlap: Math.round(thR.bottom - tdR.top), cols: ths.length, ths: ths, tds: tds,
                  firstColW: Math.round(thR.width)};
        }""", wrap_sel)

    print("TABLE", check("#tblwrap"))
    pg.evaluate("document.getElementById('tab-plans').click()")
    pg.wait_for_timeout(900)
    print("PLANS", check("#plans .tblwrap"))
    print("SCROLLHINT", pg.evaluate("""() => { const h=document.querySelector('.scrollhint');
        return h? {disp:getComputedStyle(h).display, txt:h.textContent} : null }"""))
    b.close()
