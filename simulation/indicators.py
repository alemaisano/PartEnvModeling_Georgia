from __future__ import annotations

"""
Robust Decision Making (RDM) summary and Adaptive Pathways logic.

Thresholds are expressed as index values (baseline = 100 for most species/income).
"""

import pandas as pd
import numpy as np

# ── Default thresholds (index units, baseline = 100) ─────────────────────────
DEFAULT_THRESHOLDS = {
    "deer_index":        70.0,   # deer pop must stay ≥ 70 % of start
    "chamois_index":     70.0,
    "bear_index":        80.0,   # bear recovery objective
    "broadleaf_index":   80.0,
    "biodiversity_index": 80.0,
    "income_index":      90.0,   # community income must not fall below 90
}

# ── RDM ──────────────────────────────────────────────────────────────────────

def rdm_summary(
    batch_df: pd.DataFrame,
    thresholds: dict[str, float] | None = None,
    final_tick: int | None = None,
) -> pd.DataFrame:
    """
    For each run compute which objectives are met at the final tick, then
    aggregate across runs.

    Returns one row per scenario (identified by the `scenario` param column if
    present, otherwise a single aggregate row).

    Columns:
        prob_deer_ok, prob_chamois_ok, prob_bear_ok, prob_broadleaf_ok,
        prob_biodiversity_ok, prob_income_ok,
        mean_income_final, robustness_score (share of objectives met on avg)
    """
    thr = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    if final_tick is None:
        final_tick = int(batch_df["tick"].max())

    final = batch_df[batch_df["tick"] == final_tick].copy()
    if final.empty:
        return pd.DataFrame()

    objectives = [k for k in thr if k in final.columns]

    def _group_rdm(grp: pd.DataFrame) -> pd.Series:
        results: dict = {}
        met_flags = []
        for obj in objectives:
            col_vals = grp[obj].dropna()
            if len(col_vals) == 0:
                results[f"prob_{obj}_ok"] = float("nan")
            else:
                met = (col_vals >= thr[obj]).mean()
                results[f"prob_{obj}_ok"] = round(float(met), 3)
                met_flags.append(float(met))

        if "income_index" in grp.columns:
            results["mean_income_final"] = round(float(grp["income_index"].mean()), 1)

        results["robustness_score"] = round(float(np.mean(met_flags)), 3) if met_flags else float("nan")
        return pd.Series(results)

    # Group by scenario parameter if it exists
    if "param_scenario" in final.columns:
        summary = final.groupby("param_scenario").apply(_group_rdm).reset_index()
        summary.rename(columns={"param_scenario": "scenario"}, inplace=True)
    else:
        summary = _group_rdm(final).to_frame().T
        summary.index = [0]

    return summary


# ── Adaptive Pathways ─────────────────────────────────────────────────────────

PATHWAY_RULES = [
    {
        "indicator": "deer_index",
        "condition": lambda v, thr: v < thr,
        "threshold_key": "deer_index",
        "recommendation": (
            "Deer population below threshold — recommended actions:\n"
            "  • Increase hunting restrictions (reduce hunt pressure)\n"
            "  • Deploy community rangers (rangers-in-agreement?)\n"
            "  • Activate predator compensation to reduce conflict pressure"
        ),
        "severity": "warning",
    },
    {
        "indicator": "chamois_index",
        "condition": lambda v, thr: v < thr,
        "threshold_key": "chamois_index",
        "recommendation": (
            "Chamois population below threshold — recommended actions:\n"
            "  • Reduce grazing intensity (agreement-grazing-reduction?)\n"
            "  • Restrict hunting (compensation-enabled?)\n"
            "  • Increase patrol activity"
        ),
        "severity": "warning",
    },
    {
        "indicator": "broadleaf_index",
        "condition": lambda v, thr: v < thr,
        "threshold_key": "broadleaf_index",
        "recommendation": (
            "Broadleaf forest cover below threshold — recommended actions:\n"
            "  • Reduce logging (lower hunt/log pressure in agreement)\n"
            "  • Activate community planting (agreement-planting?)\n"
            "  • Pursue plot merging for landscape connectivity (agreement-plot-merging?)"
        ),
        "severity": "warning",
    },
    {
        "indicator": "income_index",
        "condition": lambda v, thr: v < thr,
        "threshold_key": "income_index",
        "recommendation": (
            "Community income below threshold — recommended actions:\n"
            "  • Enable marginal loss compensation (agreement-marginal-loss-incentive?)\n"
            "  • Activate self-sustenance incentives (agreement-selfsustain-incentive?)\n"
            "  • Open market access (agreement-market-access?)\n"
            "  • Provide education support (agreement-education?)"
        ),
        "severity": "error",
    },
    {
        "indicator": "bear_index",
        "condition": lambda v, thr: v < thr,
        "threshold_key": "bear_index",
        "recommendation": (
            "Brown bear population below recovery objective — recommended actions:\n"
            "  • Reduce human disturbance\n"
            "  • Activate forest restoration (agreement-planting?)\n"
            "  • Enable predator compensation to reduce retaliatory killing"
        ),
        "severity": "info",
    },
    {
        "indicator": "biodiversity_index",
        "condition": lambda v, thr: v < thr,
        "threshold_key": "biodiversity_index",
        "recommendation": (
            "Overall biodiversity index below threshold — system-wide degradation risk.\n"
            "  • Consider switching to Scenario 2 (Voluntary Agreement) or\n"
            "    Scenario 3 (State-Led Conservation)\n"
            "  • Activate all ecological action switches\n"
            "  • Extend agreement duration to allow ecosystem recovery"
        ),
        "severity": "error",
    },
]


def check_adaptive_pathways(
    current_values: dict[str, float],
    thresholds: dict[str, float] | None = None,
) -> list[dict]:
    """
    Evaluate current indicator values against thresholds and return a list
    of triggered pathway recommendations.

    Parameters
    ----------
    current_values : dict  {reporter_key: current_value}
    thresholds : dict | None  Override DEFAULT_THRESHOLDS.

    Returns
    -------
    list of dicts with keys: indicator, value, threshold, recommendation, severity
    """
    thr = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    triggered = []

    for rule in PATHWAY_RULES:
        ind = rule["indicator"]
        thr_key = rule["threshold_key"]
        if ind not in current_values or thr_key not in thr:
            continue
        val = current_values[ind]
        if val is None or (isinstance(val, float) and np.isnan(val)):
            continue
        if rule["condition"](val, thr[thr_key]):
            triggered.append(
                {
                    "indicator": ind,
                    "value": round(float(val), 2),
                    "threshold": thr[thr_key],
                    "recommendation": rule["recommendation"],
                    "severity": rule["severity"],
                }
            )

    return triggered
