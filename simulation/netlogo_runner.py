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
import tarfile
import urllib.request
from pathlib import Path
import pandas as pd

# ── Windows: point at local Temurin 17 ───────────────────────────────────────
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

# ── NetLogo home resolution (Linux / Streamlit Cloud) ────────────────────────
_NL_VERSION   = "7.0.3"
_NL_TARBALL   = f"NetLogo-{_NL_VERSION}-64.tgz"
_NL_CACHE_DIR = Path(os.environ.get("NETLOGO_CACHE_DIR", "/tmp/netlogo_install"))

# Download URL candidates (tried in order).  User can override the first slot
# by setting NETLOGO_DOWNLOAD_URL in Streamlit secrets.
_NL_URLS = [
    u for u in [
        os.environ.get("NETLOGO_DOWNLOAD_URL"),
        f"https://downloads.netlogo.org/{_NL_VERSION}/{_NL_TARBALL}",
        f"https://ccl.northwestern.edu/netlogo/{_NL_VERSION}/{_NL_TARBALL}",
    ] if u
]

_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def _find_extracted(cache_dir: Path) -> str | None:
    """Return the first subdirectory that looks like a NetLogo installation."""
    for d in sorted(cache_dir.iterdir()):
        if d.is_dir() and "netlogo" in d.name.lower():
            # Verify it actually contains the NetLogo jar
            if any(d.rglob("netlogo*.jar")):
                return str(d)
    return None


def _ensure_netlogo_home() -> str | None:
    """
    Return the NetLogo installation directory for pyNetLogo.

    Priority:
      1. NETLOGO_HOME env var (fastest; set in Streamlit secrets)
      2. Common Linux install paths or already-extracted /tmp cache
      3. Download tarball from GitHub / CCL (once per container cold-start)
    On Windows returns None so pyNetLogo auto-detects from the registry.
    """
    if sys.platform == "win32":
        return None

    # 1. Explicit env var
    env_home = os.environ.get("NETLOGO_HOME", "")
    if env_home and Path(env_home).exists():
        return env_home

    # 2. Common paths + previously extracted cache
    static = [Path("/usr/local/netlogo"), Path("/opt/netlogo"), Path.home() / "netlogo"]
    for c in static:
        if c.exists():
            return str(c)

    if _NL_CACHE_DIR.exists():
        found = _find_extracted(_NL_CACHE_DIR)
        if found:
            return found

    # 3. Download and extract
    _NL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tarball = _NL_CACHE_DIR / _NL_TARBALL

    if not tarball.exists():
        last_err: Exception | None = None
        for url in _NL_URLS:
            try:
                print(f"[netlogo_runner] downloading from {url} …", flush=True)
                _download(url, tarball)
                break
            except Exception as exc:
                print(f"[netlogo_runner]   ↳ failed: {exc}", flush=True)
                last_err = exc
                tarball.unlink(missing_ok=True)
        else:
            raise RuntimeError(
                f"Could not download NetLogo {_NL_VERSION}. Last error: {last_err}\n"
                "Set NETLOGO_DOWNLOAD_URL in Streamlit secrets to a direct .tgz link, "
                "or set NETLOGO_HOME to an already-extracted NetLogo directory."
            )

    if tarball.exists():
        print(f"[netlogo_runner] extracting …", flush=True)
        with tarfile.open(tarball, "r:gz") as tf:
            tf.extractall(_NL_CACHE_DIR)

    found = _find_extracted(_NL_CACHE_DIR)
    if found:
        return found

    raise RuntimeError(
        f"Extracted NetLogo tarball but could not locate the installation directory "
        f"under {_NL_CACHE_DIR}. Set NETLOGO_HOME explicitly in Streamlit secrets."
    )

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
    post_setup: dict | None = None,   # globals to override AFTER setup() (K, r, pop values)
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

    nl = pynetlogo.NetLogoLink(gui=gui, netlogo_home=_ensure_netlogo_home())
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
        if post_setup:
            warnings += _set_params(nl, post_setup)

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
