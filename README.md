# Ocean Heating: Events and Impacts

Long-term ocean warming, marine heatwaves, and ecosystem consequences built as a single deployable HTML file with D3.js. 

Live: [saraxlinnea.github.io/ocean-heat-stress](https://saraxlinnea.github.io/ocean-heat-stress)

> **Disclaimer:** Independent science communication project by Sara Bower. Uses public NOAA data and published literature. Not affiliated with, endorsed by, or representing the views of NOAA or any U.S. government agency.

---

## What it shows

Ocean heat stress is not one number. It is a long-term warming trend, marine heatwave events layered on top of that trend, and the biological damage those events cause when they cross ecological thresholds. The dashboard tracks all three layers across five case studies.

**2014–2016 Pacific Blob, Gulf of Alaska.** A persistent high-pressure ridge suppressed wind mixing across the Northeast Pacific for nearly three years. SSTs exceeded the 90th percentile baseline by up to 2.5°C. The 2017 AFSC bottom trawl survey documented a 71% decline in Pacific cod abundance relative to the 2015 survey (Barbeaux et al. 2020). The fishery closed in 2020, the first closure in its history. In the Bering Sea, a connected heatwave in 2018–19 drove the starvation-related disappearance of more than 10 billion snow crab (Szuwalski et al. 2023).

**2016 and 2024 GBR bleaching events.** The 2016 event bleached 91% of surveyed Great Barrier Reef structures, with the northern reef — the most remote and least disturbed — hit hardest. In April 2024, NOAA confirmed the fourth global coral bleaching event, the largest on record. The interval between severe bleaching events has collapsed from roughly a decade in the 1980s to near-annual since 2016.

**2011 Ningaloo Niña (Western Australia kelp collapse)** 

**2015–16 Tasman Sea heatwave** 

**2023 NE Atlantic basin-scale event**

---

## Data sources

| Dataset | Source | Used in dashboard |
|---|---|---|
| NOAA OISST v2.1 | NOAA NCEI via ERDDAP | Hero chart (global), Gulf of Alaska & GBR case studies (when pipeline has run) |
| NOAAGlobalTemp v6 ocean annual | NOAA NCEI direct ASCII | Hero chart (1880–present) |
| Hobday MHW detection | `marineHeatWaves` Python package | Gulf of Alaska & GBR MHW bands |
| Pacific cod CPUE | Barbeaux et al. 2020; AFSC GAP via NOAA FOSS | Blob ecosystem chart (literature-transcribed values) |
| Snow crab abundance | Szuwalski et al. 2023 *Science* | Blob ecosystem chart (approximate index, unverified year-by-year) |
| GBR bleaching extent | Hughes et al. 2017 *Nature*; AIMS LTMP; NOAA CRW | GBR ecosystem chart (literature-transcribed values) |
| Ningaloo / Tasman / NE Atlantic SST | Published literature | Illustrative monthly series (not yet pipelined) |

NOAA Coral Reef Watch `mhw_5km` is listed in the resources panel as a related product; this project computes MHWs from OISST directly.

---

## Baselines

**Global hero chart:** NOAAGlobalTemp v6 (ERSSTv6 ocean) and OISST v2.1 global annual anomalies each use NOAA's native **1971–2000** baseline. The two lines are shown separately from 1981 onward so the shift from reconstruction to satellite-era observing is visible.

**Gulf of Alaska and Great Barrier Reef:** Monthly SST anomalies and Hobday MHW detection use a **1991–2020** climatology (WMO 30-year normal), computed from raw OISST `sst` in the preprocessing script.

**Other case studies:** Illustrative monthly SST series derived from published literature.

---

## Marine heatwave definition

This dashboard applies the Hobday et al. 2016 standard: a marine heatwave is a period when SST exceeds the locally and seasonally varying 90th percentile of the 1991–2020 climatological baseline for at least 5 consecutive days. The 90th percentile is computed for each calendar day using an 11-day window, then smoothed with a 31-day running mean. Intensity categories follow the Hobday taxonomy.

---

## Running the data pipeline

The dashboard loads pre-computed JSON from `./data/`. A GitHub Actions workflow (`.github/workflows/update-data.yml`) refreshes this data nightly from NOAA. To run it locally:

```bash
pip install requests pandas numpy scipy
pip install git+https://github.com/ecjoliver/marineHeatWaves.git
python ohsi_preprocessing.py
```

The script fetches the NOAAGlobalTemp ocean annual series directly from NCEI, pulls OISST from ERDDAP for the two NOAA-backed case study regions and globally, runs Hobday MHW detection, and writes eight JSON files to `./data/`. First run takes 5–10 minutes depending on ERDDAP response time.

If the NOAA file returns a 404, the filename has been updated. Check the directory at `ncei.noaa.gov/data/noaa-global-surface-temperature/v6/access/timeseries/` and update `NOAA_OCEAN_FILE` at the top of the script.

### Methods notebook

For step-by-step exploration and sanity-check plots, open [`notebooks/methods.ipynb`](notebooks/methods.ipynb) in Jupyter Lab or VS Code. It reads the same `./data/` JSON the dashboard uses. Install extras: `pip install matplotlib jupyter`.

---

## Key citations

- Hobday et al. (2016). A hierarchical approach to defining marine heatwaves. *Progress in Oceanography*, 141, 227–238. https://doi.org/10.1016/j.pocean.2015.12.014
- Bond et al. (2015). Causes and impacts of the 2014 warm anomaly in the NE Pacific. *GRL*, 42, 3414–3420. https://doi.org/10.1002/2015GL063306
- Barbeaux, Holsman & Zador (2020). Marine heatwave stress test of ecosystem-based fisheries management in the Gulf of Alaska Pacific cod fishery. *Frontiers in Marine Science*, 7, 703. https://doi.org/10.3389/fmars.2020.00703
- Hughes et al. (2017). Global warming and recurrent mass bleaching of corals. *Nature*, 543, 373–377. https://doi.org/10.1038/nature21707
- Szuwalski et al. (2023). The collapse of eastern Bering Sea snow crab. *Science*, 382, 306–310. https://doi.org/10.1126/science.adf6035
- Cheung & Frölicher (2020). Marine heatwaves exacerbate climate change impacts for fisheries in the northeast Pacific. *Scientific Reports*, 10, 6678. https://doi.org/10.1038/s41598-020-63650-z

---

## Background

Built by Sara Bower. B.S. Global Environmental Science, University of Hawaiʻi at Mānoa. 

---

## License

MIT. See LICENSE. Data sources are public domain (NOAA) or cited from published literature and not reproduced here.
