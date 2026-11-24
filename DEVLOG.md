## 2026-11-24 - Background depth, download, table polish

- Shipped an animated contour field on `#bgfx` (40 polylines, three summed sines, accent at 4 to 11 per cent alpha, 30fps, stops on `visibilitychange`, single static draw under reduced motion), plus a two-stop accent glow behind the masthead and a mask that fades the field out by 88 per cent down the page. The canvas had existed since the shell was copied but nothing ever drew on it, which is why the page read as a flat navy fill.
- `Download data` on the tab row, solid accent button, CSV of the current sort: 12 columns, rounded, UTF-8 BOM.
- Masthead rule removed; National Plans table left-aligned; table caption removed; ISO3 fallback names for Cook Islands, Niue, Vatican City.
- IGO copy pass, merged evaluation state (hatched), EU endorsement as a lighter blue, labelled theme button with a real icon sprite.

# DashElectrify - devlog

Live: https://electrifysimon.github.io/dashelectrify/ (Staticrypt passphrase `electrify`).
Repo: ElectrifySimon/dashelectrify, branch main, GitHub Pages legacy build.

## State, 2026-11-23

- 180 countries in the data layer, 177 drawn on the map (three have no Natural Earth geometry: Kosovo, Vatican, plus one WB-only aggregate dropped).
- 5 KPI cards, 5 tabs (Economics, Access, Renewables, WETO, Table), 16 ECharts panels, one SVG world choropleth.
- Machine check on the live URL after unlock: `kpis 5, map paths 177, chart canvases 4, pageerrors []`.

## Data

- Pledge: `/home/simon/static/cop31/COP31_TRK_Pledge-Signatories_2026-11-17.html` on LXC 104, captured 2026-11-20 06:02 TRT. 60 national + 24 EU-covered + EU entry = 85. Parsed by `build_data.py`, never retyped.
- World Bank WDI live API, nine series, last updated 2026-11-11, cached in `data/raw/`.
- WETO: three IRENA 2026 figures copied out of `weto-charts/charts.json` (f14, f23a, f21).

## Palette (not dashdist)

Navy, not graphite-mint: `--bg #070b13`, `--surface #0d1522`, accent electric blue `#4a8cff`, EU-covered amber `#f0b45a`, non-signatory `#20304a`.

## Build chain

`build_data.py` -> `data/dashboard.json` -> `build.py` (inlines data + geometry + WETO into one HTML) -> `publish.sh` (Staticrypt) -> `index.html` at repo root.

## Traps found

- dashdist CSS carries a later "v2 surface" token block that overrides `--accent`; editing only the first block looks like a no-op.
- The map is hand-built SVG paths, not MapLibre: no WebGL, no external tiles, works headless.
- `python3 -m http.server` serves `.mjs` fine, but an ES module import only resolves when `vendor/` sits beside the HTML; `build/vendor` is a symlink for local tests.
- Headless Chrome ignores `--window-size` here; use `scripts/shot.py` (Playwright) for screenshots and console capture.

## Traps found (cont.)

- `countries.geo.json` properties are `{iso, name}` only. Keying a name lookup on `iso_a3` silently yields an empty dict and every country falls back to its ISO3 code. Resolve from `properties.iso`, then the World Bank payload's own `country.value`, then the code as a last resort.
- Natural Earth 110m drops tiny states (Singapore, Andorra, Monaco, Maldives, Seychelles, Micronesia and six more). They have WDI data but no geometry, so names must come from the data source, not the map file.

## Open

- Light-theme gridlines and no-data land are washed out; darken `--line` and the no-data fill.
- The cron that copies the Presidency Google Sheet was never located; refreshing means re-pulling the rendered page on LXC 104.
- Legend swatch sizes still inherit a 16x3 rule from the dashdist stylesheet.
