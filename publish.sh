#!/usr/bin/env bash
# Build the gated single-file page: gated/index.html, encrypted with Staticrypt.
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py

rm -rf gated
mkdir -p gated/vendor
cp build/index.html gated/index.html
cp vendor/echarts.min.js gated/vendor/
cp -r vendor/fonts gated/vendor/

npx --yes staticrypt@3.5.4 gated/index.html \
  --password "electrify" \
  --directory gated \
  --remember 0 \
  --short \
  --template-title "DashElectrify" \
  --template-instructions "Passphrase required" \
  --template-button "Open" \
  --template-color-primary "#4a8cff" \
  --template-color-secondary "#070b13"

# Gate polish: the Staticrypt shell ignores the page theme and draws a 19px
# checkbox. Both are patched here because the shell is regenerated each build.
python3 - <<'PY'
import pathlib
p = pathlib.Path("gated/index.html")
html = p.read_text()
css = """<style>
html,body{background:#070b13!important;color:#eef3fa!important;color-scheme:dark}
.staticrypt-html,.staticrypt-body{background:#070b13!important}
body,body *{color:#eef3fa}
form input[type=password],form input[type=text]{background:#0d1522!important;color:#eef3fa!important;
  border:1px solid #26364b!important;border-radius:10px;min-height:44px}
form input[type=checkbox]{width:22px;height:22px;accent-color:#4a8cff}
label{display:flex;align-items:center;gap:10px;min-height:44px;cursor:pointer}
button[type=submit]{min-height:44px;border-radius:10px;font-weight:600}
@media(prefers-color-scheme:light){
  html,body{background:#f2f5fa!important;color:#0a1421!important;color-scheme:light}
  .staticrypt-html,.staticrypt-body{background:#f2f5fa!important}
  body,body *{color:#0a1421}
  form input[type=password],form input[type=text]{background:#fff!important;color:#0a1421!important;border-color:#d5deea!important}
}
</style>
"""
if css not in html:
    html = html.replace("</head>", css + "</head>", 1)
p.write_text(html)
print("gate css injected")
PY

# Pages serves the repo root: publish the gated file and its assets there.
cp gated/index.html index.html
rsync -a gated/vendor/ vendor/

echo "--- published ---"
du -h index.html
