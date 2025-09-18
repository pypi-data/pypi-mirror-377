# src/normet/scm/mlascm.py
from __future__ import annotations

import re
from typing import List, Optional, Dict, Any

import pandas as pd

from ..model.train import build_model
from ..model.predict import ml_predict
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = ["mlascm"]


def _safe_name(name: str) -> str:
    """
    Convert arbitrary column/unit names into FLAML/sklearn-friendly tokens.

    Rules:
      - Replace non-word characters with underscores.
      - Collapse multiple underscores.
      - Strip leading/trailing underscores.
      - If the name starts with a digit, prefix with '_'.
    """
    if name is None:
        return ""
    s = re.sub(r"\W+", "_", str(name))
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "_"
    if s[0].isdigit():
        s = "_" + s
    return s


def _build_safe_map(cols: List[str]) -> Dict[str, str]:
    """
    Build a one-to-one mapping {original -> safe}, resolving collisions
    by appending numeric suffixes.
    """
    out: Dict[str, str] = {}
    used: Dict[str, int] = {}
    for c in cols:
        base = _safe_name(c)
        cand = base
        k = 1
        while cand in used:
            k += 1
            cand = f"{base}_{k}"
        used[cand] = 1
        out[c] = cand
    return out


def mlascm(
    df: pd.DataFrame,
    date_col: str,
    outcome_col: str,
    unit_col: str,
    treated_unit: str,
    donors: List[str],
    cutoff_date: str,
    backend: str = "flaml",
    model_config: Optional[Dict[str, Any]] = None,
    split_method: str = "random",
    fraction: float = 1.0,
    seed: int = 7_654_321,
) -> pd.DataFrame:
    """
    Machine Learning Augmented Synthetic Control Method (ML-ASCM).

    Learn a mapping from donors' pre-treatment outcomes to the treated unit's
    pre-treatment outcomes using an AutoML backend (FLAML or H2O), and predict
    post-treatment counterfactual outcomes (synthetic control).

    This implementation sanitizes column names to avoid training/prediction
    mismatches with FLAML/sklearn pipelines (e.g., names like '2+26 cities').

    Parameters
    ----------
    df : pandas.DataFrame
        Long-format panel with columns [date_col, unit_col, outcome_col].
    date_col : str
        Name of the date column (convertible to datetime).
    outcome_col : str
        Name of the outcome variable.
    unit_col : str
        Column containing unit identifiers (treated and donors).
    treated_unit : str
        Identifier of the treated unit.
    donors : List[str]
        Donor unit identifiers used to build the synthetic control.
    cutoff_date : str
        Treatment cutoff date in "YYYY-MM-DD" format.
    backend : {"flaml","h2o"}, optional
        AutoML backend to use. Default "flaml".
    model_config : dict, optional
        Backend-specific training configuration.
    split_method : str, optional
        Train/test split method for the internal model. Default "random".
    fraction : float, optional
        Training fraction (0–1). Default 1.0 (use all pre-treatment data).
    seed : int, optional
        Random seed. Default 7_654_321.

    Returns
    -------
    pandas.DataFrame
        Indexed by `date_col` with columns:
          - observed : observed outcome of the treated unit (original name)
          - synthetic : synthetic counterfactual predicted by the model
          - effect : observed − synthetic
    """
    # --- Prepare panel (wide: date x units) ---
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    cutoff_ts = pd.to_datetime(cutoff_date)

    # Only keep treated + donors to avoid spurious collisions
    union_units = list(set(donors) | {treated_unit})
    panel = (
        work[work[unit_col].isin(union_units)]
        .pivot_table(index=date_col, columns=unit_col, values=outcome_col, aggfunc="mean")
        .sort_index()
    )

    if treated_unit not in panel.columns:
        raise ValueError(f"Treated unit '{treated_unit}' not found in panel.")

    donor_units = [u for u in donors if u in panel.columns and u != treated_unit]
    if not donor_units:
        raise ValueError("No valid donors available.")

    # --- Sanitize column names to be sklearn/FLAML friendly (and consistent) ---
    # Build a stable mapping across treated + donors
    col_map = _build_safe_map(list(panel.columns))
    panel_safe = panel.rename(columns=col_map)
    treated_safe = col_map[treated_unit]
    donors_safe = [col_map[u] for u in donor_units]

    # --- Split pre/post on the *sanitized* panel ---
    pre_panel_safe = panel_safe.loc[panel_safe.index < cutoff_ts]

    log.info(
        "ML-ASCM training on pre-period: %d dates, donors=%d (backend=%s)",
        pre_panel_safe.shape[0], len(donors_safe), backend,
    )

    # --- Train ML model on pre donors -> treated ---
    # build_model calls prepare_data internally (handles DatetimeIndex → 'date', renaming target to 'value', splitting, etc.)
    _, model = build_model(
        df=pre_panel_safe,
        value=treated_safe,
        backend=backend,
        feature_names=donors_safe,
        split_method=split_method,
        fraction=fraction,
        model_config=model_config,
        seed=seed,
    )

    # --- Predict synthetic series on the *full* sanitized panel ---
    synth_all = ml_predict(model, panel_safe[donors_safe])
    synth_all = pd.Series(synth_all, index=panel_safe.index, name="synthetic")

    # --- Combine with ORIGINAL observed column name for user-facing output ---
    out = pd.DataFrame(
        {
            "observed": panel[treated_unit],  # original name preserved here
            "synthetic": synth_all,
        }
    )
    out["effect"] = out["observed"] - out["synthetic"]
    out.index.name = date_col

    log.info("ML-ASCM completed: %d timestamps (%s..%s)", len(out), out.index.min(), out.index.max())
    return out
