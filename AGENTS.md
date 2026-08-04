# AGENTS.md

Guidance for humans and coding agents working on this repo.

## What this project is

Single-file science communication dashboard (D3 + precomputed JSON) on ocean warming, marine heatwaves (Hobday), and ecosystem case studies. Every user-facing number needs a source, pipeline provenance, or an explicit illustrative / literature-transcribed / unverified label. Prefer empty, null, or "-" with a short reason over fabricated values.

## Sibling / end-state policy

Independent portfolio piece. Live at GitHub Pages (`saraxlinnea.github.io/ocean-heat-stress`). Not affiliated with NOAA. No merge into other factory apps unless explicitly planned.

## Read first

1. `README.md` — product summary, baselines, citations, pipeline
2. `data/` — precomputed JSON consumed by `index.html`
3. `ohsi_preprocessing.py` — fetch + Hobday + write JSON
4. `notebooks/methods.ipynb` — sanity-check plots against `data/`
5. This file — honesty and branding constraints

`CLAIMS.md` / `DATA_SPEC.md` are draft scaffolds in-repo. Do not invent claim IDs beyond those drafts. Do not lock or upgrade claim strength without explicit user OK. Use existing UI labels (NOAA, illustrative, unverified) as the live honesty chrome.

## Run order

```bash
# optional data refresh
pip install requests pandas numpy scipy
pip install git+https://github.com/ecjoliver/marineHeatWaves.git
python ohsi_preprocessing.py

# serve the single file locally (any static server)
python -m http.server 8000
# open http://localhost:8000/
```

## Branding & theme

preset: custom-ocean (polish only; no scaffold token swap)
path: none — keep existing tokens and type in `index.html`
Do not mix scaffold presets. Do not fall back to purple SaaS, soft multi-shadow cards, or generic Inter-on-white.

Locked product look (do not replace unless the user asks):

```css
:root {
  --bg: #F7F9FC;
  --ink: #1A3A4A;
  --blue: #2E7DAF;
  --heat: #E8572A;
  --lblue: #6AACCA;
  --gray: #9B9B9B;
  --rule: #DDE3E8;
  --white: #FFFFFF;
}
```

Type stack: IBM Plex Sans, IBM Plex Mono, DM Serif Display.

Visual work is CSS/layout polish only unless the user expands scope. Keep honesty chrome (`ds-pill`, `source-pill`, `unverified-tag`).

## Hard rules

- Do **not** invent rates, rankings, emission factors, bill $, peaks, or case-study magnitudes.
- Prefer empty / null / "-" with a short reason over fabricated numbers.
- Every user-facing number needs a source or an explicit claim-strength label.
- Weak / Speculative must say illustrative, modeled, literature-transcribed, or unverified.
- Do not strip NOAA vs illustrative labels or unverified tags for aesthetics.
- No em dashes in user-facing copy.
- Do not commit secrets (`.env`).
- Do not commit, push, or deploy unless the user explicitly asks.
- Claim strength follows AI-OS `CORE/EVIDENCE_STANDARD.md` when claim files exist; until then, preserve existing UI honesty labels.

## Domain landmines

- Do not change Hobday MHW logic, climatology baselines, or chart series without an explicit data task.
- Global hero baseline (1971–2000 NOAA native) differs from regional case-study climatology (1991–2020). Do not collapse them into one story line.
- Illustrative monthly series (Ningaloo / Tasman / NE Atlantic) are not OISST-pipelined; keep that visible.
- Snow crab / some eco indices may be approximate or unverified year-by-year; keep tags.
- Imagery must not imply causation or document a named facility/event as measurement proof. No photos behind charts, map, peak band, or claim numbers.
- Home entrance may use a muted local photo (`images/home-ocean-horizon.jpg`); see `media/SOURCES.md`. Chart and proof row stay on clean canvas.

## Frontend conventions

- Single deployable `index.html` (vendored D3/topojson + inline CSS/JS)
- Data from `./data/*.json`
- Primary views (same ocean chrome):
  - **Home** (`#home`) — fullscreen photo stage: grand title, tagline, CTA, proof stack, ERSST 1981+ sparkline, condensed foot links. Site header, primary nav, and full footer hidden on this view.
  - **Case studies** (`#cases`) — index of five regions; open one to read
  - **Case detail** (`#case/{id}`) — map, peak, SST, eco, interpretation for one case (`ningaloo` | `blob` | `tasman` | `gbr` | `ne_atlantic`)
  - **Methods & sources** (`#methods`) — provenance, baselines, Hobday notes, resources grid (full global chart context lives here / in methods copy, not on Home)
- Keep NOAA / illustrative / unverified honesty chrome on case detail charts
- Footer disclaimer stays across views
- Spacing uses CSS rhythm tokens `--s1`…`--s5` (8 / 16 / 24 / 40 / 56)
- Do not collapse Home + Cases + Case detail back into one scroll without an explicit ask

## Parked / out of scope until planned

- Scaffold preset token migration
- Photo hero / muted backgrounds (propose licenses first; wait for OK before download)
- Full `CLAIMS.md` / `DATA_SPEC.md` / `BENCHMARKS.md` lock-in
- Framework rewrite (React/Vite) away from single-file HTML

## Git hygiene

- Ignore `.venv/`, `__pycache__/`, `.env`, `.DS_Store`
- Commit processed `data/` when the demo must run without a live pull
- Do not force-push `main` / `master`
