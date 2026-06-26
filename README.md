# Corridor Governance Model — Streamlit Webapp

Interactive simulation and decision-support tool built around the
**NetLogo Corridor Governance Model v6** (`Nlogo_final_model.nlogox`),
modelling community-led conservation governance in rural Georgia (South Caucasus).

**Live app:** https://partenvmodgeorgia.streamlit.app/

**Youtube tutorial to use the live app:** https://youtu.be/660jUOIvs0Y

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
2014 and 2024 ([Geostat 2024 Population Census](https://geostat.ge)). The current +0.8 %/yr natural-growth assumption
is inconsistent with this trend; all demographic outputs should be treated as indicative only.
This is a known limitation and a priority parameter for sensitivity analysis. 

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| Net natural population growth | +0.008/yr | Heuristic — no rural-Georgia ABM calibration data exists | **H** — Low; contradicts [Geostat 2024](https://geostat.ge) observed −3 %/yr; treat as placeholder |
| Baseline emigration μ | 0.08 | Heuristic prior | **H** — Low; no local survey data available |
| Baseline emigration SD | 0.05 | Heuristic; heterogeneity assumption | **H** — Low |
| WTA mean | 0.45 | Heuristic prior (updated from design value 0.50) | **H** — Low; local attitudinal survey data needed |
| WTA SD | 0.20 | Heuristic (wider than initial design value 0.15) | **H** — Low; wider spread increases boundary-clamping risk |

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
Borjomi-Kharagauli National Park (Shavgulidze et al. 2016 — *Mapping of Habitats of Key Species
and Key Biodiversity Areas in the Western Lesser Caucasus*, NACRES/WWF; available at
[nacres.org.ge](https://nacres.org.ge)).
r = 0.11 is an upper-range estimate of the intrinsic growth rate, intended to produce near-stable
dynamics at BAU hunting pressure; a recovering Caspian red-deer population showed an observed net
trend of ≈2.2 %/yr ([Salmanpour et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12276821/),
*Population Dynamics and Ecology of the Caspian Red Deer*, PMC12276821). Note: observed net trend ≠ intrinsic r;
the logistic model's r is the biological potential before mortality and density dependence.
The central estimate should be varied in the range 0.05–0.20 in sensitivity analysis.

**Chamois — 200 proxy, K = 600, r = 0.10 [L/R/X]**
No reliable corridor-specific abundance estimate; 200 is a scaled proxy informed by wider
Lesser Caucasus estimates (Shavgulidze et al. 2016, NACRES/WWF). Treated as highly uncertain;
vary in sensitivity analysis. Competition with deer under high grazing pressure is informed by
[Donini et al. (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8216891/) (European Alps context).

**Brown bear — 40 individuals, K = 120, r = 0.05 [L/X]**
Initial population derived from locally reported density of 1.9–2.3 bears/100 km² in
Borjomi-Kharagauli (Shavgulidze et al. 2016, NACRES/WWF) applied to the priority-site network
area (≈1 965 km²). K = 120 implies ≈6.1 bears/100 km²; this is above local density and represents
a recovery target rather than a baseline — treating it as a target carrying capacity, not a current equilibrium.
Growth rate based on recovering European brown bear populations (≈4–5 %/yr;
[Swenson et al., *Monitoring and Management of the Swedish Brown Bear*, SLU](https://epsilon.slu.se/201058.pdf)).
The model uses r = 0.05, the lower bound, since Georgian populations face more constraints than
well-managed Scandinavian ones.

**Broadleaf forest — index baseline 100, K = 200, r = 0.03 [R/X]**
Modelled as a habitat-quality composite index, not a literal tree count.
K = 200 implies doubling above baseline — more a policy aspiration than a current carrying capacity.
[FAO *Global Forest Resources Assessment 2025*](https://openknowledge.fao.org) provides a directional
reference for regional forest dynamics; r = 0.03 is in the upper range for area-based annual change
and is more appropriate for a quality/density index under active restoration.
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

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| Deer N₀ = 400 | 325–527 survey range → central estimate | [Shavgulidze et al. 2016, NACRES/WWF](https://nacres.org.ge) | **R** — regional survey, 2016; not corridor-specific |
| Deer K = 1 200 | 3× N₀ | Heuristic recovery target | **H** — no empirical basis |
| Deer r = 0.11 | Upper-range prior | [Salmanpour et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12276821/) (analogous population) | **X** — Caspian subspecies; observed trend ≠ intrinsic r |
| Chamois N₀ = 200 | Scaled proxy | [Shavgulidze et al. 2016, NACRES/WWF](https://nacres.org.ge) | **R/H** — no corridor-specific count; highly uncertain |
| Chamois K = 600, r = 0.10 | Heuristic | No direct source | **H** — Low |
| Bear N₀ = 40 | 1.9–2.3/100 km² × 1 965 km² | [Shavgulidze et al. 2016, NACRES/WWF](https://nacres.org.ge) | **L** — local density estimate; area is approximate |
| Bear K = 120 | 3× N₀ | Heuristic recovery target | **H** — no empirical basis |
| Bear r = 0.05 | Lower bound of 4–5 %/yr recovery | [Swenson et al., SLU](https://epsilon.slu.se/201058.pdf) | **X** — Scandinavian context; likely underestimates Georgian potential |
| Broadleaf r = 0.03 | Upper range for area-based change | [FAO FRA 2025](https://openknowledge.fao.org) | **R** — national aggregate; not corridor-specific |
| Broadleaf K = 200, N₀ = 100 (index) | Heuristic | No direct source | **H** — index, not literal tree count |
| Non-target r = 0.15, K = 200 | Composite heuristic | No direct source | **H** — Low; placeholder; vary 0.06–0.30 |
| Ecosystem status thresholds (75, 130) | Heuristic breakpoints | No direct source | **H** — arbitrary; vary in sensitivity analysis |
| eco-mod = ±0.03 | Heuristic (calibrated to avoid bear extinction under BAU) | No direct source | **H** — arbitrary magnitude |
| Heritage ramp duration = 7 yr | Heuristic | No direct source | **H** — arbitrary |
| Species stochastic noise SD = 0.01 | Heuristic | No direct source | **H** — gives ≈1 %/yr variation |

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
Evidence supports patrol deterrence effects ([Critchlow et al. 2022](https://doi.org/10.1111/csp2.12746),
*Conservation Science and Practice*), though spatial allocation and displacement effects are not
captured in this non-spatial model.

**Agriculture/grazing intensity** similarly escalates +1 level after year 20 if community
action level is 0. This represents gradual encroachment without governance pressure, treated
as a heuristic long-run trend.

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| Hunting mortality, intensity 0 (nominal ban) | 3.0 %/yr | Heuristic — residual enforcement gap | **H** — Low; vary 0–3 % in sensitivity analysis |
| Hunting mortality, intensity 1 (subsistence) | 8.0 %/yr | Heuristic — consistent with NACRES/WWF threat assessment (direction only) | **H** — Low; no measured off-take data for this region |
| Hunting mortality, intensity 2 (BAU) | 18.0 %/yr | Heuristic | **H** — Low; largest uncertainty source in the model |
| Logging mortality, intensities 0/1/2 | 1/2/10 %/yr | Heuristic (intensity 1 reduced from 4 %/yr to prevent broadleaf collapse) | **H** — Low |
| Patrol deterrence mechanism (−1/−2 intensity levels) | Categorical | [Critchlow et al. 2022](https://doi.org/10.1111/csp2.12746) — direction supported; magnitude is assumption | **X** — Ugandan enforcement context; spatial displacement not captured |
| Pressure escalation after yr 20 | +1 intensity level | Heuristic long-run trend | **H** — Low; arbitrary threshold |

### Conservation agreement parameters [L / X / H]

**Agreement duration: 25 years** (model default).
ECF's documented programme uses 10-year conservation agreements
([Eco-Corridors Fund, ecocorridorscaucasus.org](https://ecocorridorscaucasus.org)). The 25-year default is more optimistic about renewal dynamics; test 10 and 20 years in sensitivity analysis.

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
all influence participation ([Greiner 2015](https://ideas.repec.org/a/eee/agisys/v137y2015icp154-165.html),
*Agricultural Systems* 137:154–165). Tenure security supports stable participation
([*Ecology and Society* 28(1):13](https://www.ecologyandsociety.org/vol28/iss1/art13/)).
All WTA coefficients should be varied ±50 % in sensitivity analysis.

**Land tenure:** +0.10 one-time boost at initialisation plus +0.02/yr cumulative annual increase.
The cumulative annual term has no empirical upper bound specified and grows without limit over
a 50-year run; this is a known limitation. Consider clamping or removing the annual term
in sensitivity testing.

**Random investor in S2:** When the simulation begins, an investor is introduced with
probability p = 0.6. This means two runs of an identical S2 scenario can produce systematically
different outcomes (with vs. without investor). This design choice introduces stochastic
scenario-level variation beyond the intended Monte Carlo parameter uncertainty.

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| Agreement duration (default) | 25 yr | [ECF programme](https://ecocorridorscaucasus.org) documents 10-yr agreements; 25 yr is optimistic renewal assumption | **L/H** — base period from ECF; renewal dynamic unvalidated |
| WTA adjustment directions | Various | [Greiner 2015](https://ideas.repec.org/a/eee/agisys/v137y2015icp154-165.html); [E&S 28(1):13](https://www.ecologyandsociety.org/vol28/iss1/art13/) | **X** — qualitative directional support; no quantitative transfer possible |
| Land-tenure one-time WTA boost | +0.10 | Informed by [E&S 28(1):13](https://www.ecologyandsociety.org/vol28/iss1/art13/) | **H** — no quantitative basis; arbitrary magnitude |
| Land-tenure annual accumulation | +0.02/yr (uncapped) | Heuristic | **H** — Low; unbounded growth is a known model limitation |
| Agreement momentum decay | ×0.80/yr post-expiry | Heuristic | **H** — Low; arbitrary decay rate |
| Predator-compensation mechanism | Prevents WTA dropout from bear damage | [ECF wildlife compensation](https://ecocorridorscaucasus.org/wildlife-compensation) | **L** — programme documentation; implementation details not empirically validated |
| Predator-damage dropout rate | 5 %/yr if uncompensated damage > 0.5 | Heuristic | **H** — Low |
| Income-loss dropout threshold | income < 80, 8 %/yr | Heuristic | **H** — Low |
| Investor probability in S2 | p = 0.60 | Heuristic design choice | **H** — Low; produces scenario-level stochasticity beyond intended MC uncertainty |

### Privatisation scenario (S4) [H]

All scenarios start from identical ecological initial conditions. S4 diverges through gradual
habitat degradation of 3 %/yr applied to all species each tick (representing fragmentation and
reduced habitat quality from investor activities). The previous design pre-cut populations by 50 %
at setup, which produced an immediate cliff in the charts and predetermined results before any
dynamics could play out. With a common baseline and 3 %/yr degradation, S4 diverges naturally
over time while remaining comparable to other scenarios at t = 0.
Test 1–6 %/yr habitat loss in sensitivity analysis.

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| Habitat degradation rate | 3 %/yr applied to all species | Heuristic — no empirical estimate of privatisation-driven fragmentation in this region | **H** — Low; vary 1–6 %/yr in sensitivity analysis |
| Emigration multiplier | ×2.0 on baseline prob-to-leave | Heuristic | **H** — Low |
| Investor income effect | Partial income recovery (scenario-specific) | Heuristic | **H** — Low; no investor-employment data for Georgian corridor context |

### Protected area scenario (S3)

Modelled as idealised strict protection with 100 % compliance from year 2 — an ecological
upper-bound benchmark, not an empirical forecast. Literature indicates that protected areas
combining local empowerment, maintained livelihoods, and positive socioeconomic outcomes are
more likely to achieve conservation success ([Oldekop et al. 2016](https://doi.org/10.1111/cobi.12567),
*Conservation Biology* 30(1):133–141). The exclusionary PPA modelled here is one scenario, not a universal outcome.

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| Compliance assumption | 100 % from year 2 | Heuristic upper-bound framing | **H** — Low; idealised; real-world PPA compliance varies widely |
| Residual hunting at intensity 0 | 3.0 %/yr | Heuristic enforcement gap (shared with all scenarios) | **H** — Low; vary 0–3 % |
| Emigration multiplier | ×1.4 on baseline prob-to-leave | Heuristic | **H** — Low |
| S3 framing rationale | Exclusionary PPA is one outcome type | [Oldekop et al. 2016](https://doi.org/10.1111/cobi.12567) — global review (165 PAs) | **X** — meta-analysis; causal direction supported; no specific magnitudes transferred |

### Income model

The community income index changes each tick by `net-change`, a sum of all active boosts (education,
market access, self-sustain, patrol income, etc.) minus costs (hunting restrictions, logging costs,
grazing facility, predator damage). Two stochastic components are added each tick:

- **Baseline noise** `N(0, 2.5)`: year-to-year variation from weather, markets, and household shocks (±~5 index points in most years).
- **Crisis shocks**: with probability 8 % per year, an additional `N(−12, 4)` shock is applied, representing irregular but recurring crises (crop failure, market collapse, disease). Expected frequency: roughly one crisis every 12 years.

Both components apply to all scenarios equally, producing visible wobbling around the underlying trend without altering the long-run direction. Vary the shock frequency (3–15 %) and magnitude (−5 to −20) in sensitivity analysis.

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| All income boost/cost coefficients | Various (see S2 policy table) | Heuristic assumptions — no Georgian rural income time-series was used | **H** — Low; largest source of income-model uncertainty |
| Baseline income noise SD | 2.5 index points/yr | Heuristic — stylised year-to-year volatility | **H** — Low; no calibration to local data |
| Crisis shock probability | 8 %/yr (~1 per 12 yr) | Heuristic | **H** — Low; vary 3–15 % |
| Crisis shock magnitude | N(−12, 4) index points | Heuristic | **H** — Low; vary −5 to −20 |
| Income emigration thresholds (75, 90, 105, 115) | Absolute index values | Heuristic | **H** — Low; no empirical calibration |
| Income emigration multipliers (×0.3 – ×2.5) | Multiplicative | Heuristic | **H** — Low; vary ±50 % in sensitivity analysis |

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

**Parameter sources and accuracy:**

| Parameter | Value | Source | Accuracy |
|-----------|-------|--------|----------|
| Base emigration rate (formula) | 8.0 pp/yr | Heuristic — not calibrated to observed data | **H** — Low |
| Secular trend coefficient | 0.12 pp/yr per year elapsed | Heuristic | **H** — Low; disconnected from agent behaviour |
| S3 scenario addition | +4 pp | Heuristic | **H** — Low; arbitrary |
| S4 scenario addition | +10 pp | Heuristic | **H** — Low; arbitrary |
| Agent-level prob-to-leave baseline | N(0.08, 0.05) per agent | Heuristic prior (updated from initial design N(0.3, 0.1)) | **H** — Low; no local emigration survey data |
| Agent-level emigration: secular drift | +0.003 × years_elapsed | Heuristic | **H** — Low |

---

## Minimum analysis before interpreting results

Run multiple stochastic repetitions per scenario; report median and 5th–95th percentile range.
Priority sensitivity parameters ([Ligmann-Zielinska et al. 2020, *JASSS* 23(1):6](https://www.jasss.org/23/1/6.html)):
=======
Run multiple stochastic repetitions per scenario; report median and 5th–95th percentile range.
Priority sensitivity parameters (Ligmann-Zielinska et al. 2020, *JASSS* 23(1):6, jasss.org/23/1/6):
>>>>>>> 4affbcc5ab8b9ea6c3889cb158fe90d1ce2145f5

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

The table covers every quantitative or mechanistic claim drawn from an external source.
Parameters with no listed source are heuristic assumptions (**H**) and must be varied in sensitivity analysis.

| Source | Geography | Specific data extracted | Parameter applied in model | Evidence level |
|--------|-----------|------------------------|---------------------------|----------------|
| [Geostat 2024 Population Census](https://geostat.ge) | Khulo, Shuakhevi, Georgia | −3.5 %/yr (Khulo), −3.0 %/yr (Shuakhevi) compound annual decline 2014–2024 | Demographic benchmark — model's +0.8 %/yr net growth is a known upward bias; flagged for revision | **L** — direct official census; authoritative for observed trend; model currently contradicts this |
| Shavgulidze et al. (2016) — *Mapping of Habitats of Key Species and Key Biodiversity Areas in the Western Lesser Caucasus* ([NACRES / WWF](https://nacres.org.ge)) | Western Lesser Caucasus | Deer: 325–527 individuals in/around Borjomi-Kharagauli NP; Bear: 1.9–2.3/100 km²; chamois: qualitative presence confirmed; threat types listed | Deer N₀ = 400; Bear N₀ = 40 (density × 1 965 km² priority-site area); chamois 200 as scaled proxy; threat directions confirmed | **R** — regional field survey (2016); coarse spatial resolution; not corridor-specific |
| [Eco-Corridors Fund — programme description](https://ecocorridorscaucasus.org) | South Caucasus / Georgia | 10-year community conservation agreements; activity restriction + incentive structure; agreement renewal mechanism | Agreement-duration baseline (model default 25 yr, optimistic); policy-switch mechanism and incentive framing | **L** — programme documentation from implementing organisation; prescriptive, not empirically measured |
| [ECF — wildlife compensation scheme](https://ecocorridorscaucasus.org/wildlife-compensation) | Georgia | Predator-damage compensation as participation incentive described in programme | `agreement-predator-compensation` switch; prevents WTA erosion from bear damage events | **L** — programme documentation; compensation amounts not independently validated |
| [Salmanpour et al. (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12276821/) — *Population Dynamics and Ecology of the Caspian Red Deer*, PMC12276821 | Iran / Caspian region | Observed net population trend ≈ +2.2 %/yr in recovering Caspian red deer | Red deer r = 0.11 (upper-range prior; note: observed net trend ≠ intrinsic r; logistic r is biological potential before mortality) | **X** — analogous case; Caspian subspecies, not Caucasian; density and hunting context differ |
| [Swenson et al. — *Monitoring and Management of the Swedish Brown Bear*, SLU](https://epsilon.slu.se/201058.pdf) | Sweden | European brown bear recovery rates 4–5 %/yr under active management | Brown bear r = 0.05 (lower bound; Georgian population has less management support than Scandinavia) | **X** — analogous case; Scandinavian recovery context likely overestimates Georgian potential |
| [Donini et al. (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8216891/) | European Alps | Competitive interactions between red deer and chamois under high grazing pressure | Grazing-competition penalty on deer and chamois growth under high `community-grazing-level` | **X** — analogous case; Alps densities and vegetation context differ from Caucasus |
| [Critchlow et al. (2022)](https://doi.org/10.1111/csp2.12746) — *Conservation Science and Practice* | Uganda / global | Ranger patrol significantly reduces illegal hunting and snaring; quantified deterrence effect | Patrol-intensity mechanism (−1 or −2 levels on hunt-intensity); pressure escalation without patrol after year 20 | **X** — African enforcement context; spatial displacement and ranger allocation effects not captured in this non-spatial model |
| [Greiner (2015)](https://ideas.repec.org/a/eee/agisys/v137y2015icp154-165.html) — *Agricultural Systems* 137:154–165 | Australian pastoral land | Conservation contract attributes (compensation, tenure, obligations, flexibility, duration) positively affect WTA | Direction of all WTA adjustments for agreement switches; exact magnitudes are exploratory assumptions not transferred from the paper | **X** — Australian pastoral context; no quantitative transfer; vary all coefficients ±50 % |
| [*Ecology and Society* 28(1):13](https://www.ecologyandsociety.org/vol28/iss1/art13/) | Multi-country PES review | Formal land-tenure security supports stable, long-term conservation participation | Land-tenure switch: +0.10 one-time WTA boost; +0.02/yr cumulative (uncapped — known limitation) | **X** — qualitative review; no quantitative coefficients; magnitudes are heuristic assumptions |
| [Oldekop et al. (2016)](https://doi.org/10.1111/cobi.12567) — *Conservation Biology* 30(1):133–141 | Global (165 protected areas) | Protected areas with community exclusion and no livelihood alternatives tend to produce poor social outcomes; outcomes vary by community engagement | S3 framing: modelled as ecological upper-bound benchmark (idealised compliance), not a universal PPA outcome | **X** — global meta-analysis; causal direction informative; specific magnitudes not applied |
| [FAO Global Forest Resources Assessment 2025](https://openknowledge.fao.org) | Georgia / global | Georgian forest cover trends; regional broadleaf dynamics and restoration rates as directional reference | Broadleaf r = 0.03 (upper range for area-based annual change; appropriate for quality/density composite index) | **R** — national-level aggregates; not corridor- or species-specific |
| [Ligmann-Zielinska et al. (2020)](https://www.jasss.org/23/1/6.html) — *JASSS* 23(1):6 | ABM methodology | Protocol for sensitivity analysis in data-poor agent-based models; identifies priority parameters by influence on outputs | Design of the 10-parameter sensitivity sweep listed in the Minimum analysis section | Methodological reference — no parameters transferred |
