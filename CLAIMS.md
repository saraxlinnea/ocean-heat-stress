# CLAIMS.md

Claim strength labels for this product (AI-OS / EVIDENCE_STANDARD-aligned).

**Status: DRAFT ONLY.** No claims are locked. Do not treat draft strengths as final.
Do not upgrade or lock a label without new primary evidence and **explicit user OK**.

Strength scale:

| Strength | Meaning here |
|----------|----------------|
| **Strong** | Primary source or definitional identity; cross-checked where noted |
| **Moderate** | Verified inputs with known model simplifications or year mismatch |
| **Weak** | Back-of-envelope, literature transcription, or conditional on heavy assumptions |
| **Weak / Speculative** | Illustrative series or author-built composite, not a live NOAA product |

**UI rule:** Strong / Moderate may appear as plain metrics. Weak / Speculative must say "illustrative," "modeled," "unverified," or show a claim id. Prefer empty / "-" with reason over invented fills.

**Empty pipeline rule:** Blob / GBR show **Illustrative** (and status miss/fail) when `blob_*.json` / `gbr_*.json` are empty. Never show a NOAA OISST pill on FALLBACK series.

---

## Locked claims

_None. Awaiting user OK to lock any draft below._

| ID | Claim | Label | Evidence |
|----|--------|--------|----------|
| - | - | - | - |

---

## Live UI map by route (draft mapping)

### Home (`#home`)

| UI element | Draft claim | Label shown today |
|------------|-------------|-------------------|
| Proof stack >90% ocean heat uptake | OH1 | Source line under figure |
| Proof stack 2× MHW days since 1982 | OH2 | Source line |
| Proof stack 70–90% reefs at 1.5°C | OH3 | Source line ("severely degraded or gone") |
| ERSST sparkline 1981–present | OH4 | Live from `global_ersst.json` when present |
| Home foot non-affiliation | OH20 | Condensed disclaimer |

### Case studies index (`#cases`)

| UI element | Draft claim | Label shown today |
|------------|-------------|-------------------|
| Case blurbs (peaks, impacts) | OH5–OH9, OH17–OH19 | Narrative copy; not NOAA pills |

### Case detail (`#case/{id}`)

| UI element | Draft claim | Label shown today |
|------------|-------------|-------------------|
| Peak band + case peak °C | OH5–OH9 | Peak context copy |
| Blob SST / MHW | OH10 | NOAA OISST pill only when non-empty pipeline JSON; else Illustrative |
| GBR SST / MHW | OH11 | Same |
| Ningaloo / Tasman / NE Atlantic SST | OH12 | Illustrative pill |
| Pacific cod CPUE series | OH13 | unverified tag |
| EBS snow crab index | OH14 | unverified tag |
| GBR bleaching % series | OH15 | unverified tag |
| Tasman / NE Atlantic ecosystem composites | OH16 | unverified + illustrative |
| Cod 71% decline 2015→2017 (caption/interp) | OH17 | Cited Barbeaux; series still unverified |
| West-coast kelp 43% loss | OH18 | Cited Wernberg |
| GBR 91% bleaching 2016 | OH19 | Cited Hughes |

### Methods (`#methods`)

| UI element | Draft claim |
|------------|-------------|
| Baseline / Hobday / latency copy | OH4, OH10, OH11, method text |
| Illustrative case caveat | OH12, OH16 |
| Full footer NOAA disclaimer | OH20 |

---

## Drafts (not locked)

Proposed IDs and **suggested** strengths for review. Change or reject freely before lock.

| ID | Claim (plain language) | Suggested strength | Evidence / notes |
|----|------------------------|--------------------|------------------|
| **OH1** | More than 90% of Earth's excess heat since industrialization has been absorbed by the ocean | Moderate | von Schuckmann et al. 2023 ESSD; NOAA NCEI framing. Confirm exact wording vs paper before Strong |
| **OH2** | Marine heatwave days roughly doubled globally since 1982; models project large further increases at 1.5°C | Moderate | Frölicher et al. 2018 Nature. "2×" and "16-fold" are paper-derived; keep cited |
| **OH3** | At 1.5°C warming, ~70–90% of coral reefs are projected to be severely degraded or lost | Moderate | IPCC SR1.5 / Hoegh-Guldberg et al. Projection, not observation |
| **OH4** | Global ocean surface temperature anomaly (ERSST sparkline on Home; full dual series in Methods context) | Strong (when files present) | Pipeline `global_ersst.json` / `global_oisst.json`; native 1971–2000 baselines |
| **OH5** | Ningaloo 2011 peak monthly anomaly ~+6.8°C; Category IV; ~66 days | Weak | Literature / illustrative SST until pipelined |
| **OH6** | Pacific Blob GOA peak ~+2.5°C above 90th-percentile baseline; multi-year persistence | Weak until pipeline non-empty; Moderate when live | Bond / Hobday literature + pipeline peak when live |
| **OH7** | Tasman 2015–16 peak ~+2.9°C; duration ~251 days | Weak | Oliver et al. 2017; illustrative SST |
| **OH8** | GBR bleaching-era peak anomaly ~+1.7°C (case peak shown) | Weak until pipeline non-empty; Moderate when live | Pipeline / literature case framing |
| **OH9** | NE Atlantic June 2023 peak ~+2.9°C for ~16 days on shelf climatology | Weak | England et al. 2025; illustrative SST |
| **OH10** | Gulf of Alaska monthly SST anomalies and Hobday MHW events from OISST pipeline | Strong (when `blob_*.json` non-empty and meta ok) | `ohsi_preprocessing.py` + ERDDAP. Empty on-disk → Illustrative FALLBACK |
| **OH11** | Great Barrier Reef monthly SST anomalies and Hobday MHW events from OISST pipeline | Strong (when `gbr_*.json` non-empty and meta ok) | same |
| **OH12** | Ningaloo / Tasman / NE Atlantic monthly SST charts | Weak / Speculative | Explicit illustrative fallbacks in `index.html` |
| **OH13** | Pacific cod CPUE year-by-year bars | Weak | Literature-transcribed; `verified: false`; not live FOSS |
| **OH14** | EBS snow crab relative abundance index (2018=100) | Weak / Speculative | Approximate; pending AFSC table verification |
| **OH15** | GBR % reefs bleached by year | Weak | Transcribed Hughes / AIMS / CRW; survey years irregular |
| **OH16** | Tasman aquaculture and NE Atlantic ecosystem composite indices | Weak / Speculative | Author-built composites |
| **OH17** | ~71% decline in GOA Pacific cod abundance 2015→2017 survey | Moderate | Barbeaux et al. 2020 Frontiers; distinct from year-by-year CPUE bars |
| **OH18** | ~43% of west-coast kelp lost in Ningaloo 2011 event | Moderate | Wernberg et al. 2013/2016 |
| **OH19** | ~91% of surveyed GBR structures bleached in 2016 | Moderate | Hughes et al. 2017 Nature |
| **OH20** | This project is not affiliated with, endorsed by, or representing NOAA | Strong | Product disclaimer (must remain) |

### Open questions before lock

1. Promote OH1 to Strong after checking von Schuckmann exact percentage language?
2. Keep OH13–OH15 Weak until FOSS / AIMS tables audited, even if captions cite papers?
3. Should pipeline peaks (OH6/OH8) display dynamic values from JSON with claim id, vs hardcoded FALLBACK peaks?

---

## Change log

| Date | Change |
|------|--------|
| 2026-07-31 | Initial draft CLAIMS.md scaffolded (Tier C). No locks. |
| 2026-08-04 | UI map updated for Home / Cases / Case detail; empty Blob/GBR must not show NOAA. |
