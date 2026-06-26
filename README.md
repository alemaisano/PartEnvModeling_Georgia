# Corridor Governance Model — Streamlit Webapp

Interactive simulation and decision-support tool built around the
**NetLogo Corridor Governance Model v6** (`Nlogo_final_model.nlogox`),
modelling community-led conservation governance in rural Georgia (South Caucasus).

**Live app:** https://partenvmodgeorgia.streamlit.app/

> **Important:** This model is an exploratory scenario-comparison tool, not a forecast.
> Parameters marked as heuristic assumptions (see evidence codes below) should be varied
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
| **S4** | Private Investment | Corridor privatised; ecosystem starts in a degraded state |

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
| Land tenure security | WTA boost +0.10 initial; +0.02/yr cumulative |
| Grazing reduction | Reduces grazing — aids ungulate recovery |
| Community planting | Boosts broadleaf forest cover |
| Plot merging | Land consolidation: income +0.5–5.0/yr |

---

## Page guide

### Simulate

1. **Reference scenarios** — tick S1, S3, S4 to include them as baselines.
2. **Scenario 2 builder** — load a preset or toggle switches manually. Name the variant and click **+ Add to run list**.
3. **Run settings** — set simulation years (10–50), agreement duration (default 25 yrs), and MC runs (3–100).
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

Parameters classified as **H** are exploratory and their magnitudes should be varied in
sensitivity analysis before conclusions are drawn.

### Demographic parameters

| Parameter | Value | Evidence | Source / rationale |
|-----------|-------|----------|--------------------|
| Net natural population change | +0.008/yr | H | Assumed positive growth; contradicts recent Georgian census data showing mountain-municipality decline — flagged for revision |
| Baseline emigration prob. (μ) | 0.08 | H | Heuristic prior; no local calibration data |
| Baseline emigration SD | 0.05 | H | Heuristic; captures heterogeneity in mobility |
| WTA mean | 0.45 | H | Heuristic prior; local survey data needed |
| WTA SD | 0.20 | H | Higher values increase clamping artefacts at 0/1 boundaries |

**Note on demographic calibration:** The 2024 Georgian national census records compound annual
population declines of approximately −3.5 %/yr in Khulo and −3.0 %/yr in Shuakhevi between
2014 and 2024 (Geostat 2024 Population Census). The current +0.8 %/yr natural-growth assumption
is inconsistent with this trend; all demographic outputs should be treated as indicative only.
This is a known limitation and a priority parameter for sensitivity analysis.

### Ecological parameters

| Species | Initial pop. | K | r (central) | Sensitivity range | Evidence |
|---------|-------------|---|-------------|------------------|---------|
| Red deer | 400 | 1 200 | 0.11 | 0.05–0.20 | L / R / X |
| Chamois | 200 (proxy) | 600 | 0.10 | 0.04–0.18 | L / R / X |
| Brown bear | 40 | 120 | 0.05 | 0.02–0.10 | L / X |
| Broadleaf forest | 100 (index) | 200 | 0.03 | 0.01–0.08 | R / X |
| Non-target biodiversity | 100 (index) | 200 | 0.15 | 0.06–0.30 | H |

**Red deer — 400 individuals, K = 1 200, r = 0.11 [L/R/X]**
Initial population consistent with survey estimates of 325–527 individuals in and around
Borjomi-Kharagauli National Park (NACRES/WWF habitat and species mapping, Western Lesser Caucasus).
r = 0.11 is an upper-range estimate of the intrinsic growth rate, intended to produce near-stable
dynamics at BAU hunting pressure; a recovering Caspian red-deer population showed an observed net
trend of ≈2.2 %/yr (Salmanpour et al. 2025, *Population Dynamics and Ecology of the Caspian Red
Deer*, PMC12276821). Note: observed net trend ≠ intrinsic r; the logistic model's r is the
biological potential before mortality and density dependence. The central estimate should be
varied in the range 0.05–0.20 in sensitivity analysis.

**Chamois — 200 proxy, K = 600, r = 0.10 [L/R/X]**
No reliable corridor-specific abundance estimate; 200 is a scaled proxy informed by wider
Lesser Caucasus estimates (NACRES/WWF). Treated as highly uncertain; vary in sensitivity analysis.

**Brown bear — 40 individuals, K = 120, r = 0.05 [L/X]**
Initial population derived from locally reported density of 1.9–2.3 bears/100 km² in
Borjomi-Kharagauli (NACRES/WWF) applied to the priority-site network area (≈1 965 km²).
K = 120 implies ≈6.1 bears/100 km²; this is above local density and represents a recovery target
rather than a baseline — treating it as a target carrying capacity, not a current equilibrium.
Growth rate based on recovering European brown bear populations (≈4–5 %/yr;
Swenson et al., *Monitoring and Management of the Swedish Brown Bear*, SLU, epsilon.slu.se/201058.pdf).

**Broadleaf forest — index baseline 100, K = 200, r = 0.03 [R/X]**
Modelled as a habitat-quality composite index, not a literal tree count.
K = 200 implies doubling above baseline — more a policy aspiration than a current carrying capacity.
FAO *Global Forest Resources Assessment 2025* (openknowledge.fao.org) provides reference for
regional forest dynamics; r = 0.03 is in the upper range for area-based change and more
appropriate for a quality/density index under active restoration.
Logging kill rate at intensity=1 was reduced from 4 % to 2 %/yr so that BAU pressure (2 %/yr)
does not exceed r (3 %/yr): previously, broadleaf had no stable equilibrium and collapsed to 0
regardless of governance. With 2 %/yr, BAU equilibrium is ≈67 % of starting index;
community planting under S2 allows recovery toward 100 %+.

**Non-target biodiversity — K = 200, r = 0.15 [H]**
Composite placeholder for all non-focal species (small mammals, birds, invertebrates, reptiles).
Many of these have high intrinsic growth rates (r > 0.20); r = 0.15 is a central composite estimate.
At this value, BAU pressure (0.11/yr combined) produces a gradual decline of ≈3.5 %/yr from starting
density, with a BAU equilibrium at ≈27 % of K. Patrol under S2 (rangers active, hunt→0) halves total
pressure to ≈0.06/yr, allowing recovery toward 60 % of K. Community planting (agreement switch) also
boosts non-target r via habitat improvement, as it does for broadleaf.
Vary 0.06–0.30 in sensitivity analysis.

**Biodiversity index [H]**
Raw-sum index: (total current pop.) / (total initial pop.) × 100, so each species is weighted
by its absolute population size. This means deer (population 400) determines a much larger share
of the index than bear (population 40). Scenario comparisons on this index are dominated by
ungulate dynamics; bear trajectories are largely invisible in the aggregate.
This weighting choice is a known limitation: consider disaggregated species-level charts for
bear and broadleaf when interpreting results.
Ecosystem status thresholds: Low < 75, Medium 75–130, High > 130.
Ecosystem-status growth modifier is ±0.03 additive to r (±3 % effect); previously ±0.05
which produced ±100 % effect on bears (r = 0.05) — now less harsh and more symmetric.

**Heritage effect:** In years 1–7, extraction kill rates scale up linearly from near-zero to
their full BAU values. This represents the tail of pre-existing ECF conservation practices:
species show initial slow growth at simulation start, with trajectories diverging as scenario
governance structures take over after year 7.

**Annual stochastic noise:** Each species receives a ±1 % (SD) multiplicative stochastic shock
each tick, producing realistic year-to-year variation around the underlying trend.

### Pressure parameters [H informed by L/X]

Local evidence supports the direction of threats (hunting, logging, grazing, disturbance);
exact annual removal percentages are not documented (NACRES/WWF threat assessment).
These rates are the largest source of uncertainty in the model.

| Intensity level | Hunting mortality | Logging mortality | Agricultural pressure |
|-----------------|------------------|------------------|-----------------------|
| 0 — none | 3.0 % | 1.0 % | 1.0 % |
| 1 — low (subsistence) | 8.0 % | 2.0 % | 3.0 % |
| 2 — medium (BAU) | 18.0 % | 10.0 % | 6.0 % |

**Note:** Intensity = 0 produces non-zero mortality (3 % hunting, 1 % logging, 1 % agriculture).
This represents residual background pressure even under a nominal ban, and means the S3
protected-area scenario retains some ecological pressure throughout. Whether this is realistic
depends on actual enforcement capacity; vary intensity-0 rates across 0–3 % in sensitivity analysis.
Logging intensity = 1 was reduced from 4 % to 2 %/yr to prevent broadleaf collapse under BAU
(previously logging kill exceeded growth rate at all densities, so broadleaf had no stable equilibrium).

**Patrol effectiveness** modifies the categorical hunt-intensity level directly:
Low patrol (+0/−0 depending on year), Medium patrol (−1 level), High patrol (−2 levels).
After year 20 without active patrol (level 0), intensity escalates by +1 level (pressure creep).
Evidence supports patrol deterrence effects (Critchlow et al. 2022, *Conservation Science and
Practice*, DOI:10.1111/csp2.12746), though spatial allocation and displacement effects are not
captured in this non-spatial model.

**Agriculture/grazing intensity** similarly escalates +1 level after year 20 if community
action level is 0. This represents gradual encroachment without governance pressure, treated
as a heuristic long-run trend.

### Conservation agreement parameters [L / X / H]

**Agreement duration: 25 years** (model default).
ECF's documented programme uses 10-year conservation agreements
(Eco Corridor Foundation, ecocorridorscaucasus.org). The 25-year default is more optimistic about renewal dynamics; test 10 and 20 years in sensitivity analysis.

**S3 and S4 acceptance (pct_accepted):** In all scenarios, agent willingness-to-accept (WTA)
evolves from the same initial distribution and is updated each tick based on income, opportunity
perception, and predator damage. The metric `pct_accepted` is therefore meaningful and comparable
across scenarios:
- S3: reflects the fraction of the community that genuinely *supports* strict conservation (vs.
  complying reluctantly). Income falls under the S3 penalty → WTA erodes over time → declining
  community support despite ecological success. Dropout via uncompensated predator damage (5 %/yr).
- S4: reflects community disposition toward conservation values despite privatisation. Income
  stays higher (investor boost) but ecosystem degradation raises predator damage and, if income
  falls below 80, agents withdraw support at 8 %/yr.
S1 is the only scenario with forced pct_accepted = 0 (no agreement exists).

**Agreement momentum:** When an agreement expires, benefits do not snap to zero immediately.
An `agreement-momentum` variable (1.0 while active) decays at ×0.80/yr after expiry,
scaling all income boosts continuously. After 5 years: ≈33 % of original boost; after 10 years: ≈11 %.
Agent reversion is also probabilistic: each year an agent reverts with probability `1 − momentum`,
so the community unwinds gradually rather than all at once. This reflects that learned behaviours,
established relationships, and capital investments do not disappear overnight when a formal agreement ends.

WTA adjustment **directions** are supported by the conservation contract literature;
**exact magnitudes are exploratory**. Compensation, tenure, obligations, duration and flexibility
all influence participation (Greiner 2015, *Agricultural Systems* 137:154–165,
ideas.repec.org/a/eee/agisys/v137y2015). Tenure security supports stable participation
(*Ecology and Society* 28(1):13, ecologyandsociety.org).
All WTA coefficients should be varied ±50 % in sensitivity analysis.

**Land tenure:** +0.10 one-time boost at initialisation plus +0.02/yr cumulative annual increase.
The cumulative annual term has no empirical upper bound specified and grows without limit over
a 50-year run; this is a known limitation. Consider clamping or removing the annual term
in sensitivity testing.

**Random investor in S2:** When the simulation begins, an investor is introduced with
probability p = 0.6. This means two runs of an identical S2 scenario can produce systematically
different outcomes (with vs. without investor). This design choice introduces stochastic
scenario-level variation beyond the intended Monte Carlo parameter uncertainty.

### Privatisation scenario (S4) [H]

All scenarios start from identical ecological initial conditions. S4 diverges through gradual
habitat degradation of 3 %/yr applied to all species each tick (representing fragmentation and
reduced habitat quality from investor activities). The previous design pre-cut populations by 50 %
at setup, which produced an immediate cliff in the charts and predetermined results before any
dynamics could play out. With a common baseline and 3 %/yr degradation, S4 diverges naturally
over time while remaining comparable to other scenarios at t = 0.
Test 1–6 %/yr habitat loss in sensitivity analysis.

### Protected area scenario (S3)

Modelled as idealised strict protection with 100 % compliance from year 2 — an ecological
upper-bound benchmark, not an empirical forecast. Literature indicates that protected areas
combining local empowerment, maintained livelihoods, and positive socioeconomic outcomes are
more likely to achieve conservation success (Oldekop et al. 2016, *Conservation Biology* 30(1):133–141,
whiterose.ac.uk/87235). The exclusionary PPA modelled here is one scenario, not a universal outcome.

### Income model

The community income index changes each tick by `net-change`, a sum of all active boosts (education,
market access, self-sustain, patrol income, etc.) minus costs (hunting restrictions, logging costs,
grazing facility, predator damage). Two stochastic components are added each tick:

- **Baseline noise** `N(0, 2.5)`: year-to-year variation from weather, markets, and household shocks (±~5 index points in most years).
- **Crisis shocks**: with probability 8 % per year, an additional `N(−12, 4)` shock is applied, representing irregular but recurring crises (crop failure, market collapse, disease). Expected frequency: roughly one crisis every 12 years.

Both components apply to all scenarios equally, producing visible wobbling around the underlying trend without altering the long-run direction. Vary the shock frequency (3–15 %) and magnitude (−5 to −20) in sensitivity analysis.

### Emigration model

The emigration rate reporter uses a **synthetic formula** rather than actual modelled departures:

```
reported rate = 8.0 + secular_trend + income_effect + eco_effect + scenario_effect
```

where `secular_trend = years_elapsed × 0.12` (if income < 105), adding 6 pp/yr by year 50.
Scenario-specific additions: S3 +4 pp, S4 +10 pp (hard-coded regardless of other conditions).

This formula is disconnected from the agent-level emigration behaviour (`maybe-emigrate`), which
separately drives the actual human population trajectory. The chart labelled "emigration rate"
reflects this formula, not observed departures. The divergence between the formula and agent
behaviour is a known limitation and a priority area for future revision.

---

## Minimum analysis before interpreting results

Run ≥ 100 stochastic repetitions per scenario; report median and 5th–95th percentile range.
Priority sensitivity parameters (Ligmann-Zielinska et al. 2020, *JASSS* 23(1):6, jasss.org/23/1/6):

1. Baseline emigration probability (mean and SD) — and whether formula or agent behaviour is used
2. WTA distribution and agreement-attribute effects (vary all ±50 %)
3. Hunting mortality rates — especially intensity=0 residual (0–3 %)
4. Ecological growth rates r and carrying capacities K (broad ranges; data-poor)
5. Privatisation habitat-loss rate (current 3 %/yr; test 1–6 %)
6. Protected-area compliance and residual pressure (current: full compliance, 3 % residual hunting)
7. Agreement duration (test 10, 20, 25 yrs)
8. Biodiversity index weighting (current: raw-sum; test equal-weight normalised)
9. Patrol effectiveness (categorical level change vs. proportional multiplier)
10. Natural population growth rate (current +0.8 %/yr contradicts census data)

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
| `biodiversity_index` | `report-total-biodiversity` | Raw-sum biodiversity index (deer-weighted) |
| `emigration_rate` | `report-emigration-rate` | Synthetic formula (see limitations above) |
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
| Geostat 2024 Population Census | Khulo, Shuakhevi, Georgia | BAU demographic benchmark (≈ −3–3.5 %/yr observed decline; model uses +0.8 %/yr — known mismatch) |
| NACRES/WWF habitat and species mapping | Western Lesser Caucasus | Initial populations; threat directions |
| ECF programme description — ecocorridorscaucasus.org | South Caucasus | Agreement mechanism reference; 10-yr agreement duration (model uses 25 yr default) |
| ECF wildlife compensation — ecocorridorscaucasus.org/wildlife-compensation | Georgia | Predator-compensation switch mechanism |
| Salmanpour et al. (2025) — PMC12276821 | Iran/Caspian | Red-deer population dynamics reference (observed net ≈ 2.2 %/yr) |
| Swenson et al. — SLU epsilon.slu.se/201058.pdf | Sweden | Brown bear recovery growth range (4–5 %/yr) |
| Donini et al. (2021) — PMC8216891 | European Alps | Deer–chamois competition dynamics reference |
| Critchlow et al. (2022) — DOI:10.1111/csp2.12746 | Uganda / global | Patrol deterrence effects; spatial limitations noted |
| Greiner (2015) — ideas.repec.org/a/eee/agisys/v137y2015 | Australian pastoral | Agreement attribute effects on WTA |
| Collective PES review — *Ecology and Society* 28(1):13 | Multi-country | Tenure security and stable participation |
| Oldekop et al. (2016) — whiterose.ac.uk/87235 | Global | S3 framing: exclusionary PPA outcomes vary |
| FAO Forest Resources Assessment 2025 — openknowledge.fao.org | Georgia / global | Broadleaf forest dynamics reference |
| Ligmann-Zielinska et al. (2020) — jasss.org/23/1/6 | ABM methodology | Sensitivity-analysis design for data-poor ABMs |
