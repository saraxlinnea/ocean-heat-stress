#!/usr/bin/env python3
"""
Ocean Heating — Data Preprocessing
saraxlinnea.github.io/ocean-heat-stress

Fetches data from NOAA and writes static JSON for the dashboard.
Designed to run unattended in GitHub Actions (see .github/workflows/update-data.yml).
Your local machine does not need to stay on after you start it.

WHAT THIS SCRIPT DOES:
  1. Fetches the NOAAGlobalTemp v6 ocean annual anomaly series (1880-present)
     directly from NCEI as a plain text file.
  2. Fetches OISST v2.1 global annual mean anomaly (1981-present) from ERDDAP,
     as a second independent satellite-era series.
  3. Fetches regional SST for the two case study regions (Gulf of Alaska, GBR)
     and runs Hobday et al. 2016 marine heatwave detection.
  4. Writes everything to ./data/ as JSON for the dashboard to read.

DATA SOURCES:
  NOAAGlobalTemp v6:  ncei.noaa.gov (direct ASCII, no auth)
  OISST v2.1:        coastwatch.pfeg.noaa.gov/erddap (no auth)
  marineHeatWaves:   github.com/ecjoliver/marineHeatWaves

USAGE:
  pip install requests pandas numpy scipy
  pip install git+https://github.com/ecjoliver/marineHeatWaves.git
  python ohsi_preprocessing.py

OUTPUTS (written to ./data/):
  global_ersst.json    NOAAGlobalTemp ocean annual anomaly 1880-present
  global_oisst.json    OISST v2.1 global annual anomaly 1981-present
  blob_sst.json        Monthly SST anomaly, Gulf of Alaska
  gbr_sst.json         Monthly SST anomaly, Great Barrier Reef
  blob_mhw.json        MHW events (Hobday), Gulf of Alaska
  gbr_mhw.json         MHW events (Hobday), Great Barrier Reef
  ecosystem.json       Survey-based ecosystem stress series
  meta.json            Run timestamp, provenance, method flags
"""

import os
import json
import re
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from io import StringIO

# ── CONFIGURATION ─────────────────────────────────────────────────────────────

OUT_DIR = "data"

# NOAAGlobalTemp v6 ocean-only annual anomaly
# File format: year | anomaly | upper_error | lower_error
# Anomalies relative to 1971-2000 baseline (native to ERSSTv6)
# URL pattern: version is v6.0.0, filename ends in YYYYMM of last update
NOAA_GLOBALTEMP_BASE = (
    "https://www.ncei.noaa.gov/data/noaa-global-surface-temperature"
    "/v6/access/timeseries/"
)
NOAA_OCEAN_FILE = "aravg.ann.ocean.90S.90N.v6.0.0.202512.asc"
# If this 404s, the file was updated. Check the directory index at:
# https://www.ncei.noaa.gov/data/noaa-global-surface-temperature/v6/access/timeseries/
# and update the filename above to the most recent aravg.ann.ocean.* file.

# OISST v2.1 global mean via ERDDAP
# We pull the native `anom` field globally, then area-weight to get a
# single annual mean. This is the satellite-era independent line.
ERDDAP_BASE   = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"
OISST_DATASET = "ncdcOisst21Agg_LonPM180"

# Hobday et al. 2016 parameters (used for regional case studies)
CLIM_START   = 1991
CLIM_END     = 2020
MHW_PCTILE   = 90
MHW_MIN_DAYS = 5
MHW_WINDOW   = 5
MHW_SMOOTH   = 31

# Case study regions
REGIONS = {
    "blob": {
        "name": "Gulf of Alaska",
        "lon": (-165, -130),
        "lat": (50, 62),
        "date_start": "1991-01-01",
        "date_end":   "2019-12-31",
    },
    "gbr": {
        "name": "Great Barrier Reef",
        "lon": (142, 154),
        "lat": (-25, -10),
        "date_start": "1991-01-01",
        "date_end":   "2024-12-31",
    },
}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def save(data, filename):
    """Write data as indented JSON to OUT_DIR/filename."""
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"    saved {path}")
    return path


def get(url, timeout=120, **kwargs):
    """HTTP GET with a readable error if it fails."""
    resp = requests.get(url, timeout=timeout, **kwargs)
    resp.raise_for_status()
    return resp


# ── GLOBAL SERIES: NOAAGlobalTemp ERSSTv6 ─────────────────────────────────────

def fetch_noaa_globaltemp():
    """
    Fetch the NOAAGlobalTemp v6 ocean annual anomaly ASCII file from NCEI.

    File format (space-delimited, no header):
        year   anomaly_C   upper_1sigma   lower_1sigma

    Anomalies are relative to the 1971-2000 baseline, which is the native
    baseline of ERSSTv6. We do NOT re-baseline here; we report the values
    as published and note the baseline on the chart.

    Returns list of {year, anom} dicts covering 1880-present.
    """
    url = NOAA_GLOBALTEMP_BASE + NOAA_OCEAN_FILE
    print(f"  Fetching NOAAGlobalTemp ocean series...")
    print(f"    {url}")

    try:
        resp = get(url, timeout=60)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"    404: file may have been updated. Check the directory:")
            print(f"    {NOAA_GLOBALTEMP_BASE}")
            print(f"    Update NOAA_OCEAN_FILE in this script to the latest")
            print(f"    aravg.ann.ocean.90S.90N.v6* filename.")
        raise

    records = []
    for line in resp.text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            year  = int(float(parts[0]))
            anom  = round(float(parts[1]), 3)
            records.append({"year": year, "anom": anom})
        except ValueError:
            continue

    if not records:
        raise ValueError("NOAAGlobalTemp file parsed to zero records — check format")

    print(f"    {len(records)} years, {records[0]['year']} to {records[-1]['year']}")
    print(f"    Baseline: 1971-2000 (native ERSSTv6)")
    print(f"    Most recent year anomaly: +{records[-1]['anom']}°C")
    return records


# ── GLOBAL SERIES: OISST v2.1 satellite-era ───────────────────────────────────

def fetch_oisst_global_annual():
    """
    Fetch global OISST v2.1 anomaly from ERDDAP and derive annual means.

    We use a coarse spatial stride (stride=8, ~2 degree cells) to keep
    the request size manageable. Area-weighted with cos(lat).

    This gives us the satellite-only line starting in 1981, which uses
    a denser and more spatially complete observing system than the
    pre-satellite ERSSTv6 reconstruction.

    Returns list of {year, anom} dicts covering 1981-present.
    """
    print(f"  Fetching OISST v2.1 global annual series...")

    # Fetch annual-ish: one reading per month globally, stride=8 spatially
    # We fetch the `anom` field which NOAA computes against 1971-2000
    end_year = datetime.now(timezone.utc).year
    end_date = f"{end_year}-12-15T12:00:00Z"
    url = (
        f"{ERDDAP_BASE}/{OISST_DATASET}.csv"
        f"?anom[(1981-01-15T12:00:00Z):365:({end_date})]"
        f"[0][(-89.875):8:(89.875)][(-179.875):8:(179.875)]"
    )
    print(f"    {url[:80]}...")

    try:
        resp = get(url, timeout=300)
    except requests.exceptions.RequestException as e:
        print(f"    ERDDAP fetch failed: {e}")
        print(f"    Skipping OISST global series — dashboard uses ERSSTv6 only.")
        return None

    # ERDDAP CSV: row 0 = col names, row 1 = units, row 2+ = data
    lines = resp.text.split("\n")
    data_lines = [lines[0]] + [l for l in lines[2:] if l.strip()]
    df = pd.read_csv(StringIO("\n".join(data_lines)))
    df.columns = [c.strip() for c in df.columns]
    df["time"] = pd.to_datetime(df["time"])
    df["anom"] = pd.to_numeric(df["anom"], errors="coerce")
    df = df.dropna(subset=["anom"])

    # Area-weight by cos(latitude)
    df["w"] = np.cos(np.radians(df["latitude"]))
    daily = (df.groupby("time")
               .apply(lambda x: np.average(x["anom"], weights=x["w"]))
               .reset_index())
    daily.columns = ["date", "anom"]
    daily["year"] = daily["date"].dt.year

    annual = (daily.groupby("year")["anom"]
                   .mean()
                   .reset_index())
    annual["anom"] = annual["anom"].round(3)

    records = [{"year": int(r["year"]), "anom": float(r["anom"])}
               for _, r in annual.iterrows()]

    print(f"    {len(records)} years, {records[0]['year']} to {records[-1]['year']}")
    print(f"    Baseline: 1971-2000 (native OISST anom field)")
    return records


# ── REGIONAL SST + MHW ────────────────────────────────────────────────────────

def build_erddap_url(key, stride=4):
    r = REGIONS[key]
    lon0, lon1 = r["lon"]
    lat0, lat1 = r["lat"]
    t0, t1 = r["date_start"], r["date_end"]
    return (
        f"{ERDDAP_BASE}/{OISST_DATASET}.csv"
        f"?sst[({t0}T12:00:00Z):1:({t1}T12:00:00Z)]"
        f"[0][({lat0}):{stride}:({lat1})]"
        f"[({lon0}):{stride}:({lon1})]"
    )


def fetch_regional_sst(key):
    url = build_erddap_url(key)
    print(f"  Fetching regional SST: {REGIONS[key]['name']}...")
    print(f"    {url[:80]}...")
    try:
        resp = get(url, timeout=300)
    except requests.exceptions.RequestException as e:
        print(f"    ERROR: {e}")
        print(f"    Backup: CMEMS (marine.copernicus.eu)")
        return None

    lines = resp.text.split("\n")
    data_lines = [lines[0]] + [l for l in lines[2:] if l.strip()]
    df = pd.read_csv(StringIO("\n".join(data_lines)))
    df.columns = [c.strip() for c in df.columns]
    df["time"] = pd.to_datetime(df["time"])
    df["sst"] = pd.to_numeric(df["sst"], errors="coerce")
    df = df.dropna(subset=["sst"])
    print(f"    Got {len(df):,} grid-cell-days")
    return df


def spatial_average(df):
    df = df.copy()
    df["w"] = np.cos(np.radians(df["latitude"]))
    out = (df.groupby("time")
             .apply(lambda x: np.average(x["sst"], weights=x["w"]))
             .reset_index())
    out.columns = ["date", "sst"]
    return out


def detect_mhw(daily_df):
    try:
        import marineHeatWaves as mhw
    except ImportError:
        print("    marineHeatWaves not installed — using simplified fallback")
        return detect_mhw_simple(daily_df), None

    t     = daily_df["date"].values
    sst   = daily_df["sst"].values
    t_ord = np.array([pd.Timestamp(d).toordinal() for d in t])

    mhws, clim = mhw.detect(
        t_ord, sst,
        climatologyPeriod=[CLIM_START, CLIM_END],
        pctile=MHW_PCTILE,
        windowHalfWidth=MHW_WINDOW,
        smoothPercentileWidth=MHW_SMOOTH,
        minDuration=MHW_MIN_DAYS,
    )
    cats  = {1: "Moderate", 2: "Strong", 3: "Severe", 4: "Extreme"}
    events = []
    for i in range(len(mhws["time_start"])):
        cn = int(mhws["category"][i]) if "category" in mhws else None
        events.append({
            "start":          str(pd.Timestamp.fromordinal(int(mhws["time_start"][i])))[:10],
            "end":            str(pd.Timestamp.fromordinal(int(mhws["time_end"][i])))[:10],
            "peak_date":      str(pd.Timestamp.fromordinal(int(mhws["time_peak"][i])))[:10],
            "peak_intensity": round(float(mhws["intensity_max"][i]), 2),
            "mean_intensity": round(float(mhws["intensity_mean"][i]), 2),
            "duration_days":  int(mhws["duration"][i]),
            "category":       cn,
            "category_name":  cats.get(cn),
        })
    return events, clim


def detect_mhw_simple(daily_df):
    df  = daily_df.copy().reset_index(drop=True)
    thr = np.nanpercentile(df["sst"].values, MHW_PCTILE)
    df["above"] = df["sst"] > thr
    events, in_evt, s = [], False, None
    for i, row in df.iterrows():
        if row["above"] and not in_evt:
            in_evt, s = True, i
        elif not row["above"] and in_evt:
            if i - s >= MHW_MIN_DAYS:
                seg = df.iloc[s:i]
                pk  = seg["sst"].idxmax()
                events.append({
                    "start":          str(df.iloc[s]["date"])[:10],
                    "end":            str(df.iloc[i-1]["date"])[:10],
                    "peak_date":      str(df.iloc[pk]["date"])[:10],
                    "peak_intensity": round(float(seg["sst"].max() - seg["sst"].mean()), 2),
                    "mean_intensity": None,
                    "duration_days":  int(i - s),
                    "category":       None,
                    "category_name":  None,
                })
            in_evt = False
    return events


def monthly_anomaly(daily_df, clim):
    df = daily_df.copy()
    if clim is not None and "seas" in clim:
        df["anom"] = df["sst"].values - clim["seas"]
    else:
        df["anom"] = df["sst"] - df["sst"].mean()
    m = (df.set_index("date")["anom"]
           .resample("MS").mean()
           .reset_index())
    m.columns = ["date", "anom"]
    m["anom"]  = m["anom"].round(2)
    return [{"date": str(r["date"])[:10], "anom": float(r["anom"])}
            for _, r in m.iterrows()]


# ── ECOSYSTEM DATA (survey-based, hardcoded from literature) ──────────────────

ECOSYSTEM = {
    "blob_cod": {
        "label":    "Pacific cod CPUE",
        "unit":     "CPUE (kg/ha)",
        "source":   "Barbeaux et al. 2020 Frontiers in Marine Science; AFSC GAP via NOAA FOSS",
        "verified": False,
        "note":     "71% decline (2015–2017 survey) per Barbeaux et al. 2020. Year-by-year CPUE transcribed from literature, not FOSS.",
        "series":   [
            {"year": 2001, "v": 14.2}, {"year": 2003, "v": 16.8},
            {"year": 2005, "v": 18.1}, {"year": 2007, "v": 17.4},
            {"year": 2009, "v": 19.2}, {"year": 2011, "v": 21.3},
            {"year": 2013, "v": 22.7}, {"year": 2015, "v": 18.4},
            {"year": 2017, "v":  6.5}, {"year": 2019, "v":  4.1},
            {"year": 2021, "v":  5.2}, {"year": 2023, "v":  7.8},
        ],
        "annotations": [
            {"year": 2018, "v": 6.5, "label": "-58% ACL"},
            {"year": 2020, "v": 4.1, "label": "Closure"},
        ],
    },
    "blob_crab": {
        "label":    "EBS snow crab abundance",
        "unit":     "Abundance index (relative, 2018=100)",
        "source":   "Szuwalski et al. 2023 Science (NEEDS PRIMARY-SOURCE VERIFICATION)",
        "verified": False,
        "note":     (
            "Relative index, 2018=100. The widely cited figure is ~10 billion "
            "crab lost 2018-2021, attributed to heatwave-driven starvation. "
            "Absolute figures pending verification against the Science abstract."
        ),
        "series":   [
            {"year": 2015, "v": 62}, {"year": 2016, "v": 71},
            {"year": 2017, "v": 88}, {"year": 2018, "v": 100},
            {"year": 2019, "v": 54}, {"year": 2021, "v":   9},
            {"year": 2022, "v": 11}, {"year": 2023, "v":  14},
        ],
        "annotations": [
            {"year": 2018, "v": 100, "label": "Peak"},
            {"year": 2021, "v":   9, "label": "Collapse"},
        ],
    },
    "gbr_bleach": {
        "label":    "GBR bleaching extent",
        "unit":     "% of surveyed reefs affected",
        "source":   "Hughes et al. 2017 Nature; AIMS LTMP; NOAA CRW 2024",
        "verified": False,
        "note":     "Bleaching extent values transcribed from published surveys and CRW reports.",
        "series":   [
            {"year": 2002, "v": 54}, {"year": 2006, "v": 18},
            {"year": 2008, "v":  5}, {"year": 2010, "v": 27},
            {"year": 2011, "v":  1}, {"year": 2016, "v": 91},
            {"year": 2017, "v": 65}, {"year": 2020, "v": 25},
            {"year": 2022, "v": 91}, {"year": 2024, "v": 98},
        ],
        "annotations": [
            {"year": 2016, "v": 91, "label": "Alert Lvl 2"},
            {"year": 2024, "v": 98, "label": "4th Global"},
        ],
    },
}


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Ocean Heating — Preprocessing")
    print("=" * 52)
    ts = datetime.now(timezone.utc).isoformat()
    print(f"Run UTC: {ts}\n")

    meta = {
        "generated_utc":         ts,
        "oisst_dataset":         f"{ERDDAP_BASE}/{OISST_DATASET}",
        "noaa_globaltemp_file":  NOAA_GLOBALTEMP_BASE + NOAA_OCEAN_FILE,
        "climatology_baseline":  f"{CLIM_START}-{CLIM_END}",
        "ersst_baseline":        "1971-2000 (native ERSSTv6)",
        "oisst_baseline":        "1971-2000 (native OISST anom field)",
        "mhw_definition": (
            "Hobday et al. 2016: SST above the seasonally varying 90th "
            "percentile (11-day window, 31-day smoothing) for >= 5 "
            "consecutive days."
        ),
        "oisst_latency_days": 14,
        "regions": {},
        "method":  "hobday",
    }

    # ── Step 1: Global series ──────────────────────────────────────────────
    print("[GLOBAL] Long-term ocean warming series")
    print("-" * 40)
    try:
        ersst = fetch_noaa_globaltemp()
        save(ersst, "global_ersst.json")
        meta["ersst_years"] = f"{ersst[0]['year']}-{ersst[-1]['year']}"
        meta["ersst_status"] = "ok"
    except Exception as e:
        print(f"  ERSSTv6 fetch failed: {e}")
        meta["ersst_status"] = "failed"
    print()

    oisst_global = fetch_oisst_global_annual()
    if oisst_global:
        save(oisst_global, "global_oisst.json")
        meta["oisst_global_years"] = f"{oisst_global[0]['year']}-{oisst_global[-1]['year']}"
        meta["oisst_global_status"] = "ok"
    else:
        meta["oisst_global_status"] = "failed"
    print()

    # ── Step 2: Regional case studies ─────────────────────────────────────
    for key, region in REGIONS.items():
        print(f"[{key.upper()}] {region['name']}")
        print("-" * 40)

        raw = fetch_regional_sst(key)
        if raw is None:
            meta["regions"][key] = {"status": "fetch_failed"}
            continue

        daily  = spatial_average(raw)
        result = detect_mhw(daily)

        if isinstance(result, tuple):
            events, clim = result
        else:
            events, clim = result, None
            meta["method"] = "simplified"

        print(f"  MHW events detected: {len(events)}")
        for e in events[:6]:
            cat = f" [{e['category_name']}]" if e.get("category_name") else ""
            print(f"    {e['start']} to {e['end']}  "
                  f"+{e['peak_intensity']}°C  {e['duration_days']}d{cat}")

        monthly = monthly_anomaly(daily, clim)
        save(monthly, f"{key}_sst.json")
        save(events,  f"{key}_mhw.json")

        meta["regions"][key] = {
            "name":     region["name"],
            "lon":      region["lon"],
            "lat":      region["lat"],
            "n_events": len(events),
            "status":   "ok",
        }
        print()

    # ── Step 3: Ecosystem (static) ─────────────────────────────────────────
    save(ECOSYSTEM, "ecosystem.json")

    # ── Step 4: Metadata ───────────────────────────────────────────────────
    save(meta, "meta.json")

    # ── Summary ────────────────────────────────────────────────────────────
    print()
    print("Done.")
    unverified = [k for k, v in ECOSYSTEM.items() if not v.get("verified")]
    if unverified:
        print()
        print("UNVERIFIED data (do not present as fact):")
        for k in unverified:
            print(f"  {k}: {ECOSYSTEM[k]['source']}")


if __name__ == "__main__":
    main()
