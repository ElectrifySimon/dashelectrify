# DashDist design spec

Written before layout, in the Refero Styles sense: a machine-readable description
of the surface, not a mood board. Tokens below are the contract; the page is the
implementation.

## Surface

Two themes, one set of roles. Body is the page, surface is a card, raised is a
control that floats above the page. Never a third background.

| Role | Dark | Light |
|---|---|---|
| bg | #1b1b1b | #f1f1f1 |
| surface | #262626 | #ffffff |
| muted surface | #303030 | #e2e2e2 |
| ink | #f2f2f2 | #151515 |
| secondary ink | #9e9e9e | #474747 |
| line | #525252 | #d4d4d4 |
| accent | #90d7c8 | #00463d |
| accent ink | #16211f | #f4fffc |

Accent carries selection and one emphasis per screen. It is not a decoration.

## Type

Instrument Sans for interface, Bricolage Grotesque for the wordmark and section
titles, tabular figures in every number column.

| Step | Size | Weight | Use |
|---|---|---|---|
| display | 27px | 600 | page title only |
| h2 | 15px | 600 | section titles |
| body | 14px | 400 | default |
| small | 12.5px | 400 | labels, meta |
| micro | 11px | 500 | axis ticks, table heads |

Letter spacing is 0 except the wordmark (0.16em, uppercase).

## Space

4px base: 4, 8, 12, 16, 24, 32, 48. Section rhythm is 28px above, 16px below a
section head. Cards use 16px padding, never less.

## Elevation

Three levels, one light source from above.

- e1: `inset 0 1px 0 rgba(255,255,255,.07), 0 1px 2px rgba(0,0,0,.40)` controls
- e2: `inset 0 1px 0 rgba(255,255,255,.07), 0 2px 4px rgba(0,0,0,.35), 0 14px 34px rgba(0,0,0,.40)` cards, map
- e3: `inset 0 1px 0 rgba(255,255,255,.07), 0 10px 20px rgba(0,0,0,.40), 0 30px 70px rgba(0,0,0,.55)` overlay, legend

Light theme swaps black shadows for `rgba(16,24,32,...)` at a third of the alpha.

## Radius

10px controls, 12px containers. Nothing rounder.

## Motion

| Token | Value | Use |
|---|---|---|
| d-feedback | 120ms | press, toggle |
| d-ui | 220ms | hover, tab change |
| d-panel | 320ms | overlay, panel |
| e-out | cubic-bezier(.16,1,.3,1) | entrances |
| e-in | cubic-bezier(.7,0,.84,0) | exits |
| e-io | cubic-bezier(.65,0,.35,1) | layout shifts |

Entrance is 8px rise plus opacity, 30ms stagger, once per page load. Everything
above collapses under `prefers-reduced-motion: reduce`.

## Components

- **Button**: 44px min height, 10px radius, e1, hover raises to e2, press drops
  to 1px translate and e1. Primary is accent fill with a top highlight.
- **Tab**: text, not a pill. Selected state is accent text plus a 2px underline
  at the border of the strip.
- **Table**: sticky head, 40px rows, hairline separators, hover row tint plus a
  2px accent bar on the left edge, numeric columns right aligned.
- **Card**: surface, 12px radius, e2, 16px padding, no border.

## Rules

- No number in prose. Numbers live in data positions or they age badly.
- One subtitle under the title. A subtitle plus a standfirst is padding.
- Provenance, licence and date belong at the foot.
- Text contrast at least 4.5:1; non-text at least 3:1.
- Nothing animates on a data mark. Motion happens on chrome only.
