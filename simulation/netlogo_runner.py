from __future__ import annotations

"""
NetLogo single-run wrapper using pyNetLogo.

Reporter names map to NetLogo to-report procedures in the .nlogox model.
If a reporter is missing or renamed, the run will still complete — missing
reporters appear as NaN columns in the output DataFrame.

NOTE: pyNetLogo typically expects a .nlogo file. The helper `prepare_model_path`
converts the .nlogox (NetLogo 7 XML) to a temporary .nlogo file automatically.
"""

import tempfile
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd

try:
    import pynetlogo
    PYNETLOGO_AVAILABLE = True
except ImportError:
    PYNETLOGO_AVAILABLE = False

# ── Reporter map: Python key → NetLogo reporter name ────────────────────────
REPORTERS = {
    "deer_index":        "report-pop-deer",
    "chamois_index":     "report-pop-chamois",
    "bear_index":        "report-pop-bear",
    "broadleaf_index":   "report-pop-broadleaf",
    "nontarget_index":   "report-pop-nontarget",
    "biodiversity_index": "report-total-biodiversity",
    "income_index":      "report-community-income",
    "human_pop_indexed": "report-human-pop-indexed",
    "emigration_rate":   "report-emigration-rate",
    "pct_accepted":      "report-pct-accepted",
    "ecosystem_status":  "report-ecosystem-status",
    "hunt_pressure":     "report-hunt-pressure",
    "predator_damage":   "report-predator-damage",
    "agreement_active":  "report-agreement-active",
}

# Display-friendly labels used by the Streamlit app
REPORTER_LABELS = {
    "deer_index":        "Deer Population (index)",
    "chamois_index":     "Chamois Population (index)",
    "bear_index":        "Brown Bear Population (index)",
    "broadleaf_index":   "Broadleaf Forest Cover (index)",
    "nontarget_index":   "Non-target Species (index)",
    "biodiversity_index": "Biodiversity Index",
    "income_index":      "Community Income Index",
    "human_pop_indexed": "Human Population (index)",
    "emigration_rate":   "Emigration Rate (%/yr)",
    "pct_accepted":      "% Community Accepting Agreement",
    "ecosystem_status":  "Ecosystem Status (0–2)",
    "hunt_pressure":     "Hunting Pressure",
    "predator_damage":   "Predator Damage Index",
    "agreement_active":  "Agreement Active (0/1)",
}

# All NetLogo boolean switches (must be set as 'true'/'false', not 1/0)
SWITCH_PARAMS = {
    "rangers-in-agreement?",
    "compensation-enabled?",
    "agreement-market-access?",
    "agreement-education?",
    "agreement-selfsustain-incentive?",
    "agreement-marginal-loss-incentive?",
    "agreement-action-incentive?",
    "agreement-predator-compensation?",
    "agreement-land-tenure?",
    "agreement-grazing-reduction?",
    "agreement-planting?",
    "agreement-plot-merging?",
}


def prepare_model_path(nlogox_path: str) -> str:
    """
    Convert a .nlogox (NetLogo 7 XML) file to a temporary .nlogo file that
    pyNetLogo can load.  Returns the path of the created .nlogo file.

    The temp file is placed next to the original so NetLogo can resolve any
    relative paths inside the model.
    """
    nlogox_path = Path(nlogox_path)
    nlogo_path = nlogox_path.with_suffix(".nlogo")

    if nlogo_path.exists():
        return str(nlogo_path)

    try:
        tree = ET.parse(nlogox_path)
        root = tree.getroot()
        code_el = root.find("code")
        if code_el is None:
            raise ValueError("No <code> element found in .nlogox")
        code = code_el.text or ""
    except ET.ParseError as exc:
        raise RuntimeError(f"Cannot parse {nlogox_path}: {exc}") from exc

    # Minimal .nlogo structure: code section + empty sections separated by
    # the NetLogo section delimiter.
    nlogo_content = (
        code.strip()
        + "\n@#$#@#$#@\n"  # interface section (empty — we set params via commands)
        + "@#$#@#$#@\n"    # info section
        + "@#$#@#$#@\n"    # turtle shapes
        + "NetLogo 7.0.0\n"
        + "@#$#@#$#@\n"    # behaviorspace
        + "@#$#@#$#@\n"    # system dynamics
        + "@#$#@#$#@\n"    # quick help
        + "@#$#@#$#@\n"    # bitmap section
        + "@#$#@#$#@\n"    # link shapes
        + "0\n"            # model settings
        + "@#$#@#$#@\n"
        + "0\n"
        + "@#$#@#$#@\n"
    )

    nlogo_path.write_text(nlogo_content, encoding="utf-8")
    return str(nlogo_path)


def _set_params(nl, params: dict) -> list[str]:
    """Send parameter values to a live NetLogo workspace. Returns warning list."""
    warnings = []
    for name, value in params.items():
        try:
            if name in SWITCH_PARAMS or isinstance(value, bool):
                nl_value = "true" if value else "false"
            else:
                nl_value = str(value)
            nl.command(f"set {name} {nl_value}")
        except Exception as exc:
            warnings.append(f"Could not set '{name}': {exc}")
    return warnings


def run_simulation(
    model_path: str,
    params: dict,
    n_ticks: int = 30,
    gui: bool = False,
    seed: int | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Run the NetLogo model for `n_ticks` steps.

    Returns
    -------
    df : pd.DataFrame
        One row per tick; columns are the keys of REPORTERS.
    warnings : list[str]
        Non-fatal issues (missing reporters, parameter set failures).
    """
    if not PYNETLOGO_AVAILABLE:
        raise ImportError(
            "pynetlogo is not installed. Run: pip install pynetlogo"
        )

    model_path = prepare_model_path(model_path)
    warnings: list[str] = []

    nl = pynetlogo.NetLogoLink(gui=gui)
    try:
        nl.load_model(model_path)

        if seed is not None:
            nl.command(f"random-seed {seed}")

        warnings += _set_params(nl, params)
        nl.command("setup")

        # Detect which reporters are actually available
        available = {}
        missing = []
        for col, reporter in REPORTERS.items():
            try:
                nl.report(reporter)
                available[col] = reporter
            except Exception:
                missing.append(reporter)
                warnings.append(f"Reporter '{reporter}' not found — column '{col}' will be NaN")

        records = []
        for tick in range(1, n_ticks + 1):
            nl.command("go")
            row: dict = {"tick": tick}
            for col, reporter in REPORTERS.items():
                if col in available:
                    try:
                        row[col] = float(nl.report(reporter))
                    except Exception:
                        row[col] = float("nan")
                else:
                    row[col] = float("nan")
            records.append(row)

    finally:
        nl.kill_workspace()

    return pd.DataFrame(records), warnings
