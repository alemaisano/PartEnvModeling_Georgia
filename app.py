from __future__ import annotations

"""
Corridor Governance Model — Participatory Simulation Webapp
===========================================================
Run with:   streamlit run app.py

Requires NetLogo 7 installed and NETLOGO_HOME environment variable set, or
pynetlogo auto-detected installation.  See README.md for setup instructions.
"""

import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
MODEL_PATH = str(ROOT / "Nlogo_final_model.nlogox")
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT))

from simulation.netlogo_runner import (
    REPORTERS,
    REPORTER_LABELS,
    PYNETLOGO_AVAILABLE,
    run_simulation,
)
from simulation.batch_runner import run_batch, compute_percentile_bands
from simulation.indicators import (
    rdm_summary,
    check_adaptive_pathways,
    DEFAULT_THRESHOLDS,
)

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Corridor Governance Simulator",
    page_icon="🦌",
    layout="wide",
    initial_sidebar_state="expanded",
)

SCENARIO_NAMES = {
    1: "Sc1 — Business as Usual",
    2: "Sc2 — Voluntary Agreement",
    3: "Sc3 — State-Led Conservation",
    4: "Sc4 — Private Investment",
}

SCENARIO_DESCRIPTIONS = {
    1: "No active governance. Hunting and logging continue; slow ecosystem degradation.",
    2: "Community participatory agreement with configurable switches. Most flexible scenario.",
    3: "State-enforced conservation from year 2: full extraction ban, mandatory rangers.",
    4: "Corridor privatised; ecosystem already degraded at start. All extraction halted by investor.",
}

REPORTER_GROUPS = {
    "Species & Biodiversity": [
        "deer_index", "chamois_index", "bear_index",
        "broadleaf_index", "nontarget_index", "biodiversity_index",
    ],
    "Socioeconomic": [
        "income_index", "human_pop_indexed",
        "emigration_rate", "pct_accepted",
    ],
    "Governance": [
        "ecosystem_status", "hunt_pressure",
        "predator_damage", "agreement_active",
    ],
}

# ── colour palette for reporters ─────────────────────────────────────────────
REPORTER_COLOURS = {
    "deer_index":        "#8B4513",
    "chamois_index":     "#D2691E",
    "bear_index":        "#2F4F4F",
    "broadleaf_index":   "#228B22",
    "nontarget_index":   "#9370DB",
    "biodiversity_index": "#006400",
    "income_index":      "#DAA520",
    "human_pop_indexed": "#4169E1",
    "emigration_rate":   "#DC143C",
    "pct_accepted":      "#20B2AA",
    "ecosystem_status":  "#708090",
    "hunt_pressure":     "#B22222",
    "predator_damage":   "#FF6347",
    "agreement_active":  "#32CD32",
}

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def build_sidebar() -> dict:
    """Render sidebar controls and return collected params dict."""
    st.sidebar.title("Simulation Controls")

    if not PYNETLOGO_AVAILABLE:
        st.sidebar.error(
            "pynetlogo not found. Install it with:\n"
            "```\npip install pynetlogo\n```\n"
            "and ensure NetLogo 7 is installed."
        )

    # ── Scenario ──
    st.sidebar.header("Scenario")
    scenario = st.sidebar.selectbox(
        "Governance Scenario",
        options=[1, 2, 3, 4],
        format_func=lambda x: SCENARIO_NAMES[x],
        index=1,
        help="Select the governance scenario to simulate.",
    )
    st.sidebar.caption(SCENARIO_DESCRIPTIONS[scenario])

    st.sidebar.divider()

    # ── Time ──
    st.sidebar.header("Time Horizon")
    sim_years = st.sidebar.slider("Simulation years", 10, 50, 30, step=1)
    agreement_duration = st.sidebar.slider(
        "Agreement duration (Sc2 only)",
        min_value=0, max_value=50, value=25, step=5,
        help="After this many years the Sc2 agreement expires and agents revert.",
    )

    st.sidebar.divider()

    # ── Scenario 2 switches ──
    sc2_active = scenario == 2
    st.sidebar.header("Agreement Design  _(Sc2 only)_")

    col_a, col_b = st.sidebar.columns(2)

    with col_a:
        rangers          = st.sidebar.toggle("Rangers in agreement",        value=True,  disabled=not sc2_active)
        compensation     = st.sidebar.toggle("Hunting/logging compensation", value=False, disabled=not sc2_active)
        market_access    = st.sidebar.toggle("Market access",               value=False, disabled=not sc2_active)
        education        = st.sidebar.toggle("Education support",           value=True,  disabled=not sc2_active)
        selfsustain      = st.sidebar.toggle("Self-sustain incentive",      value=False, disabled=not sc2_active)
        marginal_loss    = st.sidebar.toggle("Marginal loss incentive",     value=False, disabled=not sc2_active)
        action_incentive = st.sidebar.toggle("Action incentive",            value=False, disabled=not sc2_active)
        pred_comp        = st.sidebar.toggle("Predator compensation",       value=False, disabled=not sc2_active)
        land_tenure      = st.sidebar.toggle("Land tenure security",        value=True,  disabled=not sc2_active)
        grazing_red      = st.sidebar.toggle("Grazing reduction",           value=True,  disabled=not sc2_active)
        planting         = st.sidebar.toggle("Community planting",          value=True,  disabled=not sc2_active)
        plot_merging     = st.sidebar.toggle("Plot merging",                value=False, disabled=not sc2_active)

    params = {
        "scenario":                          scenario,
        "simulation-years":                  sim_years,
        "agreement-duration":                agreement_duration,
        "rangers-in-agreement?":             rangers,
        "compensation-enabled?":             compensation,
        "agreement-market-access?":          market_access,
        "agreement-education?":              education,
        "agreement-selfsustain-incentive?":  selfsustain,
        "agreement-marginal-loss-incentive?": marginal_loss,
        "agreement-action-incentive?":       action_incentive,
        "agreement-predator-compensation?":  pred_comp,
        "agreement-land-tenure?":            land_tenure,
        "agreement-grazing-reduction?":      grazing_red,
        "agreement-planting?":               planting,
        "agreement-plot-merging?":           plot_merging,
    }
    return params, sim_years


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def plot_timeseries(df: pd.DataFrame, cols: list[str], title: str) -> go.Figure:
    """Line chart for a set of reporter columns over ticks."""
    fig = go.Figure()
    for col in cols:
        if col in df.columns and df[col].notna().any():
            fig.add_trace(go.Scatter(
                x=df["tick"], y=df[col],
                mode="lines",
                name=REPORTER_LABELS.get(col, col),
                line=dict(color=REPORTER_COLOURS.get(col, "#888"), width=2),
            ))
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="Index (baseline = 100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
        height=340,
    )
    return fig


def plot_percentile_bands(
    bands_df: pd.DataFrame,
    col: str,
    title: str,
    single_df: pd.DataFrame | None = None,
) -> go.Figure:
    """Fan chart: p10/p90 shaded band + median line, optional single-run overlay."""
    p10_col    = f"{col}_p10"
    med_col    = f"{col}_median"
    p90_col    = f"{col}_p90"

    fig = go.Figure()

    if p10_col in bands_df.columns and p90_col in bands_df.columns:
        fig.add_trace(go.Scatter(
            x=pd.concat([bands_df["tick"], bands_df["tick"][::-1]]),
            y=pd.concat([bands_df[p90_col], bands_df[p10_col][::-1]]),
            fill="toself",
            fillcolor="rgba(100,149,237,0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            name="P10–P90 range",
            hoverinfo="skip",
        ))

    if med_col in bands_df.columns:
        fig.add_trace(go.Scatter(
            x=bands_df["tick"], y=bands_df[med_col],
            mode="lines",
            name="Median",
            line=dict(color="#4169E1", width=2.5),
        ))

    if single_df is not None and col in single_df.columns:
        fig.add_trace(go.Scatter(
            x=single_df["tick"], y=single_df[col],
            mode="lines",
            name="Single run",
            line=dict(color=REPORTER_COLOURS.get(col, "#888"), dash="dash", width=1.5),
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=REPORTER_LABELS.get(col, col),
        height=300,
        margin=dict(t=50, b=40),
    )
    return fig


def plot_rdm_bar(rdm_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of robustness probabilities."""
    prob_cols = [c for c in rdm_df.columns if c.startswith("prob_")]
    if rdm_df.empty or not prob_cols:
        return go.Figure()

    row = rdm_df.iloc[0]
    labels = [c.replace("prob_", "").replace("_ok", "").replace("_", " ").title() for c in prob_cols]
    values = [float(row[c]) if not pd.isna(row[c]) else 0.0 for c in prob_cols]
    colours = ["#228B22" if v >= 0.7 else "#DAA520" if v >= 0.5 else "#DC143C" for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colours,
        text=[f"{v:.0%}" for v in values],
        textposition="outside",
    ))
    fig.add_vline(x=0.7, line_dash="dash", line_color="gray", annotation_text="70%")
    fig.update_layout(
        title="Probability each objective is met (final year)",
        xaxis=dict(range=[0, 1.1], tickformat=".0%"),
        height=320,
        margin=dict(t=50, b=40, r=80),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO COMPARISON HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def run_all_scenarios(params: dict, sim_years: int) -> dict[int, pd.DataFrame]:
    """Run all 4 scenarios with current switches, return dict keyed by scenario number."""
    results = {}
    for sc in [1, 2, 3, 4]:
        p = {**params, "scenario": sc}
        try:
            df, _ = run_simulation(MODEL_PATH, p, n_ticks=sim_years)
            results[sc] = df
        except Exception as exc:
            st.warning(f"Scenario {sc} failed: {exc}")
    return results


def plot_scenario_comparison(
    scenario_dfs: dict[int, pd.DataFrame],
    col: str,
) -> go.Figure:
    fig = go.Figure()
    colours = ["#E63946", "#2A9D8F", "#E9C46A", "#264653"]
    for i, (sc, df) in enumerate(scenario_dfs.items()):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["tick"], y=df[col],
                mode="lines",
                name=SCENARIO_NAMES[sc],
                line=dict(color=colours[i % 4], width=2),
            ))
    fig.update_layout(
        title=f"{REPORTER_LABELS.get(col, col)} — Scenario Comparison",
        xaxis_title="Year",
        yaxis_title=REPORTER_LABELS.get(col, col),
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=40),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# ADAPTIVE PATHWAYS DISPLAY
# ─────────────────────────────────────────────────────────────────────────────

def display_adaptive_pathways(df: pd.DataFrame, thresholds: dict):
    """Check final-tick values and show triggered pathway cards."""
    if df.empty:
        return
    final_row = df.iloc[-1]
    current_vals = {col: final_row[col] for col in REPORTERS if col in df.columns}
    triggered = check_adaptive_pathways(current_vals, thresholds)

    if not triggered:
        st.success("All monitored indicators are above their thresholds at the final year.")
        return

    for item in triggered:
        sev = item["severity"]
        fn = st.error if sev == "error" else (st.warning if sev == "warning" else st.info)
        fn(
            f"**{REPORTER_LABELS.get(item['indicator'], item['indicator'])}**  "
            f"= {item['value']:.1f}  (threshold: {item['threshold']:.1f})\n\n"
            + item["recommendation"]
        )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    params, sim_years = build_sidebar()

    st.title("Corridor Governance Model — Participatory Simulator")
    st.caption(
        "Built on the NetLogo Corridor Governance Model v6. "
        "Adjust parameters in the sidebar, then run a simulation."
    )

    if not PYNETLOGO_AVAILABLE:
        st.error(
            "**pynetlogo is not installed.**  "
            "Please follow the setup instructions in README.md before running simulations."
        )
        st.stop()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_single, tab_batch, tab_compare, tab_rdm = st.tabs([
        "Single Run", "Monte Carlo", "Scenario Comparison", "Decision Support"
    ])

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 1 — SINGLE RUN
    # ═══════════════════════════════════════════════════════════════════════
    with tab_single:
        st.subheader("Single Simulation Run")
        col_btn, col_warn = st.columns([1, 3])
        run_clicked = col_btn.button("▶  Run Simulation", type="primary", use_container_width=True)

        if run_clicked:
            with st.spinner("Running NetLogo simulation…"):
                try:
                    df, run_warnings = run_simulation(
                        MODEL_PATH, params, n_ticks=sim_years
                    )
                    st.session_state["single_df"] = df
                    st.session_state["single_params"] = params.copy()
                    if run_warnings:
                        with col_warn:
                            with st.expander(f"{len(run_warnings)} warning(s)", expanded=False):
                                for w in run_warnings:
                                    st.warning(w)
                except Exception as exc:
                    st.error(f"Simulation failed: {exc}")
                    st.stop()

        if "single_df" not in st.session_state:
            st.info("Press **Run Simulation** to start.")
        else:
            df: pd.DataFrame = st.session_state["single_df"]

            # Missing reporters notice
            missing_cols = [c for c in REPORTERS if df[c].isna().all()]
            if missing_cols:
                st.warning(
                    "The following reporters returned no data (NaN). "
                    "Check reporter names in `simulation/netlogo_runner.py`:\n"
                    + ", ".join(missing_cols)
                )

            # ── Species & Biodiversity plot ──
            st.plotly_chart(
                plot_timeseries(
                    df,
                    REPORTER_GROUPS["Species & Biodiversity"],
                    "Species Populations & Biodiversity (index, baseline = 100)",
                ),
                use_container_width=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(
                    plot_timeseries(df, REPORTER_GROUPS["Socioeconomic"], "Socioeconomic Indicators"),
                    use_container_width=True,
                )
            with c2:
                st.plotly_chart(
                    plot_timeseries(df, REPORTER_GROUPS["Governance"], "Governance Indicators"),
                    use_container_width=True,
                )

            # ── Summary table ──
            st.subheader("Final-year Summary")
            final = df.iloc[-1][list(REPORTERS.keys())].rename(REPORTER_LABELS)
            summary_df = pd.DataFrame(
                {"Indicator": final.index, "Final Value": final.values.round(2)}
            ).set_index("Indicator")
            st.dataframe(summary_df, use_container_width=True)

            # ── Download ──
            csv = df.to_csv(index=False).encode()
            st.download_button(
                "⬇ Download results CSV", csv, "single_run_results.csv", "text/csv"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2 — MONTE CARLO
    # ═══════════════════════════════════════════════════════════════════════
    with tab_batch:
        st.subheader("Monte Carlo / Batch Run")
        st.caption(
            "Uncertain parameters are sampled uniformly within the ranges you define. "
            "Results are saved to `outputs/batch_results.csv`."
        )

        n_runs = st.slider("Number of Monte Carlo runs", 5, 200, 30, step=5)

        st.markdown("**Define uncertainty ranges for numeric parameters:**")
        uncertain_ranges: dict[str, tuple[float, float]] = {}

        unc_cols = st.columns(3)
        numeric_params = {
            "simulation-years":   (10, 50),
            "agreement-duration": (5,  50),
        }
        for i, (pname, (def_lo, def_hi)) in enumerate(numeric_params.items()):
            with unc_cols[i % 3]:
                lo, hi = st.slider(
                    f"{pname}", def_lo, def_hi,
                    (int(params.get(pname, def_lo)), int(params.get(pname, def_hi))),
                    key=f"unc_{pname}",
                )
                if lo < hi:
                    uncertain_ranges[pname] = (lo, hi)

        run_batch_clicked = st.button("▶  Run Monte Carlo", type="primary")

        if run_batch_clicked:
            progress_bar = st.progress(0, text="Starting batch runs…")

            def _progress(done, total):
                progress_bar.progress(done / total, text=f"Run {done}/{total}…")

            with st.spinner("Running batch…"):
                try:
                    batch_df = run_batch(
                        model_path=MODEL_PATH,
                        base_params=params,
                        uncertain_ranges=uncertain_ranges,
                        n_runs=n_runs,
                        n_ticks=sim_years,
                        progress_callback=_progress,
                    )
                    st.session_state["batch_df"] = batch_df
                    progress_bar.empty()
                    st.success(f"Completed {n_runs} runs. Results saved to `outputs/batch_results.csv`.")
                except Exception as exc:
                    st.error(f"Batch run failed: {exc}")

        if "batch_df" not in st.session_state:
            st.info("Press **Run Monte Carlo** to start.")
        else:
            batch_df: pd.DataFrame = st.session_state["batch_df"]
            valid_reporter_cols = [c for c in REPORTERS if c in batch_df.columns and batch_df[c].notna().any()]
            bands_df = compute_percentile_bands(batch_df, valid_reporter_cols)
            single_df = st.session_state.get("single_df")

            st.markdown("### Uncertainty Bands (P10 / Median / P90)")
            selected_reporters = st.multiselect(
                "Choose indicators to plot",
                options=valid_reporter_cols,
                default=valid_reporter_cols[:4],
                format_func=lambda c: REPORTER_LABELS.get(c, c),
            )

            for col in selected_reporters:
                st.plotly_chart(
                    plot_percentile_bands(
                        bands_df, col,
                        f"{REPORTER_LABELS.get(col, col)} — Monte Carlo Bands",
                        single_df=single_df,
                    ),
                    use_container_width=True,
                )

            csv_batch = batch_df.to_csv(index=False).encode()
            st.download_button(
                "⬇ Download batch CSV", csv_batch, "batch_results.csv", "text/csv"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 3 — SCENARIO COMPARISON
    # ═══════════════════════════════════════════════════════════════════════
    with tab_compare:
        st.subheader("Scenario Comparison")
        st.caption(
            "Runs all four scenarios with the current agreement switches and shows "
            "side-by-side trajectories."
        )
        run_compare = st.button("▶  Run All 4 Scenarios", type="primary")

        if run_compare:
            with st.spinner("Running 4 scenarios…"):
                scenario_results = run_all_scenarios(params, sim_years)
                st.session_state["scenario_results"] = scenario_results

        if "scenario_results" not in st.session_state:
            st.info("Press **Run All 4 Scenarios** to compare.")
        else:
            sc_results: dict = st.session_state["scenario_results"]

            comp_reporter = st.selectbox(
                "Indicator to compare",
                options=list(REPORTERS.keys()),
                format_func=lambda c: REPORTER_LABELS.get(c, c),
                index=list(REPORTERS.keys()).index("biodiversity_index"),
            )
            st.plotly_chart(
                plot_scenario_comparison(sc_results, comp_reporter),
                use_container_width=True,
            )

            # Final-year table across scenarios
            st.markdown("### Final-year values across scenarios")
            rows = []
            for sc, df in sc_results.items():
                row = {"Scenario": SCENARIO_NAMES[sc]}
                for col in REPORTERS:
                    if col in df.columns and df[col].notna().any():
                        row[REPORTER_LABELS.get(col, col)] = round(df.iloc[-1][col], 1)
                    else:
                        row[REPORTER_LABELS.get(col, col)] = "N/A"
                rows.append(row)
            st.dataframe(pd.DataFrame(rows).set_index("Scenario"), use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 4 — DECISION SUPPORT (RDM + ADAPTIVE PATHWAYS)
    # ═══════════════════════════════════════════════════════════════════════
    with tab_rdm:
        st.subheader("Decision Support")

        col_thr1, col_thr2 = st.columns(2)
        with col_thr1:
            st.markdown("**Adjust thresholds** (index units, baseline = 100):")
        custom_thresholds = {}
        thr_cols = st.columns(3)
        for i, (k, v) in enumerate(DEFAULT_THRESHOLDS.items()):
            with thr_cols[i % 3]:
                custom_thresholds[k] = st.number_input(
                    REPORTER_LABELS.get(k, k), min_value=0.0, max_value=200.0,
                    value=float(v), step=5.0, key=f"thr_{k}",
                )

        st.divider()

        # ── RDM from batch ──
        st.markdown("### Robust Decision Making — Objective Probabilities")
        if "batch_df" not in st.session_state:
            st.info("Run a Monte Carlo batch first (Monte Carlo tab) to see RDM results.")
        else:
            rdm_df = rdm_summary(
                st.session_state["batch_df"],
                thresholds=custom_thresholds,
            )
            if not rdm_df.empty:
                st.plotly_chart(plot_rdm_bar(rdm_df), use_container_width=True)
                st.dataframe(rdm_df.round(3), use_container_width=True)

                rob = rdm_df.iloc[0].get("robustness_score", None)
                if rob is not None and not pd.isna(rob):
                    colour = "green" if rob >= 0.7 else "orange" if rob >= 0.5 else "red"
                    st.markdown(
                        f"**Overall robustness score:** "
                        f":{colour}[{rob:.0%}] of objectives met on average."
                    )

        st.divider()

        # ── Adaptive Pathways ──
        st.markdown("### Adaptive Pathway Triggers")
        if "single_df" not in st.session_state:
            st.info("Run a single simulation first to see adaptive pathway recommendations.")
        else:
            display_adaptive_pathways(
                st.session_state["single_df"], custom_thresholds
            )

        # ── RDM across all scenarios (if comparison ran) ──
        if "scenario_results" in st.session_state:
            st.divider()
            st.markdown("### Scenario Robustness Comparison")
            sc_rdm_rows = []
            for sc, df in st.session_state["scenario_results"].items():
                final_row = df.iloc[-1]
                row = {"Scenario": SCENARIO_NAMES[sc]}
                for k, thr in custom_thresholds.items():
                    if k in df.columns:
                        row[REPORTER_LABELS.get(k, k)] = (
                            "✅" if final_row[k] >= thr else "❌"
                        )
                n_met = sum(
                    1 for k, thr in custom_thresholds.items()
                    if k in df.columns and final_row[k] >= thr
                )
                row["Robustness"] = f"{n_met}/{len(custom_thresholds)}"
                sc_rdm_rows.append(row)
            st.dataframe(
                pd.DataFrame(sc_rdm_rows).set_index("Scenario"),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
