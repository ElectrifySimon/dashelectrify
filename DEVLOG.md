## 2026-11-28 - Phone nav pass three

- The wrapped tab strip was still 129 px on an 839 px screen. Below 560 px the strip is replaced by a native view picker ("Choose a view") and the download icon, so the bar is 53 px and every view is reachable with one tap. The seven buttons stay in the DOM for desktop and for anyone on a wider phone.
- Toast moved to the top of the content, under the bar, so the download confirmation stops landing on the map.
- Chart legends: `plain` under five series, `scroll` above it, smaller type under 760 px. The WETO pager arrows only appear when there is something to page.
- National Plans: cells wrap instead of clipping, plan column widened. The panel still needs a stacked layout at phone width; the intro paragraph is clipped by its scroll container.
- Verified live at 412 px: bar 53 px, picker visible, 7 views in the DOM, switching to Plans hides the map block, no page errors.

## 2026-11-24 - Background depth, download, table polish

- Shipped an animated contour field on `#bgfx` (40 polylines, three summed sines, accent at 4 to 11 per cent alpha, 30fps, stops on `visibilitychange`, single static draw under reduced motion), plus a two-stop accent glow behind the masthead and a mask that fades the field out by 88 per cent down the page. The canvas had existed since the shell was copied but nothing ever drew on it, which is why the page read as a flat navy fill.
- `Download data` on the tab row, solid accent button, CSV of the current sort: 12 columns, rounded, UTF-8 BOM.
- Masthead rule removed; National Plans table left-aligned; table caption removed; ISO3 fallback names for Cook Islands, Niue, Vatican City.
- IGO copy pass, merged evaluation state (hatched), EU endorsement as a lighter blue, labelled theme button with a real icon sprite.

## 2026-11-28 - Phone pass, from four agent reports

- Four AI testers ran the live page at 320, 360, 412 and 430 px. First run scored 4, 4, 4, 5 out of 10. Second run after the first fix pass scored 4, 4, 5, 5 and named the remaining defects: hidden tabs, a sliced tab strip, a frozen country column covering its neighbours, map legend text lost on the dark card, chart legends printed over each other, and a gate that ignored the phone theme.
- Nav moved above the KPI grid and pinned with `position:sticky`, background now opaque so figures cannot ghost through the labels. At 760 px the tab row wraps to two rows and every label stays whole; no horizontal strip, no sliced word.
- Download button left the tab strip: 40 px icon at the right of the last tab row on phones, labelled on desktop, with a toast on click.
- Map card is a column: filters, map at 2:1 so it fills the card instead of letterboxing in a 340 px box, legend and note below it on the surface colour. The old legend took the left 210 px of the card because a media query set both `top` and `bottom`.
- Tables: at phone width the first column is no longer frozen, so it stops covering the data beside it; the header stays sticky and sits above the rows. `min-width` keeps the columns from collapsing, and a line under the table says to swipe.
- Charts: legends forced to a scrolling row under the plot (`top` deleted, `bottom: 0`), tooltips confined, subtitles allowed to wrap.
- Numbers: one formatter set. `2.1bn`, `$40.8tn`, `$56,104`; the old code produced `$4685.59bn` and a `1000k` tick.
- Theme: a stored choice wins, otherwise `prefers-color-scheme`. The gate shell gets its own injected CSS at publish time for both themes, a 44 px checkbox and a 44 px field.
- Social card: `social-preview.png` at 1200x630, written from the live numbers (87, 2.1bn, 25.4%, $40.8tn), OG and Twitter tags added, favicon inlined.
- Verified on the live URL at 412 px: 7 tabs, no overflow, header `TH` above the first `TD`, legend on the surface colour, 4 canvases on Economics, no page errors.

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
