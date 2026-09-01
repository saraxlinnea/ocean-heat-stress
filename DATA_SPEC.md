# DATA_SPEC.md

Schemas and primary sources for Ocean Heating (Tier C pipeline-first site).

Status values: **seeded** | **planned** | **blocked**

---

## Product spine

| Dataset | Unlocks | Status | Notes |
|---------|---------|--------|-------|
| NOAAGlobalTemp v6 ocean annual (ERSST) | Intro sparkline; Overview dual SST chart | seeded | Direct NCEI ASCII; native 1971–2000 baseline |
| OISST v2.1 global annual anomaly | Overview dual SST chart | seeded | ERDDAP yearly chunks; 1971–2000 native `anom` |
| NOAA CPC ONI (seasonal) | Overview ENSO timeline + decade bars | seeded | `oni.ascii.txt`; classic ONI (not RONI); derived episodes |
| OISST regional daily (blob / gbr) | Case SST charts + MHW bands | blocked | Files may be empty `[]` after soft ERDDAP failure. UI must show Illustrative + miss/fail until non-empty. Pipeline reconciles `status: empty`. |
| Ecosystem literature series | Ecosystem bar charts | seeded | Transcribed / approximate; treat as quarantine-grade until verified |
| Ningaloo / Tasman / NE Atlantic SST | Those three case SST charts | planned | Illustrative in `index.html` until regional pipeline |

---

## Critical exclusions

- Do **not** treat NOAA Coral Reef Watch `mhw_5km` as the MHW series plotted here (related product only).
- Do **not** mix hero **1971–2000** anomalies with regional **1991–2020** Hobday anomalies on one unlabeled chart.
- Do **not** present author-built composites (Tasman aquaculture index, NE Atlantic signal index) as NOAA products.
- Do **not** invent year-by-year FOSS CPUE; literature transcription stays unlabeled as live NOAA until FOSS-wired.
- Quarantine: any series with `verified: false` in dashboard data or `ECOSYSTEM` in `ohsi_preprocessing.py` until primary tables are checked.

---

## Schemas

### `data/global_ersst.json`

**Source:** NCEI NOAAGlobalTemp v6 ocean annual ASCII (`NOAA_OCEAN_FILE` in `ohsi_preprocessing.py`)

**Fields:**

| Column | Type | Unit | Notes |
|--------|------|------|-------|
| year | int | calendar year | |
| anom | float | °C | vs 1971–2000 |

**Derived:** none (as published)

---

### `data/global_oisst.json`

**Source:** ERDDAP `ncdcOisst21Agg_LonPM180` field `anom`, yearly chunks, spatial stride 8, area-weighted

**Fields:**

| Column | Type | Unit | Notes |
|--------|------|------|-------|
| year | int | calendar year | typically 1982–present; incomplete years skipped |
| anom | float | °C | vs 1971–2000 |

**Derived:** monthly mid-month samples → annual mean of area-weighted fields

---

### `data/oni.json`

**Source:** NOAA CPC `oni.ascii.txt` (ERSSTv6-based Oceanic Niño Index)

**Top-level fields:**

| Field | Type | Notes |
|-------|------|-------|
| index | string | `"ONI"` |
| source / source_url | string | CPC provenance |
| note | string | Classic ONI, not RONI; episode rule documented |
| threshold_c | float | 0.5 |
| min_seasons | int | 5 |
| seasons | array | Seasonal ONI rows |
| episodes | array | Derived El Niño / La Niña episodes |
| decade_summary | array | Episode counts and strong-share by decade |

**`seasons[]` fields:**

| Column | Type | Notes |
|--------|------|-------|
| season | string | CPC label (DJF, JFM, …) |
| year | int | Season year |
| oni | float | °C anomaly |
| start / end | string | ISO date bounds for season window |

**`episodes[]` fields:** phase (`el_nino` \| `la_nina`), start, end, duration_seasons, peak_oni, peak_season, strength (`weak` \| `moderate` \| `strong` \| `very_strong`)

**`decade_summary[]` fields:** decade, decade_start, el_nino_count, la_nina_count, episode_count, strong_or_greater, strong_or_greater_share, max_abs_peak_oni, mean_abs_peak_oni, max_peak_oni, max_peak_phase, very_strong_count, is_partial

**Top-level:** `latest_year` (int, last season year in CPC file)

**Derived:** episodes when |ONI| ≥ 0.5°C for ≥5 consecutive overlapping seasons (CPC convention). Decade summary from episode peak years; `is_partial` true when `latest_year` has not reached decade end.

---

### `data/blob_sst.json` / `data/gbr_sst.json`

**Source:** ERDDAP OISST `sst`, regional bbox, daily, yearly chunks, stride 8; anomalies vs Hobday seasonal climatology when available

**Fields:**

| Column | Type | Unit | Notes |
|--------|------|------|-------|
| date | string | ISO date (month start) | `YYYY-MM-01` |
| anom | float | °C | monthly mean of daily anomaly |

**Derived:** area-weighted daily SST → Hobday clim `seas` subtraction (or series-mean fallback) → monthly mean. Dates normalized to calendar midnight before reindex.

**Integrity:** refuse `status: ok` if this array is empty.

---

### `data/blob_mhw.json` / `data/gbr_mhw.json`

**Source:** `marineHeatWaves.detect` (Hobday et al. 2016) on regional daily SST

**Fields:**

| Column | Type | Unit | Notes |
|--------|------|------|-------|
| start / end / peak_date | string | ISO date | |
| peak_intensity / mean_intensity | float | °C | relative to clim |
| duration_days | int | days | |
| category | int or null | 1–4 | Moderate→Extreme |
| category_name | string or null | | |

**Derived:** climatology period clamped to available years within 1991–2020.

---

### `data/ecosystem.json`

**Source:** hardcoded `ECOSYSTEM` dict in `ohsi_preprocessing.py` (literature)

**Fields (per series):** label, unit, source, verified (bool), note, series `[{year, v}]`, annotations

**Quarantine:** all current series ship with `verified: false`.

---

### `data/meta.json`

**Source:** written each pipeline run

**Key statuses:** `ersst_status`, `oisst_global_status`, `oni_status`, `regions.<key>.status` (`ok` \| `fetch_failed` \| `failed` \| `empty`), optional `error`, `n_events`, `n_months`

**UI:** `index.html` data-status bar requires **non-empty** JSON arrays for green checks. Meta `ok` alone is not enough. Empty `[]` → miss/fail; case FALLBACK stays Illustrative until `applyRegionalSst` loads rows. Actions exit 0 on soft ERDDAP failure; green workflow ≠ all layers ok.

---

## Pipeline commands

```bash
# From repo root, with venv active:
python ohsi_preprocessing.py
# Nightly: .github/workflows/update-data.yml (timeout 40m, numpy<2)
```

**Landmines:** ERDDAP retry/backoff; yearly chunking; normalize noon timestamps; pin `numpy<2` for marineHeatWaves; NCEI 503 retry on ERSST ASCII.
