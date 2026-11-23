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

echo "--- gated ---"
du -h gated/index.html
