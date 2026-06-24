from __future__ import annotations

"""
Corridor Governance Model — Participatory Simulation Webapp
Three pages: Simulate | Parameters | MCDA
Run with: streamlit run app.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

ROOT = Path(__file__).parent

# Plotly chart config: show toolbar on hover, only the camera (download) button
_PCFG = {"displayModeBar": "hover", "modeBarButtonsToKeep": ["toImage"],
          "displaylogo": False, "toImageButtonOptions": {"format": "png", "scale": 2}}
MODEL_PATH = str(ROOT / "Nlogo_final_model.nlogox")
sys.path.insert(0, str(ROOT))

from simulation.netlogo_runner import run_simulation, PYNETLOGO_AVAILABLE

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Corridor Governance Simulator",
    page_icon="🦌",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
[data-testid="stSidebar"] { min-width:258px; max-width:280px; }
[data-testid="stSidebar"] .block-container { padding-top:0.6rem; }
[data-testid="stSidebar"] label { font-size:0.77rem !important; }
div[data-testid="stPlotlyChart"] { margin-top:-4px !important; margin-bottom:-4px !important; }
.stVerticalBlock { gap:2px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# Reference scenarios (not S2 — those are built by the user)
REF_SCENARIOS: dict[str, dict] = {
    "S1": {
        "label": "S1 — No Action (BAU)",
        "description": "Community retains **informal land access**. All activities continue at baseline intensity. No conservation agreement. Reference trajectory.",
        "params": {"scenario": 1},
        "color": "#6b7280",
    },
    "S3": {
        "label": "S3 — State Protected Area",
        "description": "**State-imposed ban** on all land-based activities from year 2. No compensation. Biodiversity recovers; community collapses.",
        "params": {"scenario": 3},
        "color": "#0d9488",
    },
    "S4": {
        "label": "S4 — Land Privatisation",
        "description": "Land sold to a **private investor**. All community activities banned. Very high emigration. Ecosystem starts degraded.",
        "params": {"scenario": 4},
        "color": "#dc2626",
    },
}

# ECF switch keys → human-readable labels
SWITCH_LABELS: dict[str, str] = {
    "rangers-in-agreement?":             "Community rangers",
    "compensation-enabled?":             "Compensation (hunting / logging)",
    "agreement-market-access?":          "Market access",
    "agreement-education?":              "Education",
    "agreement-selfsustain-incentive?":  "Self-sustenance incentive",
    "agreement-marginal-loss-incentive?":"Marginal-loss cash transfer",
    "agreement-action-incentive?":       "Action bonus incentive",
    "agreement-predator-compensation?":  "Predator damage compensation",
    "agreement-land-tenure?":            "Land tenure rights",
    "agreement-planting?":               "Planting programme",
    "agreement-plot-merging?":           "Plot merging",
    "agreement-grazing-reduction?":      "Grazing reduction",
}

ALL_OFF: dict[str, bool] = {k: False for k in SWITCH_LABELS}

# Named ECF presets for quick loading
S2_PRESETS: dict[str, dict[str, bool]] = {
    "Incentives": {**ALL_OFF,
        "agreement-market-access?": True,
        "agreement-education?": True,
        "agreement-selfsustain-incentive?": True,
    },
    "Financial": {**ALL_OFF,
        "compensation-enabled?": True,
        "agreement-marginal-loss-incentive?": True,
        "agreement-predator-compensation?": True,
    },
    "Financial + Land tenure": {**ALL_OFF,
        "compensation-enabled?": True,
        "agreement-marginal-loss-incentive?": True,
        "agreement-predator-compensation?": True,
        "agreement-land-tenure?": True,
    },
    "Full package": {k: True for k in SWITCH_LABELS},
}

# Colour palette for S2 variants (cycled)
S2_PALETTE = ["#f59e0b","#3b82f6","#8b5cf6","#22c55e","#f97316","#6366f1","#ec4899","#14b8a6","#a16207","#1d4ed8"]

# ── Ecological parameters (applied as post_setup after NetLogo setup()) ────────
ECO_PARAMS: dict[str, dict] = {
    "r-deer":       {"label":"Deer growth rate (r)",        "group":"Growth rates",        "default":0.11, "lo":0.02,"hi":0.30,"step":0.005,"fmt":"%.3f"},
    "r-chamois":    {"label":"Chamois growth rate (r)",     "group":"Growth rates",        "default":0.10, "lo":0.02,"hi":0.30,"step":0.005,"fmt":"%.3f"},
    "r-bear":       {"label":"Bear growth rate (r)",        "group":"Growth rates",        "default":0.05, "lo":0.01,"hi":0.15,"step":0.005,"fmt":"%.3f"},
    "r-broadleaf":  {"label":"Broadleaf growth rate (r)",   "group":"Growth rates",        "default":0.03, "lo":0.01,"hi":0.10,"step":0.005,"fmt":"%.3f"},
    "r-nontarget":  {"label":"Non-target growth rate (r)",  "group":"Growth rates",        "default":0.06, "lo":0.01,"hi":0.15,"step":0.005,"fmt":"%.3f"},
    "K-deer":       {"label":"Deer carrying capacity (K)",  "group":"Carrying capacities", "default":1200, "lo":400, "hi":3000,"step":50,   "fmt":"%.0f"},
    "K-chamois":    {"label":"Chamois carrying cap. (K)",   "group":"Carrying capacities", "default":600,  "lo":200, "hi":1500,"step":50,   "fmt":"%.0f"},
    "K-bear":       {"label":"Bear carrying cap. (K)",      "group":"Carrying capacities", "default":120,  "lo":40,  "hi":300, "step":5,    "fmt":"%.0f"},
    "K-broadleaf":  {"label":"Broadleaf carrying cap. (K)", "group":"Carrying capacities", "default":200,  "lo":80,  "hi":500, "step":10,   "fmt":"%.0f"},
    "K-nontarget":  {"label":"Non-target carrying cap. (K)","group":"Carrying capacities", "default":200,  "lo":80,  "hi":500, "step":10,   "fmt":"%.0f"},
    "pop-deer":     {"label":"Initial deer population",     "group":"Initial populations", "default":400,  "lo":100, "hi":800, "step":10,   "fmt":"%.0f"},
    "pop-chamois":  {"label":"Initial chamois population",  "group":"Initial populations", "default":200,  "lo":50,  "hi":400, "step":10,   "fmt":"%.0f"},
    "pop-bear":     {"label":"Initial bear population",     "group":"Initial populations", "default":40,   "lo":10,  "hi":100, "step":2,    "fmt":"%.0f"},
    "pop-broadleaf":{"label":"Initial broadleaf cover",     "group":"Initial populations", "default":100,  "lo":30,  "hi":200, "step":5,    "fmt":"%.0f"},
    "pop-nontarget":{"label":"Initial non-target pop.",     "group":"Initial populations", "default":100,  "lo":30,  "hi":200, "step":5,    "fmt":"%.0f"},
    "hunt-deer":    {"label":"Initial deer hunt intensity", "group":"Baseline management", "default":1,    "lo":0,   "hi":2,   "step":1,    "fmt":"%.0f"},
    "hunt-chamois": {"label":"Initial chamois hunt intens.","group":"Baseline management", "default":1,    "lo":0,   "hi":2,   "step":1,    "fmt":"%.0f"},
    "hunt-bear":    {"label":"Initial bear hunt intensity", "group":"Baseline management", "default":0,    "lo":0,   "hi":2,   "step":1,    "fmt":"%.0f"},
    "log-broadleaf":{"label":"Initial logging intensity",   "group":"Baseline management", "default":1,    "lo":0,   "hi":2,   "step":1,    "fmt":"%.0f"},
    "agri-intensity":{"label":"Initial agri intensity",     "group":"Baseline management", "default":1,    "lo":0,   "hi":2,   "step":1,    "fmt":"%.0f"},
    "grazing-intensity":{"label":"Initial grazing intens.", "group":"Baseline management", "default":1,    "lo":0,   "hi":2,   "step":1,    "fmt":"%.0f"},
}

# ── Agent behaviour parameters (applied BEFORE setup() so initialise-human uses them)
AGENT_PARAMS: dict[str, dict] = {
    "wta-mean": {"label":"WTA mean",              "group":"Agent behaviour", "default":0.45,"lo":0.10,"hi":0.90,"step":0.01, "fmt":"%.2f"},
    "wta-sd":   {"label":"WTA std dev",           "group":"Agent behaviour", "default":0.20,"lo":0.01,"hi":0.40,"step":0.01, "fmt":"%.2f"},
    "ptl-mean": {"label":"Propensity-to-leave μ", "group":"Agent behaviour", "default":0.08,"lo":0.01,"hi":0.30,"step":0.005,"fmt":"%.3f"},
    "ptl-sd":   {"label":"Propensity-to-leave σ", "group":"Agent behaviour", "default":0.05,"lo":0.005,"hi":0.20,"step":0.005,"fmt":"%.3f"},
    "opp-mean": {"label":"Opportunity percep. μ", "group":"Agent behaviour", "default":0.20,"lo":0.05,"hi":0.60,"step":0.01, "fmt":"%.2f"},
    "opp-sd":   {"label":"Opportunity percep. σ", "group":"Agent behaviour", "default":0.08,"lo":0.01,"hi":0.25,"step":0.005,"fmt":"%.3f"},
}

# ── Income model coefficients (applied as post_setup; used every tick) ─────────
INCOME_PARAMS: dict[str, dict] = {
    "income-investor-boost": {"label":"Investor boost (S2)",      "group":"Income model", "default":3.0,"lo":0.0,"hi":8.0, "step":0.1,"fmt":"%.1f"},
    "income-edu-boost":      {"label":"Education boost",          "group":"Income model", "default":0.5,"lo":0.0,"hi":3.0, "step":0.1,"fmt":"%.1f"},
    "income-market-boost":   {"label":"Market access boost",      "group":"Income model", "default":0.3,"lo":0.0,"hi":2.0, "step":0.05,"fmt":"%.2f"},
    "income-selfsustain":    {"label":"Self-sustain boost",       "group":"Income model", "default":1.5,"lo":0.0,"hi":5.0, "step":0.1,"fmt":"%.1f"},
    "income-marginal-loss":  {"label":"Marginal-loss comp.",      "group":"Income model", "default":1.0,"lo":0.0,"hi":4.0, "step":0.1,"fmt":"%.1f"},
    "income-action-bonus":   {"label":"Action incentive bonus",   "group":"Income model", "default":0.8,"lo":0.0,"hi":3.0, "step":0.1,"fmt":"%.1f"},
    "income-merge-max":      {"label":"Plot-merging boost (max)", "group":"Income model", "default":5.0,"lo":0.5,"hi":10.0,"step":0.5,"fmt":"%.1f"},
    "income-predator-coef":  {"label":"Predator damage coef.",    "group":"Income model", "default":1.5,"lo":0.0,"hi":5.0, "step":0.1,"fmt":"%.1f"},
    "income-s3-penalty":     {"label":"S3 scenario penalty",      "group":"Income model", "default":5.0,"lo":0.0,"hi":12.0,"step":0.5,"fmt":"%.1f"},
}

# Combined dict for Parameters page iteration (agent before income, eco last)
ALL_PARAMS: dict[str, dict] = {**AGENT_PARAMS, **INCOME_PARAMS, **ECO_PARAMS}

MCDA_CRITERIA: dict[str, dict] = {
    "biodiversity_index": {"label":"Biodiversity index",        "dir":1,  "w":20},
    "deer_index":         {"label":"Deer population",           "dir":1,  "w":15},
    "chamois_index":      {"label":"Chamois population",        "dir":1,  "w":15},
    "bear_index":         {"label":"Bear population",           "dir":1,  "w":10},
    "broadleaf_index":    {"label":"Broadleaf forest cover",    "dir":1,  "w":10},
    "income_index":       {"label":"Community income",          "dir":1,  "w":15},
    "human_pop_indexed":  {"label":"Human population",          "dir":1,  "w":10},
    "emigration_rate":    {"label":"Emigration rate (↓ better)","dir":-1, "w":5},
    "pct_accepted":       {"label":"% Accepting agreement",     "dir":1,  "w":0},
}

SPECIES = {
    "deer_index":      ("#A0522D", "Deer"),
    "chamois_index":   ("#228B22", "Chamois"),
    "bear_index":      ("#4169E1", "Bear"),
    "broadleaf_index": ("#2E8B57", "Broadleaf"),
    "nontarget_index": ("#9370DB", "Non-target"),
}

DASHBOARD_METRICS = [
    ("pct_accepted",       "% Accepting Agreement", "%"),
    ("income_index",       "Income (index)",         "index"),
    ("biodiversity_index", "Biodiversity",           "index"),
    ("emigration_rate",    "Emigration Rate (%/yr)", "%/yr"),
    ("human_pop_indexed",  "Human Population",       "index"),
    ("ecosystem_status",   "Ecosystem Status (0–2)", ""),
]

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def _unc_default(v: dict) -> dict:
    d = float(v["default"])
    return {
        "on":   False,
        "dist": "Uniform",
        "lo":   round(d * 0.80, 6),
        "hi":   round(d * 1.20, 6),
        "mean": d,
        "std":  round(max(d * 0.10, float(v["step"])), 6),
        "mode": d,
    }


def _init_state() -> None:
    if "eco_vals" not in st.session_state:
        st.session_state.eco_vals = {k: v["default"] for k, v in ALL_PARAMS.items()}
    if "unc" not in st.session_state:
        st.session_state.unc = {k: _unc_default(v) for k, v in ALL_PARAMS.items()}
    # migrate old unc structure and add any new keys
    for pk, pd_def in ALL_PARAMS.items():
        st.session_state.eco_vals.setdefault(pk, float(pd_def["default"]))
        u = st.session_state.unc.setdefault(pk, _unc_default(pd_def))
        if "dist" not in u:
            d = float(pd_def["default"])
            u.setdefault("dist", "Uniform")
            u.setdefault("mean", d)
            u.setdefault("std",  round(max(d * 0.10, float(pd_def["step"])), 6))
            u.setdefault("mode", d)
    if "ref_includes" not in st.session_state:
        st.session_state.ref_includes = {"S1": True, "S3": False, "S4": False}
    if "builder_sw" not in st.session_state:
        st.session_state.builder_sw = dict(ALL_OFF)
    if "builder_name" not in st.session_state:
        st.session_state.builder_name = "S2 variant 1"
    if "s2_queue" not in st.session_state:
        st.session_state.s2_queue = []
    if "run_results" not in st.session_state:
        st.session_state.run_results = []
    if "mcda_w" not in st.session_state:
        st.session_state.mcda_w = {k: v["w"] for k, v in MCDA_CRITERIA.items()}
    if "show_bands" not in st.session_state:
        st.session_state.show_bands = True

_init_state()

# ══════════════════════════════════════════════════════════════════════════════
# CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def hex_rgba(c: str, a: float) -> str:
    h = c.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"


def _percentiles(results: list, col: str):
    series = [df[col].values for df in results
              if col in df.columns and not df[col].isna().all()]
    if not series:
        return (None,) * 6
    ml = min(len(s) for s in series)
    arr = np.array([s[:ml] for s in series])
    t = np.arange(1, ml + 1)
    return t, *[np.nanpercentile(arr, p, axis=0) for p in (10, 25, 50, 75, 90)]


def _draw_band(fig, t, p10, p25, p50, p75, p90, color,
               name="", showlegend=False, show_unc=True):
    if show_unc:
        kw = dict(line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_trace(go.Scatter(x=t, y=p90, **kw))
        fig.add_trace(go.Scatter(x=t, y=p10, fill="tonexty",
                                 fillcolor=hex_rgba(color, 0.13), **kw))
        fig.add_trace(go.Scatter(x=t, y=p75, **kw))
        fig.add_trace(go.Scatter(x=t, y=p25, fill="tonexty",
                                 fillcolor=hex_rgba(color, 0.32), **kw))
    fig.add_trace(go.Scatter(x=t, y=p50, line=dict(color=color, width=2),
                             name=name, showlegend=showlegend))


def _base_layout(fig, title, ylabel, height):
    fig.update_layout(
        title=dict(text=title, font=dict(size=10), x=0.5, xanchor="center"),
        height=height,
        margin=dict(l=38, r=6, t=32, b=34),
        xaxis=dict(title=dict(text="years", font=dict(size=8)), tickfont=dict(size=8)),
        yaxis=dict(title=dict(text=ylabel, font=dict(size=8)), tickfont=dict(size=8)),
        paper_bgcolor="white", plot_bgcolor="#f8f9fa",
        showlegend=False,
    )


def small_chart_single(results, col, title, color, ylabel, show_unc=True, height=200):
    fig = go.Figure()
    t, p10, p25, p50, p75, p90 = _percentiles(results, col)
    if t is not None:
        _draw_band(fig, t, p10, p25, p50, p75, p90, color, show_unc=show_unc)
    else:
        fig.add_annotation(text="reporter not available", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=9, color="#aaa"))
    _base_layout(fig, title, ylabel, height)
    return fig


def small_chart_multi(run_results, col, title, ylabel, show_unc=True, height=200):
    fig = go.Figure()
    has_data = False
    for exp in run_results:
        t, p10, p25, p50, p75, p90 = _percentiles(exp["results"], col)
        if t is None:
            continue
        # showlegend=False — legend is shown once in the color-key strip, not inside each chart
        _draw_band(fig, t, p10, p25, p50, p75, p90, exp["color"],
                   show_unc=show_unc)
        has_data = True
    if not has_data:
        fig.add_annotation(text="no data", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=9, color="#aaa"))
    _base_layout(fig, title, ylabel, height)
    return fig


def metrics_chart_multi(run_results, show_unc=True, height=660):
    """
    3 × 2 subplot grid for the 6 dashboard metrics.
    Single shared legend — double-click to isolate an experiment across all panels.
    """
    titles = [m[1] for m in DASHBOARD_METRICS]
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=titles,
        vertical_spacing=0.10,
        horizontal_spacing=0.10,
    )
    for mi, (cname, _, ylabel) in enumerate(DASHBOARD_METRICS):
        r, c = mi // 2 + 1, mi % 2 + 1
        first_panel = (mi == 0)          # show legend entry only once per experiment
        for exp in run_results:
            t, p10, p25, p50, p75, p90 = _percentiles(exp["results"], cname)
            if t is None:
                continue
            lg = exp["name"]             # legendgroup key ties all panels together
            kw = dict(line=dict(width=0), showlegend=False,
                      hoverinfo="skip", legendgroup=lg)
            if show_unc:
                fig.add_trace(go.Scatter(x=t, y=p90, **kw), row=r, col=c)
                fig.add_trace(go.Scatter(x=t, y=p10, fill="tonexty",
                                         fillcolor=hex_rgba(exp["color"], 0.13),
                                         **kw), row=r, col=c)
                fig.add_trace(go.Scatter(x=t, y=p75, **kw), row=r, col=c)
                fig.add_trace(go.Scatter(x=t, y=p25, fill="tonexty",
                                         fillcolor=hex_rgba(exp["color"], 0.32),
                                         **kw), row=r, col=c)
            fig.add_trace(go.Scatter(
                x=t, y=p50,
                line=dict(color=exp["color"], width=2),
                name=exp["name"], legendgroup=lg,
                showlegend=first_panel,
            ), row=r, col=c)
        # y-axis label per subplot
        fig.update_yaxes(
            title=dict(text=ylabel, font=dict(size=8)),
            tickfont=dict(size=7), row=r, col=c,
        )
        fig.update_xaxes(
            title=dict(text="years", font=dict(size=8)) if r == 3 else {},
            tickfont=dict(size=7), row=r, col=c,
        )
    fig.update_layout(
        height=height,
        margin=dict(l=40, r=10, t=30, b=70),
        paper_bgcolor="white",
        plot_bgcolor="#f8f9fa",
        legend=dict(
            orientation="h", y=-0.10, x=0.5, xanchor="center",
            font=dict(size=9),
            itemclick="toggle", itemdoubleclick="toggleothers",
        ),
    )
    # apply plot_bgcolor to all subplots
    fig.update_layout({
        f"plot_bgcolor": "#f8f9fa",
        **{f"xaxis{'' if i==0 else i+1}_gridcolor": "#e5e7eb"
           for i in range(6)},
        **{f"yaxis{'' if i==0 else i+1}_gridcolor": "#e5e7eb"
           for i in range(6)},
    })
    return fig


def species_chart(results_or_list, *, multi=False, sp_filter=None,
                  exp_filter=None, show_unc=True, height=540):
    """
    Unified species chart.
    single mode : results_or_list is list[pd.DataFrame] for one experiment.
    multi mode  : results_or_list is list[{name, color, results}].
    sp_filter   : list of SPECIES keys to display (None = all).
    exp_filter  : list of experiment names to display (None = all, multi only).
    show_unc    : draw 10-90 / 25-75 bands.
    Double-click a legend item to isolate; single-click to toggle.
    """
    DASHES = ["solid", "dash", "dot", "dashdot", "longdash"]
    fig = go.Figure()
    visible_sp = sp_filter if sp_filter else list(SPECIES.keys())

    if not multi:
        results = results_or_list
        for col, (sc, sp_name) in SPECIES.items():
            if col not in visible_sp:
                continue
            t, p10, p25, p50, p75, p90 = _percentiles(results, col)
            if t is None:
                continue
            _draw_band(fig, t, p10, p25, p50, p75, p90, sc,
                       name=sp_name, showlegend=True, show_unc=show_unc)
        title = "Target Species (index, baseline = 100)"

    else:
        exps = results_or_list
        if exp_filter:
            exps = [e for e in exps if e["name"] in exp_filter]
        one_exp = (len(exps) == 1)   # single visible experiment → color by species
        for exp in exps:
            for i, (col, (sc, sp_name)) in enumerate(SPECIES.items()):
                if col not in visible_sp:
                    continue
                t, p10, p25, p50, p75, p90 = _percentiles(exp["results"], col)
                if t is None:
                    continue
                color = sc if one_exp else exp["color"]
                label = sp_name if one_exp else f"{exp['name']} — {sp_name}"
                n_before = len(fig.data)
                _draw_band(fig, t, p10, p25, p50, p75, p90, color,
                           name=label, showlegend=True, show_unc=show_unc)
                lg = f"{exp['name']}_{col}"
                for tr in fig.data[n_before:]:
                    tr.legendgroup = lg
                for tr in fig.data[n_before:-1]:
                    tr.showlegend = False
                if not one_exp:
                    fig.data[-1].line.dash = DASHES[i % len(DASHES)]
        title = ("Target Species (index, baseline = 100)" if one_exp
                 else "Target Species — experiments compared")

    n_leg_rows = max(1, len(visible_sp) * (len(exps) if multi and exps else 1) // 3)
    leg_y = -0.06 - 0.07 * n_leg_rows
    fig.update_layout(
        title=dict(text=title, font=dict(size=10), x=0.5, xanchor="center"),
        height=height,
        margin=dict(l=38, r=6, t=32, b=max(60, 24 + 22 * n_leg_rows)),
        xaxis=dict(title=dict(text="years", font=dict(size=8)), tickfont=dict(size=8)),
        yaxis=dict(title=dict(text="index", font=dict(size=8)), tickfont=dict(size=8)),
        legend=dict(orientation="h", yanchor="top", y=leg_y,
                    xanchor="center", x=0.5, font=dict(size=8),
                    itemclick="toggle", itemdoubleclick="toggleothers"),
        paper_bgcolor="white", plot_bgcolor="#f8f9fa",
    )
    return fig


def get_final_median(results, col):
    t, _, _, p50, _, _ = _percentiles(results, col)
    return float(p50[-1]) if t is not None else np.nan


def _sample_one(pk: str, rng: np.random.Generator) -> float:
    u = st.session_state.unc[pk]
    if not u["on"]:
        return float(st.session_state.eco_vals[pk])
    pd_def = ALL_PARAMS[pk]
    hard_lo, hard_hi = float(pd_def["lo"]), float(pd_def["hi"])
    dist = u.get("dist", "Uniform")
    if dist == "Normal":
        v = rng.normal(float(u["mean"]), max(float(u["std"]), 1e-9))
        return float(np.clip(v, hard_lo, hard_hi))
    elif dist == "Triangular":
        lo, mode, hi = float(u["lo"]), float(u["mode"]), float(u["hi"])
        if lo >= hi:
            hi = lo + 1e-9
        mode = float(np.clip(mode, lo, hi))
        return float(rng.triangular(lo, mode, hi))
    else:  # Uniform
        lo, hi = float(u["lo"]), float(u["hi"])
        if lo >= hi:
            hi = lo + 1e-9
        return float(rng.uniform(lo, hi))


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    page = st.radio("Navigation", ["🗺 Simulate", "⚙ Parameters", "📊 MCDA"],
                    label_visibility="collapsed", key="page_radio")
    st.divider()

    # ── Simulate sidebar ──────────────────────────────────────────────────────
    if page == "🗺 Simulate":
        st.info(
            "**1.** Tick the reference scenarios to include as baselines.\n\n"
            "**2.** Build one or more Scenario 2 variants: load a preset or "
            "toggle switches manually, name the variant, then click **+ Add to run list**.\n\n"
            "**3.** Set simulation length, agreement duration, and MC runs.\n\n"
            "**4.** Click **▶ Run** — all experiments run simultaneously."
        )

        # ── Reference scenarios ───────────────────────────────────────────────
        st.markdown("**Reference scenarios**")
        for sk, sd in REF_SCENARIOS.items():
            checked = st.checkbox(
                sd["label"], value=st.session_state.ref_includes[sk],
                key=f"ref_{sk}",
            )
            st.session_state.ref_includes[sk] = checked

        st.divider()

        # ── S2 builder ────────────────────────────────────────────────────────
        st.markdown("**Scenario 2 — ECF agreement**")

        # Preset quick-load buttons (2 per row)
        preset_keys = list(S2_PRESETS.keys())
        for i in range(0, len(preset_keys), 2):
            row_cols = st.columns(2)
            for j, pk in enumerate(preset_keys[i:i+2]):
                if row_cols[j].button(pk, key=f"preset_{pk}", use_container_width=True):
                    preset = S2_PRESETS[pk]
                    st.session_state.builder_sw = dict(preset)
                    # write directly into each checkbox's widget-state key so
                    # the checkboxes reflect the preset on rerun
                    for sw_key, sw_val in preset.items():
                        st.session_state[f"sw_{sw_key}"] = sw_val
                    st.session_state.builder_name = pk
                    st.rerun()

        st.markdown("<span style='font-size:0.74rem;color:#6b7280'>— or set toggles manually —</span>",
                    unsafe_allow_html=True)

        # Switch toggles
        for sw_key, sw_label in SWITCH_LABELS.items():
            new_val = st.checkbox(
                sw_label, value=st.session_state.builder_sw.get(sw_key, False),
                key=f"sw_{sw_key}",
            )
            st.session_state.builder_sw[sw_key] = new_val

        # Name + add
        st.session_state.builder_name = st.text_input(
            "Variant name",
            value=st.session_state.builder_name,
            key="builder_name_input",
            label_visibility="collapsed",
            placeholder="Variant name…",
        )

        n_queued = len(st.session_state.s2_queue)
        if st.button("＋ Add to run list", use_container_width=True, key="add_variant"):
            color = S2_PALETTE[n_queued % len(S2_PALETTE)]
            st.session_state.s2_queue.append({
                "name": st.session_state.builder_name or f"S2 variant {n_queued+1}",
                "switches": dict(st.session_state.builder_sw),
                "color": color,
            })
            next_n = len(st.session_state.s2_queue) + 1
            st.session_state.builder_name = f"S2 variant {next_n}"
            st.rerun()

        # ── Queued variants list ──────────────────────────────────────────────
        if st.session_state.s2_queue:
            st.markdown("<span style='font-size:0.76rem;color:#374151;font-weight:600'>Run list</span>",
                        unsafe_allow_html=True)
            to_remove = None
            for idx, v in enumerate(st.session_state.s2_queue):
                c_dot, c_name, c_del = st.columns([0.15, 0.7, 0.15])
                c_dot.markdown(
                    f"<span style='color:{v['color']};font-size:1.1rem'>●</span>",
                    unsafe_allow_html=True,
                )
                c_name.markdown(
                    f"<span style='font-size:0.76rem'>{v['name']}</span>",
                    unsafe_allow_html=True,
                )
                if c_del.button("✕", key=f"del_v_{idx}", help="Remove"):
                    to_remove = idx
            if to_remove is not None:
                st.session_state.s2_queue.pop(to_remove)
                st.rerun()
        else:
            st.caption("No S2 variants queued yet.")

        st.divider()

        # ── Run settings ──────────────────────────────────────────────────────
        sim_years = st.slider("Simulation years", 10, 50, 30, 5, key="sim_yrs")
        agr_dur   = st.slider("Agreement duration (yrs)", 5, 50, 25, 5, key="agr_dur")
        n_runs    = st.slider("MC runs per experiment", 3, 100, 10, 1, key="n_runs")

        n_total = sum(1 for v in st.session_state.ref_includes.values() if v) + len(st.session_state.s2_queue)
        run_btn = st.button(
            f"▶  Run {n_total} experiment{'s' if n_total != 1 else ''}",
            type="primary", use_container_width=True,
            disabled=(n_total == 0),
        )

        if st.session_state.run_results:
            if st.button("Clear results", key="clr_results"):
                st.session_state.run_results = []
                st.rerun()

    # ── Parameters sidebar ────────────────────────────────────────────────────
    elif page == "⚙ Parameters":
        st.info(
            "Edit ecological, agent-behaviour, and income-model parameters.\n\n"
            "Enable **Uncertain?** on any parameter to sample it from a distribution "
            "in every MC run. Choose **Uniform**, **Normal**, or **Triangular** and "
            "set the bounds. Agent-behaviour params are sampled before setup; "
            "income coefficients are applied after setup."
        )
        if st.button("↺ Reset all to defaults", key="reset_params"):
            st.session_state.eco_vals = {k: v["default"] for k, v in ALL_PARAMS.items()}
            st.session_state.unc = {k: _unc_default(v) for k, v in ALL_PARAMS.items()}
            st.rerun()
        n_unc = sum(1 for u in st.session_state.unc.values() if u["on"])
        st.caption(f"{n_unc} parameter(s) uncertain (sampled in MC)")

    # ── MCDA sidebar ──────────────────────────────────────────────────────────
    elif page == "📊 MCDA":
        st.info(
            "Requires **≥ 2 experiments** from the last simulation run.\n\n"
            "Set a **weight (0–100)** for each criterion below — criteria with "
            "weight 0 are excluded from scoring.\n\n"
            "The page shows: weighted ranking · radar chart · score profile "
            "per criterion with MC bands · ranking across criteria · "
            "weight sensitivity (1 000 Dirichlet draws)."
        )
        n_res = len(st.session_state.run_results)
        if n_res >= 2:
            st.caption(f"{n_res} experiments from last run.")
        else:
            st.caption("Run ≥ 2 experiments in Simulate first.")
        if st.button("Clear results", key="clr_mcda"):
            st.session_state.run_results = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SIMULATE
# ══════════════════════════════════════════════════════════════════════════════
if page == "🗺 Simulate":

    if not PYNETLOGO_AVAILABLE:
        st.error("pynetlogo is not installed. Run: `pip install pynetlogo`")
        st.stop()

    # ── Run button handler ────────────────────────────────────────────────────
    if run_btn:
        new_results: list[dict] = []
        errors: list[str] = []

        # Build experiment list: reference scenarios first, then S2 variants
        experiments_to_run: list[dict] = []
        for sk, sd in REF_SCENARIOS.items():
            if st.session_state.ref_includes.get(sk):
                experiments_to_run.append({
                    "name": sk,
                    "color": sd["color"],
                    "params": {**sd["params"],
                               "simulation-years": sim_years,
                               "agreement-duration": agr_dur,
                               **{k: False for k in SWITCH_LABELS}},
                })
        for v in st.session_state.s2_queue:
            experiments_to_run.append({
                "name": v["name"],
                "color": v["color"],
                "params": {"scenario": 2,
                           "simulation-years": sim_years,
                           "agreement-duration": agr_dur,
                           **v["switches"]},
            })

        total_runs = len(experiments_to_run) * n_runs
        prog = st.progress(0.0, f"Running {total_runs} simulations across {len(experiments_to_run)} experiments…")
        run_count = 0

        for exp in experiments_to_run:
            exp_results = []
            for i in range(n_runs):
                try:
                    rng = np.random.default_rng(i)
                    pre_p  = dict(exp["params"])   # scenario switches etc.
                    post_p = {}
                    for pk in ALL_PARAMS:
                        v = _sample_one(pk, rng)
                        if pk in AGENT_PARAMS:
                            pre_p[pk] = v          # must be set before setup()
                        else:
                            post_p[pk] = v         # set after setup()
                    df, _ = run_simulation(MODEL_PATH, pre_p, post_setup=post_p,
                                          n_ticks=sim_years, seed=i)
                    exp_results.append(df)
                except Exception as e:
                    errors.append(f"{exp['name']} run {i}: {e}")
                run_count += 1
                prog.progress(run_count / total_runs,
                              f"{exp['name']} — run {i+1}/{n_runs}")

            if exp_results:
                new_results.append({"name": exp["name"], "color": exp["color"],
                                    "results": exp_results})

        prog.empty()
        if errors:
            st.error("Some runs failed:\n" + "\n".join(errors[:5]))
        if new_results:
            st.session_state.run_results = new_results

    # ── Results view ──────────────────────────────────────────────────────────
    rr = st.session_state.run_results

    if not rr:
        st.info("Configure experiments in the sidebar, then press **▶ Run**.")
        st.stop()

    single = len(rr) == 1
    exp0   = rr[0]

    # ── View controls ────────────────────────────────────────────────────────
    ctrl_cols = st.columns([1, 4, 4] if not single else [1, 8])
    with ctrl_cols[0]:
        show_unc = st.checkbox("Uncertainty bands", value=st.session_state.show_bands,
                               key="show_bands_cb")
        st.session_state.show_bands = show_unc

    if not single:
        with ctrl_cols[1]:
            all_names = [e["name"] for e in rr]
            exp_filter = st.multiselect(
                "Show experiments", all_names, default=all_names,
                key="exp_filter", label_visibility="collapsed",
                placeholder="Filter experiments…",
            )
            rr_filtered = [e for e in rr if e["name"] in exp_filter] if exp_filter else rr
    else:
        rr_filtered = rr

    # species filter lives above the right column; collect it before layout
    sp_all = list(SPECIES.keys())
    sp_labels = {k: v[1] for k, v in SPECIES.items()}

    # ── Main chart layout ────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2], gap="small")

    with col_right:
        sp_filter = st.multiselect(
            "Show species", sp_all, default=sp_all,
            format_func=lambda k: sp_labels[k],
            key="sp_filter", label_visibility="collapsed",
            placeholder="Filter species…",
        )
        visible_sp = sp_filter if sp_filter else sp_all

        if single:
            fig_sp = species_chart(
                exp0["results"], multi=False,
                sp_filter=visible_sp, show_unc=show_unc,
            )
        else:
            fig_sp = species_chart(
                rr_filtered, multi=True,
                sp_filter=visible_sp, show_unc=show_unc,
            )
        st.plotly_chart(fig_sp, use_container_width=True,
                        config=_PCFG)

    with col_left:
        if single:
            for row_pair in [DASHBOARD_METRICS[i:i+2] for i in range(0, 6, 2)]:
                c1, c2 = st.columns(2, gap="small")
                for widget, (cname, title, ylabel) in zip([c1, c2], row_pair):
                    with widget:
                        st.plotly_chart(
                            small_chart_single(exp0["results"], cname, title,
                                               exp0["color"], ylabel, show_unc=show_unc),
                            use_container_width=True, config=_PCFG,
                        )
        else:
            # Single combined subplot figure — legend supports double-click isolation
            st.plotly_chart(
                metrics_chart_multi(rr_filtered, show_unc=show_unc),
                use_container_width=True, config=_PCFG,
            )

    st.caption("💡 **Double-click** a legend item to isolate it; single-click to toggle.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙ Parameters":
    st.markdown("## Model Parameters & Uncertainty")

    # ── Global uncertainty controls ───────────────────────────────────────────
    st.markdown("#### Uncertainty settings")
    st.caption(
        "Tick **Uncertain?** to activate stochastic sampling for a parameter. "
        "Each MC run draws a new value from the chosen distribution. "
        "**Uniform**: draw uniformly ∈ [Min, Max]. "
        "**Normal**: draw from 𝒩(μ, σ), clipped to the hard parameter bounds. "
        "**Triangular**: draw from Triangular(Min, Mode, Max)."
    )

    ga, gb, gc = st.columns([1, 1, 4])
    if ga.button("Enable all", key="unc_all_on", use_container_width=True):
        for pk in ECO_PARAMS:
            st.session_state.unc[pk]["on"] = True
        st.rerun()
    if gb.button("Disable all", key="unc_all_off", use_container_width=True):
        for pk in ECO_PARAMS:
            st.session_state.unc[pk]["on"] = False
        st.rerun()
    n_unc = sum(1 for u in st.session_state.unc.values() if u["on"])
    gc.markdown(
        f"<span style='font-size:0.84rem;color:#374151'>"
        f"{n_unc} / {len(ECO_PARAMS)} parameters uncertain</span>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Per-group parameter tables ────────────────────────────────────────────
    groups: dict[str, list] = {}
    for k, v in ALL_PARAMS.items():
        groups.setdefault(v["group"], []).append(k)

    HDR_W = [3, 1.8, 0.9, 1.6]
    HDR   = ["Parameter", "Central value", "Uncertain?", "Distribution"]

    for group_name, keys in groups.items():
        st.markdown(f"#### {group_name}")
        hcols = st.columns(HDR_W)
        for col_w, lbl in zip(hcols, HDR):
            col_w.markdown(
                f"<span style='font-size:0.76rem;color:#6b7280;font-weight:600'>{lbl}</span>",
                unsafe_allow_html=True,
            )

        for pk in keys:
            pd_def = ALL_PARAMS[pk]
            u = st.session_state.unc[pk]
            hard_lo = float(pd_def["lo"])
            hard_hi = float(pd_def["hi"])
            step    = float(pd_def["step"])
            fmt     = pd_def["fmt"]

            # main row ────────────────────────────────────────────────────────
            c_lbl, c_val, c_on, c_dist = st.columns(HDR_W)

            with c_lbl:
                st.markdown(
                    f"<span style='font-size:0.82rem'>{pd_def['label']}</span>",
                    unsafe_allow_html=True,
                )

            with c_val:
                new_val = st.number_input(
                    "", key=f"pval_{pk}",
                    value=float(st.session_state.eco_vals[pk]),
                    min_value=hard_lo, max_value=hard_hi,
                    step=step, format=fmt,
                    label_visibility="collapsed",
                )
                st.session_state.eco_vals[pk] = new_val

            with c_on:
                is_on = st.checkbox(
                    "", key=f"unc_on_{pk}",
                    value=u["on"],
                    label_visibility="collapsed",
                )
                u["on"] = is_on

            with c_dist:
                dist_opts = ["Uniform", "Normal", "Triangular"]
                cur_dist  = u.get("dist", "Uniform")
                dist = st.selectbox(
                    "", key=f"unc_dist_{pk}",
                    options=dist_opts,
                    index=dist_opts.index(cur_dist) if cur_dist in dist_opts else 0,
                    disabled=not is_on,
                    label_visibility="collapsed",
                )
                u["dist"] = dist

            # distribution params sub-row (only when uncertain) ───────────────
            if is_on:
                if dist == "Uniform":
                    _, p_lo, p_hi = st.columns([0.4, 3.8, 3.8])
                    with p_lo:
                        lo_c = float(np.clip(u["lo"], hard_lo, new_val))
                        u["lo"] = st.number_input(
                            "Min", key=f"ulo_{pk}",
                            value=lo_c, min_value=hard_lo, max_value=new_val,
                            step=step, format=fmt,
                        )
                    with p_hi:
                        hi_c = float(np.clip(u["hi"], new_val, hard_hi))
                        u["hi"] = st.number_input(
                            "Max", key=f"uhi_{pk}",
                            value=hi_c, min_value=new_val, max_value=hard_hi,
                            step=step, format=fmt,
                        )

                elif dist == "Normal":
                    _, p_mean, p_std = st.columns([0.4, 3.8, 3.8])
                    with p_mean:
                        u["mean"] = st.number_input(
                            "Mean (μ)", key=f"umean_{pk}",
                            value=float(np.clip(u.get("mean", new_val), hard_lo, hard_hi)),
                            min_value=hard_lo, max_value=hard_hi,
                            step=step, format=fmt,
                        )
                    with p_std:
                        max_std = max((hard_hi - hard_lo) / 2, step)
                        u["std"] = st.number_input(
                            "Std dev (σ)", key=f"ustd_{pk}",
                            value=float(np.clip(u.get("std", step * 2), step, max_std)),
                            min_value=step, max_value=max_std,
                            step=step, format=fmt,
                            help=f"Output clipped to [{hard_lo}, {hard_hi}]",
                        )

                elif dist == "Triangular":
                    _, p_lo, p_mode, p_hi = st.columns([0.4, 2.6, 2.6, 2.6])
                    with p_lo:
                        lo_c = float(np.clip(u["lo"], hard_lo, new_val))
                        u["lo"] = st.number_input(
                            "Min", key=f"tlo_{pk}",
                            value=lo_c, min_value=hard_lo, max_value=new_val,
                            step=step, format=fmt,
                        )
                    with p_mode:
                        mode_c = float(np.clip(u.get("mode", new_val), u["lo"], hard_hi))
                        u["mode"] = st.number_input(
                            "Mode (peak)", key=f"tmode_{pk}",
                            value=mode_c, min_value=float(u["lo"]), max_value=hard_hi,
                            step=step, format=fmt,
                        )
                    with p_hi:
                        hi_c = float(np.clip(u["hi"], new_val, hard_hi))
                        u["hi"] = st.number_input(
                            "Max", key=f"thi_{pk}",
                            value=hi_c, min_value=new_val, max_value=hard_hi,
                            step=step, format=fmt,
                        )

        st.markdown("---")




# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MCDA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 MCDA":
    st.markdown("## Multi-Criteria Decision Analysis")

    rr = st.session_state.run_results
    if len(rr) < 2:
        st.info("Run at least **2 experiments** from the Simulate page to enable MCDA.")
        st.stop()

    # ── Raw final-tick medians ────────────────────────────────────────────────
    raw: dict[str, dict] = {}
    for exp in rr:
        raw[exp["name"]] = {crit: get_final_median(exp["results"], crit)
                            for crit in MCDA_CRITERIA}
    df_raw = pd.DataFrame(raw).T
    exp_colors = {exp["name"]: exp["color"] for exp in rr}

    # ── Weight controls ───────────────────────────────────────────────────────
    st.markdown("#### Criterion weights")
    st.caption("Weighted-sum of min-max normalised final-tick median values.")
    w_cols = st.columns(len(MCDA_CRITERIA))
    weights: dict[str, float] = {}
    for col_w, (crit, meta) in zip(w_cols, MCDA_CRITERIA.items()):
        with col_w:
            w = st.number_input(
                meta["label"], min_value=0, max_value=100,
                value=int(st.session_state.mcda_w[crit]), step=5,
                key=f"w_{crit}",
                help="Higher = better" if meta["dir"] == 1 else "Lower = better",
            )
            weights[crit] = float(w)
            st.session_state.mcda_w[crit] = w

    total_w = sum(weights.values()) or 1.0

    # ── Normalise & score ─────────────────────────────────────────────────────
    df_norm = df_raw.copy()
    for crit, meta in MCDA_CRITERIA.items():
        if crit not in df_norm.columns:
            continue
        vmin, vmax = df_norm[crit].min(), df_norm[crit].max()
        if vmax > vmin:
            df_norm[crit] = ((df_norm[crit] - vmin) / (vmax - vmin)
                             if meta["dir"] == 1
                             else (vmax - df_norm[crit]) / (vmax - vmin))
        else:
            df_norm[crit] = 0.5

    crits_in = [c for c in MCDA_CRITERIA if c in df_norm.columns]
    df_norm["Score"] = df_norm[crits_in].apply(
        lambda row: sum(row[c] * weights[c] / total_w for c in crits_in), axis=1
    )
    df_norm["Rank"] = df_norm["Score"].rank(ascending=False).astype(int)
    df_norm = df_norm.sort_values("Score", ascending=False)

    st.divider()

    # ── Ranking table + bar chart ─────────────────────────────────────────────
    c_tbl, c_bar = st.columns([3, 2], gap="medium")
    with c_tbl:
        st.markdown("#### Ranking")
        disp = df_norm[["Rank", "Score"] + crits_in].rename(
            columns={"Score": "Score", "Rank": "Rank",
                     **{c: MCDA_CRITERIA[c]["label"] for c in crits_in}}
        )
        st.dataframe(
            disp.style.format({"Score": "{:.3f}",
                               **{MCDA_CRITERIA[c]["label"]: "{:.2f}" for c in crits_in}}),
            use_container_width=True,
        )

    with c_bar:
        st.markdown("#### Weighted score")
        fig_bar = go.Figure(go.Bar(
            x=df_norm.index.tolist(), y=df_norm["Score"].tolist(),
            marker_color=[exp_colors.get(n, "#888") for n in df_norm.index],
            text=[f"{v:.3f}" for v in df_norm["Score"]], textposition="outside",
        ))
        fig_bar.update_layout(height=300, margin=dict(l=10,r=10,t=30,b=10),
                              yaxis=dict(range=[0,1.15]),
                              paper_bgcolor="white", plot_bgcolor="#f8f9fa")
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})

    # ── Radar ─────────────────────────────────────────────────────────────────
    st.markdown("#### Normalised performance per criterion")
    crit_labels = [MCDA_CRITERIA[c]["label"] for c in crits_in]
    fig_radar = go.Figure()
    for exp in rr:
        vals = [float(df_norm.loc[exp["name"], c])
                if exp["name"] in df_norm.index and c in df_norm.columns else 0
                for c in crits_in]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=crit_labels + [crit_labels[0]],
            fill="toself", fillcolor=hex_rgba(exp["color"], 0.15),
            line=dict(color=exp["color"], width=2), name=exp["name"],
        ))
    fig_radar.update_layout(height=420,
                            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                            legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
                            margin=dict(l=40,r=40,t=20,b=60),
                            paper_bgcolor="white")
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar":False})

    # ── Dirichlet Monte Carlo: win frequency + global sensitivity ────────────
    st.divider()
    st.markdown("#### Weight sensitivity — 1 000 Dirichlet samples")
    st.caption(
        "Random weight vectors are drawn from a Dirichlet distribution (all criteria equally likely). "
        "**Win frequency**: how often each experiment ranks #1. "
        "**Global sensitivity** (Spearman ρ): rank correlation between each criterion's sampled weight "
        "and each experiment's score — shows which criteria drive the ranking."
    )

    nc = len(crits_in)
    rng_s = np.random.default_rng(42)
    N_MC = 1000

    # accumulate per-sample weights and scores
    mc_w_arr  = np.zeros((N_MC, nc))          # shape (N_MC, n_criteria)
    mc_sc_arr = np.zeros((N_MC, len(rr)))     # shape (N_MC, n_experiments)
    win_cnt   = {exp["name"]: 0 for exp in rr}
    sec_cnt   = {exp["name"]: 0 for exp in rr}
    exp_names = [exp["name"] for exp in rr]

    for s in range(N_MC):
        raw_w = rng_s.dirichlet(np.ones(nc))
        mc_w_arr[s] = raw_w
        tw = raw_w.sum()
        row_scores: dict[str, float] = {}
        for ei, exp in enumerate(rr):
            if exp["name"] not in df_norm.index:
                continue
            sc = sum(float(df_norm.loc[exp["name"], c]) * raw_w[ci]
                     for ci, c in enumerate(crits_in)) / tw
            mc_sc_arr[s, ei] = sc
            row_scores[exp["name"]] = sc
        ranked = sorted(row_scores, key=row_scores.get, reverse=True)
        if ranked:          win_cnt[ranked[0]] += 1
        if len(ranked) > 1: sec_cnt[ranked[1]] += 1

    pct_win = {k: v / 10 for k, v in win_cnt.items()}
    pct_sec = {k: v / 10 for k, v in sec_cnt.items()}

    # ── Win-frequency bars ────────────────────────────────────────────────────
    c_w1, c_w2 = st.columns(2, gap="medium")
    for col_w, pct, label in [(c_w1, pct_win, "Wins #1 (%)"),
                               (c_w2, pct_sec, "Ranks #2 (%)")]:
        with col_w:
            fig_w = go.Figure(go.Bar(
                x=list(pct.keys()), y=list(pct.values()),
                marker_color=[exp_colors.get(n, "#888") for n in pct],
                text=[f"{v:.0f}%" for v in pct.values()], textposition="outside",
            ))
            fig_w.update_layout(
                title=dict(text=label, font=dict(size=11), x=0.5, xanchor="center"),
                height=300, margin=dict(l=10, r=10, t=36, b=10),
                yaxis=dict(title="%", range=[0, 115]),
                paper_bgcolor="white", plot_bgcolor="#f8f9fa",
            )
            st.plotly_chart(fig_w, use_container_width=True,
                            config=_PCFG)

    # ── Score profile per criterion (parallel-coordinates style) ──────────────
    st.divider()
    st.markdown("#### Score profile per criterion")
    _unc_pc = st.checkbox("Show uncertainty bands", value=True, key="mcda_unc_pc")
    st.caption(
        "Each line is a scenario's normalised score (0 = worst, 1 = best) across "
        "active criteria. Bands show 10–90 % (light) and 25–75 % (dark) of MC run "
        "outcomes, normalised with the same min-max bounds as the median."
    )

    _crit_labels = [MCDA_CRITERIA[c]["label"] for c in crits_in]

    # per-criterion normalization bounds (same as df_norm, derived from df_raw)
    _bounds: dict[str, tuple] = {}   # crit → (vmin, vmax, dir)
    for _crit in crits_in:
        _meta = MCDA_CRITERIA[_crit]
        _col_vals = df_raw[_crit].dropna()
        _vmin = float(_col_vals.min()) if len(_col_vals) else 0.0
        _vmax = float(_col_vals.max()) if len(_col_vals) else 1.0
        _bounds[_crit] = (_vmin, _vmax, _meta["dir"])

    def _norm_clip(v, vmin, vmax, d):
        if vmax == vmin:
            return 0.5
        s = (v - vmin) / (vmax - vmin)
        return float(np.clip(s if d == 1 else 1 - s, 0.0, 1.0))

    fig_pc = go.Figure()
    _shown = set()

    for exp in rr:
        if exp["name"] not in df_norm.index:
            continue
        # collect final-tick percentile scores per criterion
        _p10s, _p25s, _p50s, _p75s, _p90s = [], [], [], [], []
        for _crit in crits_in:
            _vmin, _vmax, _dir = _bounds[_crit]
            _ts, _a, _b, _m, _c2, _d = _percentiles(exp["results"], _crit)
            if _ts is None:
                for _lst in (_p10s, _p25s, _p50s, _p75s, _p90s):
                    _lst.append(None)
                continue
            # direction flip means p10/p90 swap their role — take outer envelope
            _n10 = _norm_clip(float(_a[-1]), _vmin, _vmax, _dir)
            _n25 = _norm_clip(float(_b[-1]), _vmin, _vmax, _dir)
            _n50 = _norm_clip(float(_m[-1]), _vmin, _vmax, _dir)
            _n75 = _norm_clip(float(_c2[-1]), _vmin, _vmax, _dir)
            _n90 = _norm_clip(float(_d[-1]), _vmin, _vmax, _dir)
            _p10s.append(min(_n10, _n90))   # outer low (handles dir flip)
            _p25s.append(min(_n25, _n75))   # inner low
            _p50s.append(_n50)
            _p75s.append(max(_n25, _n75))   # inner high
            _p90s.append(max(_n10, _n90))   # outer high

        _lg = exp["name"]
        _show1st = _lg not in _shown
        _shown.add(_lg)
        _kw0 = dict(legendgroup=_lg, showlegend=False,
                    mode="lines", hoverinfo="skip", line=dict(width=0))

        if _unc_pc:
            # outer band p10-p90
            fig_pc.add_trace(go.Scatter(
                x=_crit_labels, y=_p90s, **_kw0))
            fig_pc.add_trace(go.Scatter(
                x=_crit_labels, y=_p10s,
                fill="tonexty", fillcolor=hex_rgba(exp["color"], 0.13),
                **_kw0))
            # inner band p25-p75
            fig_pc.add_trace(go.Scatter(
                x=_crit_labels, y=_p75s, **_kw0))
            fig_pc.add_trace(go.Scatter(
                x=_crit_labels, y=_p25s,
                fill="tonexty", fillcolor=hex_rgba(exp["color"], 0.32),
                **_kw0))

        # median line
        fig_pc.add_trace(go.Scatter(
            x=_crit_labels, y=_p50s,
            mode="lines+markers",
            line=dict(color=exp["color"], width=2),
            marker=dict(size=6, color=exp["color"]),
            name=exp["name"], legendgroup=_lg,
            showlegend=_show1st,
        ))

    fig_pc.update_layout(
        height=360,
        margin=dict(l=40, r=10, t=10, b=90),
        yaxis=dict(range=[0, 1], title="score (0–1)",
                   tickfont=dict(size=9), gridcolor="#e0e0e0"),
        xaxis=dict(tickangle=-30, tickfont=dict(size=9), gridcolor="#e0e0e0"),
        paper_bgcolor="white", plot_bgcolor="#f8f9fa",
        legend=dict(font=dict(size=9), orientation="h",
                    yanchor="bottom", y=1.02, xanchor="left", x=0,
                    itemclick="toggle", itemdoubleclick="toggleothers"),
    )
    st.plotly_chart(fig_pc, use_container_width=True,
                    config=_PCFG)

    # ── Bump chart: ranking across criteria ───────────────────────────────────
    st.markdown("#### Ranking across criteria")
    st.caption(
        "Each line is a scenario. The y-axis shows its rank on each criterion "
        "(1 = best). A scenario that stays near the top across all criteria is "
        "robust; one that swings widely has trade-offs."
    )

    # per-criterion ranks (higher normalised score → rank 1)
    _ranked_by_crit: dict[str, dict[str, int]] = {}
    for _crit in crits_in:
        _sc = {
            exp["name"]: float(df_norm.loc[exp["name"], _crit])
            for exp in rr if exp["name"] in df_norm.index
        }
        _sorted = sorted(_sc, key=_sc.get, reverse=True)
        _ranked_by_crit[_crit] = {nm: rnk + 1 for rnk, nm in enumerate(_sorted)}

    _n_exp = sum(1 for exp in rr if exp["name"] in df_norm.index)

    fig_bump = go.Figure()
    for exp in rr:
        if exp["name"] not in df_norm.index:
            continue
        _ranks = [_ranked_by_crit[c].get(exp["name"], _n_exp) for c in crits_in]
        fig_bump.add_trace(go.Scatter(
            x=_crit_labels,
            y=_ranks,
            mode="lines+markers",
            name=exp["name"],
            line=dict(color=exp["color"], width=2),
            marker=dict(size=9, color=exp["color"]),
        ))

    fig_bump.update_layout(
        height=360,
        margin=dict(l=40, r=10, t=10, b=100),
        yaxis=dict(
            autorange="reversed",
            tickvals=list(range(1, _n_exp + 1)),
            title="Rank",
            tickfont=dict(size=9),
            gridcolor="#e0e0e0",
        ),
        xaxis=dict(tickangle=-30, tickfont=dict(size=9), gridcolor="#e0e0e0"),
        paper_bgcolor="white",
        plot_bgcolor="#f8f9fa",
        legend=dict(font=dict(size=9), orientation="h",
                    yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig_bump, use_container_width=True,
                    config=_PCFG)
