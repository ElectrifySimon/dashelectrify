#!/usr/bin/env python3
"""Inline the datasets into data.js so the gated page is one self-contained file."""
import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
data = json.loads((ROOT / "data" / "dashboard.json").read_text())
geo = json.loads((ROOT / "data" / "countries.geo.json").read_text())
weto = json.loads((ROOT / "data" / "weto.json").read_text())

compact = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
body = ("window.ELECTRIFY_DATA=" + compact(data) + ";\n"
        "window.__GEO__=" + compact(geo) + ";\n"
        "window.WETO=" + compact(weto) + ";\n")
(ROOT / "data.js").write_text(body)

html = (ROOT / "index.tpl.html").read_text()
html = html.replace('<script src="data.js"></script>', "<script>\n" + body + "</script>")
html = html.replace("__BUILD_DATE__", datetime.date.today().strftime("%d %B %Y").lstrip("0"))
if "__BUILD_DATE__" in html:
    raise SystemExit("build failed, leftover __BUILD_DATE__")
build = ROOT / "build"
build.mkdir(exist_ok=True)
(build / "index.html").write_text(html)
print(f"build/index.html {len(html):,} bytes, {len(data['countries'])} countries, "
      f"{len(geo['features'])} geometries, {len(weto)} WETO figures")
