# Corridor Governance Model — Streamlit Webapp

Participatory simulation app built around the **NetLogo Corridor Governance Model v6**
(`Nlogo_final_model.nlogox`).

Access the streamlit app: https://partenvmodgeorgia.streamlit.app/

---

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Prerequisites

### 1. NetLogo 7
Download from https://ccl.northwestern.edu/netlogo/  
Install NetLogo 7.x and note its installation directory.

### 2. Java (JDK 11+)
pyNetLogo runs NetLogo via JVM.  
Download from https://adoptium.net/

### 3. pyNetLogo
```bash
pip install pynetlogo
```

If pyNetLogo cannot auto-detect NetLogo, set the environment variable before running:
```bash
# Windows
set NETLOGO_HOME=C:\Program Files\NetLogo 7.0.0

# macOS / Linux
export NETLOGO_HOME=/Applications/NetLogo 7.0.0
```

---

## Model File Format

The model file is `Nlogo_final_model.nlogox` — the NetLogo 7 XML format.

`simulation/netlogo_runner.py` automatically extracts the code section and
creates `Nlogo_final_model.nlogo` the first time a simulation is run.
This generated `.nlogo` file is used by pyNetLogo.

---

## Project Structure

```
app.py                       Streamlit entry point
requirements.txt
README.md

simulation/
  __init__.py
  netlogo_runner.py          Single-run wrapper (pyNetLogo)
  batch_runner.py            Monte Carlo / batch runner
  indicators.py              RDM summary + Adaptive Pathways logic

data/
  default_parameters.csv     Parameter catalogue with min/max/defaults

outputs/
  .gitkeep
  batch_results.csv          Written after each Monte Carlo run
```

---

## Model Parameters

### Sliders (always active)

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `scenario` | 1–4 | 2 | Governance scenario |
| `simulation-years` | 10–50 | 30 | Simulation horizon |
| `agreement-duration` | 0–50 | 25 | Years before Sc2 agreement expires |

### Switches (Scenario 2 only)

| Switch | Default | Effect |
|--------|---------|--------|
| `rangers-in-agreement?` | ON | Ranger patrol lv2, reduces hunting |
| `compensation-enabled?` | OFF | Compensates hunting/logging income loss |
| `agreement-market-access?` | OFF | Income +0.3/yr, opportunity +0.005/yr |
| `agreement-education?` | ON | Income +0.5/yr, opportunity +0.005/yr |
| `agreement-selfsustain-incentive?` | OFF | Beekeeping/eco-tourism: income +1.5/yr |
| `agreement-marginal-loss-incentive?` | OFF | Cash transfer: income +1.0/yr |
| `agreement-action-incentive?` | OFF | Bonus per action: income +0.8/yr, action level +1 |
| `agreement-predator-compensation?` | OFF | Prevents WTA erosion from bear damage |
| `agreement-land-tenure?` | ON | WTA boost +0.10 initial, +0.02/yr |
| `agreement-grazing-reduction?` | ON | Reduces grazing, aids ungulate recovery |
| `agreement-planting?` | ON | Community planting boosts broadleaf |
| `agreement-plot-merging?` | OFF | Plot consolidation: income +0.5–5.0/yr |

---

## Scenarios

| # | Name | Description |
|---|------|-------------|
| 1 | Business as Usual | No governance; slow ecosystem degradation |
| 2 | Voluntary Agreement | Participatory agreement with configurable switches |
| 3 | State-Led Conservation | Mandatory full extraction ban from year 2 |
| 4 | Private Investment | Corridor privatised; ecosystem already degraded at start |

---

## Reporters Used

All reporters are index values (baseline = 100 at t=0) unless noted.

| Python column | NetLogo reporter | Description |
|---------------|-----------------|-------------|
| `deer_index` | `report-pop-deer` | Deer population % of start |
| `chamois_index` | `report-pop-chamois` | Chamois population % of start |
| `bear_index` | `report-pop-bear` | Brown bear population % of start |
| `broadleaf_index` | `report-pop-broadleaf` | Broadleaf forest cover % of start |
| `nontarget_index` | `report-pop-nontarget` | Non-target species % of start |
| `biodiversity_index` | `report-total-biodiversity` | Combined biodiversity index |
| `income_index` | `report-community-income` | Community income index (baseline 100) |
| `human_pop_indexed` | `report-human-pop-indexed` | Human population % of start |
| `emigration_rate` | `report-emigration-rate` | Emigration rate %/yr |
| `pct_accepted` | `report-pct-accepted` | % community accepting agreement |
| `ecosystem_status` | `report-ecosystem-status` | 0=degraded, 1=stable, 2=recovering |
| `hunt_pressure` | `report-hunt-pressure` | Average hunting pressure (0–2) |
| `predator_damage` | `report-predator-damage` | Bear damage index |
| `agreement_active` | `report-agreement-active` | 0/1 whether agreement is active |

---

## TODO — Model-Specific Adjustments

If reporter names in the NetLogo model are ever renamed, update the `REPORTERS`
dict in `simulation/netlogo_runner.py`.

The app degrades gracefully: missing reporters appear as NaN columns and are
flagged with a warning banner inside the app.

---

## Adaptive Pathway Logic

When an indicator crosses its threshold at the final simulation year, the app
displays a recommended intervention in the **Decision Support** tab:

| Indicator below threshold | Recommended action |
|--------------------------|-------------------|
| Deer population | Increase hunting restrictions; deploy rangers |
| Chamois population | Reduce grazing; restrict hunting |
| Broadleaf forest cover | Reduce logging; activate planting |
| Community income | Enable compensation and market access |
| Brown bear population | Reduce disturbance; restore forest |
| Biodiversity index | Systemic intervention; consider Sc2 or Sc3 |

---

## Files Created / Modified

- `app.py` — created
- `requirements.txt` — created
- `simulation/__init__.py` — created
- `simulation/netlogo_runner.py` — created
- `simulation/batch_runner.py` — created
- `simulation/indicators.py` — created
- `data/default_parameters.csv` — created
- `outputs/.gitkeep` — created
- `README.md` — created

The original NetLogo model (`Nlogo_final_model.nlogox`) was **not modified**.
A derived `Nlogo_final_model.nlogo` is auto-generated at runtime.
