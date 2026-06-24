from __future__ import annotations

"""
NetLogo single-run wrapper using pyNetLogo.

Reporter names map to NetLogo to-report procedures in the .nlogox model.
If a reporter is missing or renamed, the run will still complete — missing
reporters appear as NaN columns in the output DataFrame.

NOTE: pyNetLogo typically expects a .nlogo file. The helper `prepare_model_path`
converts the .nlogox (NetLogo 7 XML) to a temporary .nlogo file automatically.
"""

import os
import sys
from pathlib import Path
import pandas as pd

# ── Ensure Java 17 is visible before JPype/pyNetLogo starts the JVM ─────────
_TEMURIN = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
if sys.platform == "win32" and Path(_TEMURIN).exists():
    os.environ.setdefault("JAVA_HOME", _TEMURIN)
    _bin = str(Path(_TEMURIN) / "bin")
    if _bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _bin + os.pathsep + os.environ.get("PATH", "")

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
    Return the absolute path to the NetLogo model file, ready for pyNetLogo.

    NetLogo 7 reads .nlogox natively via its load-model command, so we pass
    it directly.  We use Path.as_posix() to produce C:/Users/... style paths;
    str(Path) on Windows gives backslashes that Java's path resolver prefixes
    with a spurious leading '/', breaking load-model.
    """
    p = Path(nlogox_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Model file not found: {p}")
    # as_posix() → "C:/Users/..." which Java handles correctly on Windows.
    return p.as_posix()


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
    # Streamlit runs user code in worker threads that have no Java ClassLoader.
    # Setting it here prevents NullPointerException inside NetLogo's resource loading.
    try:
        import jpype
        if jpype.isJVMStarted():
            thread = jpype.JClass("java.lang.Thread")
            loader = jpype.JClass("java.lang.ClassLoader")
            ct = thread.currentThread()
            if ct.getContextClassLoader() is None:
                ct.setContextClassLoader(loader.getSystemClassLoader())
    except Exception:
        pass

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
