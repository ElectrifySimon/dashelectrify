"""Audit the social card layout: overflow, overlap, contrast of key blocks."""
import json
from playwright.sync_api import sync_playwright

HTML = "file:///home/simon/projects/dashelectrify/scripts/card.html"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable",
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto(HTML, wait_until="load")
    pg.wait_for_timeout(1200)
    out = pg.evaluate("""() => {
      const box = s => { const e = document.querySelector(s); if (!e) return null;
        const r = e.getBoundingClientRect();
        return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height),
                overflow: e.scrollWidth - Math.round(r.width)}; };
      const bodyOverflow = document.body.scrollWidth - 1200;
      const sel = ['.copy','h1','.sub','.stats','.legend','.foot','.badge','.mapwrap'];
      const boxes = Object.fromEntries(sel.map(s => [s, box(s)]));
      // overlap test between copy blocks and the map
      const ov = (a, bb) => !(a.x + a.w <= bb.x || bb.x + bb.w <= a.x || a.y + a.h <= bb.y || bb.y + bb.h <= a.y);
      const pairs = [['h1','.mapwrap'],['.sub','.mapwrap'],['.stats','.legend'],['.badge','.mapwrap'],['.foot','.legend']];
      const overlaps = pairs.filter(([x, y]) => boxes[x] && boxes[y] && ov(boxes[x], boxes[y])).map(([x, y]) => x + '/' + y);
      return {bodyOverflow, boxes, overlaps};
    }""")
    print(json.dumps(out, indent=1))
    b.close()
