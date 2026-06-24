from __future__ import annotations

"""
Monte Carlo / batch runner.

Samples uncertain numeric parameters uniformly within user-supplied [min, max]
ranges, runs the NetLogo model N times, and writes results to
outputs/batch_results.csv.

Each row in the output has columns: run_id, tick, <all reporter columns>,
<all sampled parameter columns>.
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path

from simulation.netlogo_runner import run_simulation, SWITCH_PARAMS

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
BATCH_CSV = OUTPUT_DIR / "batch_results.csv"


def _sample_params(
    base_params: dict,
    uncertain_ranges: dict[str, tuple[float, float]],
    rng: np.random.Generator,
) -> dict:
    """Return a copy of base_params with uncertain params sampled uniformly."""
    sampled = base_params.copy()
    for name, (lo, hi) in uncertain_ranges.items():
        if name in SWITCH_PARAMS:
            # Boolean: treat lo/hi as probabilities of being True
            sampled[name] = bool(rng.random() < (lo + hi) / 2)
        else:
            sampled[name] = float(rng.uniform(lo, hi))
    return sampled


def run_batch(
    model_path: str,
    base_params: dict,
    uncertain_ranges: dict[str, tuple[float, float]],
    n_runs: int,
    n_ticks: int,
    gui: bool = False,
    seed: int = 42,
    progress_callback=None,
) -> pd.DataFrame:
    """
    Run the model `n_runs` times, sampling uncertain parameters each run.

    Parameters
    ----------
    model_path : str
    base_params : dict       Fixed parameters applied every run.
    uncertain_ranges : dict  {param_name: (min, max)} — overrides base_params.
    n_runs : int
    n_ticks : int
    gui : bool
    seed : int               Master RNG seed for reproducibility.
    progress_callback : callable(run_index, n_runs) | None
        Called after each completed run so UIs can show a progress bar.

    Returns
    -------
    pd.DataFrame with columns: run_id, tick, <reporters>, <sampled params>
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    all_frames: list[pd.DataFrame] = []
    all_warnings: list[str] = []

    for run_idx in range(n_runs):
        run_seed = int(rng.integers(0, 2**31))
        sampled_params = _sample_params(base_params, uncertain_ranges, rng)

        try:
            df, warnings = run_simulation(
                model_path=model_path,
                params=sampled_params,
                n_ticks=n_ticks,
                gui=gui,
                seed=run_seed,
            )
            df["run_id"] = run_idx
            # Attach sampled param values as columns for post-hoc analysis
            for k, v in sampled_params.items():
                if k in uncertain_ranges:
                    df[f"param_{k}"] = v
            all_frames.append(df)
            all_warnings.extend(warnings)
        except Exception as exc:
            all_warnings.append(f"Run {run_idx} failed: {exc}")

        if progress_callback:
            progress_callback(run_idx + 1, n_runs)

    if not all_frames:
        raise RuntimeError("All batch runs failed. Check warnings.")

    result = pd.concat(all_frames, ignore_index=True)
    result.to_csv(BATCH_CSV, index=False)
    return result


def compute_percentile_bands(
    batch_df: pd.DataFrame,
    reporter_cols: list[str],
) -> pd.DataFrame:
    """
    Aggregate batch results into median / p10 / p90 bands per tick.

    Returns a DataFrame with columns:
        tick, <col>_p10, <col>_median, <col>_p90   for each reporter col.
    """
    rows = []
    for tick, grp in batch_df.groupby("tick"):
        row: dict = {"tick": tick}
        for col in reporter_cols:
            if col in grp.columns:
                vals = grp[col].dropna()
                row[f"{col}_p10"]    = float(np.percentile(vals, 10)) if len(vals) else float("nan")
                row[f"{col}_median"] = float(np.percentile(vals, 50)) if len(vals) else float("nan")
                row[f"{col}_p90"]    = float(np.percentile(vals, 90)) if len(vals) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)
