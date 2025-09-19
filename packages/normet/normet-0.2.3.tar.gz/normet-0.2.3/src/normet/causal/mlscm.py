# src/normet/causal/mlscm.py
from __future__ import annotations

import re
from typing import List, Optional, Dict, Any

import pandas as pd

from ..model.train import build_model
from ..model.predict import ml_predict
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = ["mlscm"]


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


def mlscm(
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
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Machine Learning Augmented Synthetic Control Method (ML-SCM).

    This function estimates a synthetic counterfactual outcome for a treated unit
    by learning a mapping from donor units' outcomes to the treated unit’s
    outcomes during the pre-treatment period. The mapping is estimated using
    AutoML (FLAML or H2O), and then used to predict synthetic outcomes in both
    the pre- and post-treatment periods. The difference between observed and
    synthetic outcomes represents the estimated treatment effect.

    Parameters
    ----------
    df : pandas.DataFrame
        Long-format panel with columns [date_col, unit_col, outcome_col].
    date_col : str
        Name of the datetime-like column. Must be convertible to ``pd.to_datetime``.
    outcome_col : str
        Name of the outcome variable column.
    unit_col : str
        Column containing unit identifiers (treated and donor units).
    treated_unit : str
        Identifier of the treated unit.
    donors : list of str
        List of donor unit identifiers to construct the synthetic control.
    cutoff_date : str
        Treatment cutoff date in ``YYYY-MM-DD`` format. Pre-period is strictly
        before this timestamp.
    backend : {"flaml", "h2o"}, default="flaml"
        AutoML backend to use for model training.
    model_config : dict, optional
        Backend-specific training configuration passed to the AutoML backend
        (e.g., time budget, estimators, evaluation metric).
    split_method : {"random","chronological"}, default="random"
        Strategy for splitting pre-treatment data into train/test when training
        the AutoML model. Ignored if ``fraction=1.0``.
    fraction : float, default=1.0
        Training fraction of pre-treatment data (0–1). ``1.0`` uses all available
        pre-treatment observations for training.
    seed : int, default=7_654_321
        Random seed for reproducibility.
    verbose : bool, default=True
        Whether to emit progress logs during training and prediction.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by ``date_col`` with the following columns:

        - ``observed`` : Observed outcome of the treated unit.
        - ``synthetic`` : Predicted counterfactual outcome of the treated unit.
        - ``effect`` : Difference ``observed − synthetic``.

    Raises
    ------
    ValueError
        If treated unit is missing from the panel, or no valid donor units exist.
    FileNotFoundError
        If backend requires files or dependencies not found on the system.
    RuntimeError
        If AutoML training fails unexpectedly.
    ImportError
        If the chosen backend (``flaml`` or ``h2o``) is not installed.

    Notes
    -----
    - Column names are sanitized to avoid issues with AutoML backends (e.g.,
      FLAML/sklearn restrictions on symbols in column names).
    - The synthetic control is estimated using only the pre-treatment period,
      then extrapolated to the full timeline.
    - The AutoML backend is responsible for model selection and hyperparameter
      tuning; behavior depends on ``backend`` and ``model_config`` settings.

    Examples
    --------
    >>> out = mlscm(
    ...     df=data,
    ...     date_col="date",
    ...     outcome_col="Y",
    ...     unit_col="city",
    ...     treated_unit="treated_city",
    ...     donors=["donor1","donor2","donor3"],
    ...     cutoff_date="2015-01-01",
    ...     backend="flaml",
    ...     model_config={"time_budget": 60, "metric": "r2"},
    ...     verbose=True,
    ... )
    >>> out.head()
                     observed  synthetic    effect
    date
    2014-01-01         10.5       10.7     -0.2
    2014-01-02         12.0       11.8      0.2
    """
    # --- Prepare panel (wide: date x units) ---
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    cutoff_ts = pd.to_datetime(cutoff_date)

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

    # Sanitize names
    col_map = _build_safe_map(list(panel.columns))
    panel_safe = panel.rename(columns=col_map)
    treated_safe = col_map[treated_unit]
    donors_safe = [col_map[u] for u in donor_units]

    # Pre-treatment
    pre_panel_safe = panel_safe.loc[panel_safe.index < cutoff_ts]

    log.info(
        "ML-SCM training on pre-period: %d dates, donors=%d (backend=%s)",
        pre_panel_safe.shape[0], len(donors_safe), backend,
    )

    # Train model
    _, model = build_model(
        df=pre_panel_safe,
        value=treated_safe,
        backend=backend,
        feature_names=donors_safe,
        split_method=split_method,
        fraction=fraction,
        model_config=model_config,
        seed=seed,
        verbose=verbose,
    )

    # Predict synthetic
    synth_all = ml_predict(model, panel_safe[donors_safe])
    synth_all = pd.Series(synth_all, index=panel_safe.index, name="synthetic")

    # Output
    out = pd.DataFrame(
        {
            "observed": panel[treated_unit],
            "synthetic": synth_all,
        }
    )
    out["effect"] = out["observed"] - out["synthetic"]
    out.index.name = date_col

    log.info("ML-SCM completed: %d timestamps (%s..%s)", len(out), out.index.min(), out.index.max())
    return out
