# Corridor Governance Model — Streamlit Webapp

Interactive simulation and decision-support tool built around the
**NetLogo Corridor Governance Model v6** (`Nlogo_final_model.nlogox`),
modelling community-led conservation governance in rural Georgia.

**Live app:** https://partenvmodgeorgia.streamlit.app/

---

## What the app does

The app wraps the NetLogo ABM in a three-page Streamlit interface:

| Page | Purpose |
|------|---------|
| **Simulate** | Configure and run experiments; inspect time-series results with uncertainty bands |
| **Parameters** | Edit ecological & socioeconomic parameters; define Monte Carlo uncertainty distributions |
| **MCDA** | Multi-criteria ranking of experiments; sensitivity to weights |

Every simulation is a **Monte Carlo ensemble**: each experiment runs N times
with parameters sampled from user-defined distributions (Uniform / Normal / Triangular).
Results are displayed as **10–90 %** (outer) and **25–75 %** (inner) percentile bands
around the median.

---

## Scenarios

| ID | Label | Description |
|----|-------|-------------|
| **S1** | Business as Usual | No governance intervention; baseline ecosystem trajectory |
| **S2** | Voluntary ECF Agreement | Participatory agreement with 12 configurable policy switches |
| **S3** | State-Led Conservation | Mandatory extraction ban imposed from year 2 |
| **S4** | Private Investment | Corridor privatised; ecosystem starts degraded |

Multiple S2 variants (different switch combinations) can be built, queued, and
run simultaneously for side-by-side comparison.

### S2 policy switches

| Switch | Effect |
|--------|--------|
| Rangers in agreement | Ranger patrol lv2 — reduces hunting pressure |
| Compensation enabled | Offsets income loss from hunting/logging restrictions |
| Market access | Community income +0.3/yr, opportunity +0.005/yr |
| Education support | Community income +0.5/yr, opportunity +0.005/yr |
| Self-sustain incentive | Beekeeping / eco-tourism income +1.5/yr |
| Marginal loss incentive | Cash transfer: income +1.0/yr |
| Action incentive | Bonus per action: income +0.8/yr, action level +1 |
| Predator compensation | Prevents WTA erosion from bear damage |
| Land tenure security | WTA boost +0.10 initial, +0.02/yr |
| Grazing reduction | Reduces grazing — aids ungulate recovery |
| Community planting | Boosts broadleaf forest cover |
| Plot merging | Land consolidation: income +0.5–5.0/yr |

---

## Page guide

### Simulate

1. **Reference scenarios** — tick S1, S3, S4 to include them as baselines.
2. **Scenario 2 builder** — load a preset (Incentives / Financial / Full package…)
   or toggle switches manually. Name the variant and click **+ Add to run list**.
   Repeat to queue multiple S2 variants.
3. **Run settings** — set simulation years (10–50), agreement duration, and
   number of MC runs per experiment (3–100).
4. Click **▶ Run** — all experiments run in parallel with Monte Carlo sampling.
5. Results appear as time-series charts (6 dashboard metrics + target species).
   Use the legend to isolate scenarios; double-click to focus on one.

### Parameters

Edit the 21 ecological and socioeconomic parameters (growth rates, carrying
capacities, initial populations, baseline management).  
For each parameter you can enable **uncertainty**: choose a distribution
(Uniform, Normal, Triangular) and set its bounds — the parameter is then
sampled fresh in every MC run.

### MCDA

Requires ≥ 2 experiments from the last simulation run.

1. **Weights** (sidebar) — assign a weight 0–100 to each of the 9 criteria.
   Criteria with weight 0 are excluded.
2. **Ranking table + bar chart** — weighted-sum scores and ranks.
3. **Radar chart** — per-criterion normalised scores at a glance.
4. **Score profile** — parallel-coordinates chart showing each scenario's
   normalised score on every criterion, with MC uncertainty bands.
5. **Ranking across criteria** — bump chart: rank of each scenario per criterion,
   revealing trade-offs.
6. **Weight sensitivity** — 1 000 Dirichlet-sampled weight vectors; shows how
   often each scenario ranks #1 and #2 across random weight draws.

---

## Local setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.9+ | |
| Java JDK | 17 (recommended) | [Eclipse Temurin](https://adoptium.net/) |
| NetLogo | 7.0.3 | [netlogo.org](https://www.netlogo.org/download) |

```bash
# 1. Clone the repo
git clone https://github.com/alemaisano/PartEnvModeling_Georgia
cd PartEnvModeling_Georgia

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Point pyNetLogo at your NetLogo installation (Linux / macOS)
export NETLOGO_HOME="/path/to/NetLogo 7.0.3"

# 4. Run
streamlit run app.py
```

On **Windows**, `NETLOGO_HOME` is auto-detected from the registry if NetLogo 7
is installed normally. On **Linux**, the app will attempt to download NetLogo
automatically on first run if `NETLOGO_HOME` is not set.

---

## Streamlit Cloud deployment

The repo includes `packages.txt` (installs `openjdk-17-jdk`) and automatic
NetLogo 7.0.3 download on cold start.  
Optional: set `NETLOGO_HOME` in **App settings → Secrets** to skip the download.

---

## Project structure

```
app.py                     Streamlit entry point (all pages)
requirements.txt
packages.txt               apt packages for Streamlit Cloud (Java)
README.md

simulation/
  netlogo_runner.py        Single-run wrapper (pyNetLogo + Java setup)
  batch_runner.py          Monte Carlo / batch runner
  indicators.py            RDM + Adaptive Pathways logic (reference)

Nlogo_final_model.nlogox   NetLogo 7 XML model (not modified by app)
```

---

## Output metrics

All values are indices (baseline = 100 at t = 0) unless noted.

| Column | NetLogo reporter | Description |
|--------|-----------------|-------------|
| `pct_accepted` | `report-pct-accepted` | % community accepting agreement |
| `income_index` | `report-community-income` | Community income index |
| `biodiversity_index` | `report-total-biodiversity` | Combined biodiversity index |
| `emigration_rate` | `report-emigration-rate` | Emigration rate %/yr |
| `human_pop_indexed` | `report-human-pop-indexed` | Human population % of start |
| `ecosystem_status` | `report-ecosystem-status` | 0 = degraded · 1 = stable · 2 = recovering |
| `deer_index` | `report-pop-deer` | Deer population % of start |
| `chamois_index` | `report-pop-chamois` | Chamois population % of start |
| `bear_index` | `report-pop-bear` | Brown bear population % of start |
| `broadleaf_index` | `report-pop-broadleaf` | Broadleaf forest cover % of start |
| `nontarget_index` | `report-pop-nontarget` | Non-target species % of start |
