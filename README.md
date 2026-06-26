# Corridor Governance Model — Streamlit Webapp

Interactive simulation and decision-support tool built around the
**NetLogo Corridor Governance Model v6** (`Nlogo_final_model.nlogox`),
modelling community-led conservation governance in rural Georgia (South Caucasus).

**Live app:** https://partenvmodgeorgia.streamlit.app/

> **Important:** This model is an exploratory scenario-comparison tool, not a forecast.
> Parameters classified as exploratory assumptions (marked below) should be varied
> in sensitivity analysis before interpreting differences between scenarios.

---

## What the app does

| Page | Purpose |
|------|---------|
| **Simulate** | Configure and run experiments; inspect time-series results with uncertainty bands |
| **Parameters** | Edit ecological & socioeconomic parameters; define Monte Carlo uncertainty distributions |
| **MCDA** | Multi-criteria ranking of experiments; sensitivity to weights |

Every simulation is a **Monte Carlo ensemble**: each experiment runs N times with parameters
sampled from user-defined distributions (Uniform / Normal / Triangular).
Results are displayed as 10–90 % (outer) and 25–75 % (inner) percentile bands around the median.

---

## Scenarios

| ID | Label | Description |
|----|-------|-------------|
| **S1** | Business as Usual | No governance intervention; baseline ecosystem trajectory |
| **S2** | Voluntary ECF Agreement | Participatory agreement with 12 configurable policy switches |
| **S3** | State-Led Conservation | Mandatory extraction ban imposed from year 2 |
| **S4** | Private Investment | Corridor privatised; ecosystem degrades gradually (1 %/yr) |

All scenarios start from **identical** ecological and demographic initial conditions.
Differences emerge only after governance conditions are applied.

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
| Land tenure security | WTA boost +0.10 at initialisation (one-time) |
| Grazing reduction | Reduces grazing — aids ungulate recovery |
| Community planting | Boosts broadleaf forest cover |
| Plot merging | Land consolidation: income +0.5–5.0/yr |

---

## Page guide

### Simulate

1. **Reference scenarios** — tick S1, S3, S4 to include them as baselines.
2. **Scenario 2 builder** — load a preset or toggle switches manually. Name the variant and click **+ Add to run list**.
3. **Run settings** — set simulation years (10–50), agreement duration (default 10 yrs per ECF programme), and MC runs (3–100).
4. Click **▶ Run** — all experiments run with Monte Carlo sampling.
5. Results appear as time-series charts (6 dashboard metrics + target species).

### Parameters

Edit ecological, agent-behaviour, and income-model parameters.
Enable **Uncertain?** on any parameter to sample it from a distribution in every MC run.
Agent-behaviour params are sampled before setup; income coefficients are applied after setup.

### MCDA

Requires ≥ 2 experiments. Assign weights (auto-renormalized to 100) to 9 criteria.
Charts: weighted ranking · radar · score profile per criterion · ranking across criteria ·
Dirichlet weight sensitivity · per-criterion weight sweep showing how score changes as
each criterion's weight varies 0–100 %.

---

## Model parameterisation and data sources

Parameters follow a four-level evidence hierarchy:
**L** = direct local/case-study evidence · **R** = Georgian/Caucasus regional ·
**X** = external transferable experience · **H** = heuristic/modelling assumption.

Parameters classified as **H** are exploratory; their magnitudes should be varied in sensitivity analysis.

### Demographic parameters

| Parameter | Value | Evidence | Source / rationale |
|-----------|-------|----------|--------------------|
| Net natural population change | −0.003/yr | R/L | 2024 Georgian census: Khulo −3.5 %/yr, Shuakhevi −3.0 %/yr compound (2014–2024) |
| Baseline emigration prob. (μ) | 0.030 | R/L | Calibrated so BAU produces ≈3–3.5 %/yr total decline matching mountain municipalities |
| Baseline emigration SD | 0.020 | H | Heuristic; captures heterogeneity in mobility and rooting factors |
| WTA mean | 0.45 | H | Heuristic prior; local survey data needed for calibration |
| WTA SD | 0.15 | H | 0.15 limits clamping artefacts; 0.20 produced unrealistic boundary accumulation |

**BAU calibration target:** Khulo and Shuakhevi municipalities showed compound annual population declines of approximately 3.5 % and 3.0 % between the 2014 and 2024 national censuses (Geostat 2024 Population Census, Georgia).

### Ecological parameters

| Species | Initial pop. | K | r (central) | Sensitivity range | Evidence |
|---------|-------------|---|-------------|------------------|---------|
| Red deer | 400 | 1 200 | 0.07 | 0.04–0.11 | L / R / X |
| Chamois | 200 (proxy) | 600 | 0.06 | 0.03–0.10 | L / R / X |
| Brown bear | 40 | 80 | 0.04 | 0.02–0.05 | L / X |
| Broadleaf forest | 100 (index) | 150 | 0.01 | 0.005–0.03 | R / X |
| Non-target biodiversity | 100 (index) | 150 | 0.04 | 0.02–0.06 | H |

**Red deer — 400 individuals, K = 1 200, r = 0.07 [L/R/X]**
Initial population consistent with survey estimates of 325–527 individuals in and around
Borjomi-Kharagauli National Park (NACRES/WWF habitat and species mapping, Western Lesser Caucasus).
Growth rate calibrated from a Caspian red-deer population under successful conservation
showing an observed net trend of ≈2.2 %/yr (Salmanpour et al. 2025, *Population Dynamics and
Ecology of the Caspian Red Deer*, PMC12276821). Note: observed net trend ≠ intrinsic r;
the logistic model's r is the biological potential before mortality and density dependence.

**Chamois — 200 proxy, K = 600, r = 0.06 [L/R/X]**
No reliable corridor-specific abundance estimate; 200 is a scaled proxy informed by wider
Lesser Caucasus estimates (NACRES/WWF). Treated as highly uncertain; varied in sensitivity analysis.

**Brown bear — 40 individuals, K = 80, r = 0.04 [L/X]**
Initial population defensible from locally reported density of 1.9–2.3 bears/100 km² in
Borjomi-Kharagauli (NACRES/WWF) applied to the priority-site network area (≈1 965 km²).
K = 80 ≈ 4.1 bears/100 km²; previous K = 120 implied ≈6.1/100 km², roughly three times
local density. Growth rate based on recovering European brown bear populations (≈4–5 %/yr;
Swenson et al., *Monitoring and Management of the Swedish Brown Bear*, SLU, epsilon.slu.se/201058.pdf).

**Broadleaf forest — index baseline 100, K = 150, r = 0.01 [R/X]**
Modelled as a habitat-quality composite index, not a literal tree count.
r = 0.01 for area change (FAO *Global Forest Resources Assessment 2025*, openknowledge.fao.org).
K = 150 implies 50 % improvement over baseline; K = 200 would imply doubling (policy aspiration, not baseline).

**Biodiversity index [H]**
Equally weighted normalised: each of the five components contributes 20 % regardless of
absolute population size. The previous raw-sum index allowed deer to determine 47 % and
bear only 5 % of the total, making trade-offs invisible.
Baseline = 100; ecosystem status: Low < 80, Medium 80–120, High > 120 (test 75/125 and 90/110).
Ecosystem-status growth modifier is **multiplicative** (×0.90/1.00/1.10), not additive.
Previous ±0.05 additive to r was not equivalent to ±5 %: for bears (r = 0.04) it produced ±125 % effect.

### Pressure parameters [H informed by L/X]

Local evidence supports the direction of threats (hunting, logging, grazing, disturbance);
exact annual removal percentages are not documented (NACRES/WWF threat assessment).

| Intensity level | Hunting mortality | Logging mortality | Agricultural pressure |
|-----------------|------------------|------------------|-----------------------|
| 0 — none (ban) | 0.0 % | 0.0 % | 0.0 % |
| 1 — low (subsistence) | 2.0 % | 0.5 % | 1.5 % |
| 2 — medium (BAU) | 5.0 % | 2.0 % | 4.0 % |
| High (stress test) | 12.0 % | 6.0 % | — |

Previous intensity = 0 still produced 3 % hunting and 1 % logging mortality, making
the S3 protected-area ecological model internally inconsistent.

**Patrol effectiveness** uses multiplicative residual-pressure multipliers:
None ×1.00, Low ×0.90, Medium ×0.60, High ×0.30 (proxy; test ±20 pp).
Evidence supports deterrence effects of strategically allocated patrol effort;
effects vary with accessibility, spatial allocation, and offender displacement
(Critchlow et al. 2022, *Conservation Science and Practice*, DOI:10.1111/csp2.12746).
Non-spatial model limitations are explicitly acknowledged.

### Conservation agreement parameters [L / X / H]

**Agreement duration: 10 years** (ECF programme default; Eco Corridor Foundation,
ecocorridorscaucasus.org). Previous default of 25 years was inconsistent with the
documented 10-year conservation agreement structure.

WTA adjustment **directions** are supported by the conservation contract literature;
**exact magnitudes are exploratory**. Compensation, tenure, obligations, duration and
flexibility all influence participation (Greiner 2015, *Agricultural Systems* 137:154–165,
ideas.repec.org/a/eee/agisys/v137y2015). Tenure security supports stable participation
(*Ecology and Society* 28(1):13, ecologyandsociety.org).
All WTA coefficients should be varied ±50 % in sensitivity analysis.

**Land tenure:** one-time WTA boost at initialisation (+0.10 one-time).
Previous cumulative +0.02/yr annual increase had no empirical upper bound and no
evidence basis for continued annual accumulation.

**Private investor in S2 removed.** Previous model introduced an investor randomly
(p = 0.6), causing identical S2 runs to produce systematically different results.
Market-access and private-collaboration benefits are exposed as explicit switches.

### Privatisation scenario (S4) [H]

All scenarios now start from identical ecological conditions.
Previous S4 reduced species populations by 40–50 % at setup, predetermining the result.
Habitat degradation: 1 %/yr central estimate; 6 %/yr retained as extreme stress test only.
Emigration pressure arises from livelihood loss and ecosystem effects,
not a separate ×2.0 scenario multiplier (double-counting removed).

### Protected area scenario (S3)

Modelled as idealised strict protection with 100 % compliance — an ecological upper-bound
benchmark, not an empirical forecast. The literature indicates that protected areas combining
local empowerment, maintained livelihoods, and positive socioeconomic outcomes are more
likely to achieve conservation success (Oldekop et al. 2016, *Conservation Biology* 30(1):133–141,
whiterose.ac.uk/87235). Exclusionary PPA is one scenario, not a universal outcome.

### Emigration model

Emigration rate reported as **actual departures / population at start of tick × 100 %**.
Previous reporter used a disconnected synthetic formula (base rate 8 %/yr + 0.12 pts/yr per
year elapsed) regardless of modelled behaviour.

Annual emigration escalation term (+0.003 per year, adding 15 pp by year 50) has been removed;
no empirical basis for a mechanically fixed escalation date.

Scenario-label emigration multipliers (S3 ×1.4, S4 ×2.0) removed; land-access loss and
livelihood effects are already captured in the income and demographic components.

---

## Minimum analysis before interpreting results

Run ≥ 100 stochastic repetitions per scenario; report median and 5th–95th percentile range.
Priority sensitivity parameters (Ligmann-Zielinska et al. 2020, *JASSS* 23(1):6, jasss.org/23/1/6):

1. Baseline emigration probability (mean and SD)
2. WTA distribution and agreement-attribute effects (vary all ±50 %)
3. Hunting mortality rates
4. Ecological growth rates r and carrying capacities K
5. Patrol effectiveness multipliers (±20 pp)
6. Privatisation habitat-loss rate (central 1 %; stress test 6 %)
7. Protected-area compliance (central 100 %; test 70–85 %)
8. Biodiversity index thresholds (test 75/125 and 90/110)
9. Agreement duration (test 5, 10, 20 yrs)
10. Compensation and livelihood-index coefficients

---

## Local setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.9+ | |
| Java JDK | 17 (recommended) | [Eclipse Temurin](https://adoptium.net/) |
| NetLogo | 7.0.3 | [netlogo.org](https://www.netlogo.org/download) |

```bash
git clone https://github.com/alemaisano/PartEnvModeling_Georgia
cd PartEnvModeling_Georgia
pip install -r requirements.txt
# Linux/macOS: export NETLOGO_HOME="/path/to/NetLogo 7.0.3"
streamlit run app.py
```

On **Windows**, `NETLOGO_HOME` is auto-detected from the registry.
On **Linux**, the app downloads NetLogo automatically on first run if `NETLOGO_HOME` is not set.

---

## Streamlit Cloud deployment

Includes `packages.txt` (`openjdk-17-jdk`) and automatic NetLogo 7.0.3 download on cold start.
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

Nlogo_final_model.nlogox   NetLogo 7 XML model
```

---

## Output metrics

| Column | NetLogo reporter | Description |
|--------|-----------------|-------------|
| `pct_accepted` | `report-pct-accepted` | % community accepting agreement |
| `income_index` | `report-community-income` | Community livelihood index (baseline = 100) |
| `biodiversity_index` | `report-total-biodiversity` | Equally-weighted normalised biodiversity index |
| `emigration_rate` | `report-emigration-rate` | Actual departures / population × 100 (%/yr) |
| `human_pop_indexed` | `report-human-pop-indexed` | Human population % of start |
| `ecosystem_status` | `report-ecosystem-status` | 0 = degraded · 1 = stable · 2 = recovering |
| `deer_index` | `report-pop-deer` | Deer population % of start |
| `chamois_index` | `report-pop-chamois` | Chamois population % of start |
| `bear_index` | `report-pop-bear` | Brown bear population % of start |
| `broadleaf_index` | `report-pop-broadleaf` | Broadleaf forest cover % of start |
| `nontarget_index` | `report-pop-nontarget` | Non-target species % of start |

---

## Key sources

| Source | Geography | Used for |
|--------|-----------|---------|
| Geostat 2024 Population Census | Khulo, Shuakhevi, Georgia | BAU demographic calibration (≈3–3.5 %/yr decline) |
| NACRES/WWF habitat and species mapping | Western Lesser Caucasus | Initial populations; threat directions |
| ECF programme description — ecocorridorscaucasus.org | South Caucasus | Agreement duration (10 yr); livelihood safeguards |
| ECF wildlife compensation — ecocorridorscaucasus.org/wildlife-compensation | Georgia | Predator-compensation mechanism |
| Salmanpour et al. (2025) — PMC12276821 | Iran/Caspian | Red-deer growth calibration (net ≈2.2 %/yr observed) |
| Swenson et al. — SLU epsilon.slu.se/201058.pdf | Sweden | Bear growth range (4–5 %/yr recovering population) |
| Donini et al. (2021) — PMC8216891 | European Alps | Optional deer–chamois competition sensitivity term |
| Critchlow et al. (2022) — DOI:10.1111/csp2.12746 | Uganda / global | Patrol multiplier approach; spatial limitations |
| Greiner (2015) — ideas.repec.org/a/eee/agisys/v137y2015 | Australian pastoral | Agreement attribute directions |
| Collective PES review — *Ecology and Society* 28(1):13 | Multi-country | Tenure security → stable participation |
| Oldekop et al. (2016) — whiterose.ac.uk/87235 | Global | S3 framing: exclusionary PPA not universally positive |
| FAO Forest Resources Assessment 2025 — openknowledge.fao.org | Georgia / global | Broadleaf dynamics |
| Ligmann-Zielinska et al. (2020) — jasss.org/23/1/6 | ABM methodology | Sensitivity-analysis design for data-poor ABMs |
