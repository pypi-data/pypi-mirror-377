# src/normet/utils/metrics.py
from __future__ import annotations

from typing import Callable, Optional, List, Dict, Union

import numpy as np
import pandas as pd
from scipy import stats as _stats

from .logging import get_logger

log = get_logger(__name__)

__all__ = ["Stats", "modStats"]

# ---------------------------------------------------------------------
# Low-level metrics on arrays
# ---------------------------------------------------------------------

def _fac2(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    """
    Fraction of predictions within a factor of 2 of observations (FAC2).

    FAC2 = mean( 0.5 <= y_pred / y_true <= 2 )
    Notes:
        - We guard against division by zero by adding a tiny epsilon to y_true.
        - Only finite ratios are used; if none are finite, returns NaN.
    """
    epsilon = 1e-9
    ratio = np.divide(
        y_pred,
        y_true + epsilon,
        out=np.full_like(y_pred, np.nan, dtype=float),
        where=np.isfinite(y_true) & (y_true != 0),
    )
    mask = np.isfinite(ratio)
    if not np.any(mask):
        return np.nan
    r = ratio[mask]
    return float(np.mean((r >= 0.5) & (r <= 2.0)))


def _stats_from_arrays(y_pred: np.ndarray, y_true: np.ndarray, statistic: List[str]) -> pd.DataFrame:
    """
    Compute a set of scalar statistics from two 1D arrays.

    Parameters
    ----------
    y_pred : np.ndarray
        Predicted values (same length as y_true).
    y_true : np.ndarray
        Observed (ground-truth) values.
    statistic : List[str]
        A list of metric names to compute. Supported keys:
        {"n","FAC2","MB","MGE","NMB","NMGE","RMSE","r","COE","IOA","R2"}.

    Returns
    -------
    pandas.DataFrame
        Single-row DataFrame containing the requested metrics.
        If "r" is requested, also includes "p_level" with significance stars.
    """
    # Keep only rows where both arrays are finite
    mask = np.isfinite(y_pred) & np.isfinite(y_true)
    yhat = np.asarray(y_pred, dtype=float)[mask]
    yobs = np.asarray(y_true, dtype=float)[mask]

    n = yhat.size
    if n == 0:
        # If no valid pairs, return NaNs for requested metrics.
        keys = set(statistic)
        if "r" in statistic:
            keys |= {"p_level"}
        out = {k: np.nan for k in keys}
        if "n" in statistic:
            out["n"] = 0
        return pd.DataFrame([out])

    diff = yhat - yobs
    adiff = np.abs(diff)

    res: Dict[str, Union[float, int, str]] = {}

    # Count
    if "n" in statistic:
        res["n"] = int(n)

    # Factor-of-two accuracy
    if "FAC2" in statistic:
        res["FAC2"] = _fac2(yhat, yobs)

    # Mean bias / Mean absolute error / RMSE
    if "MB" in statistic:
        res["MB"] = float(np.mean(diff))
    if "MGE" in statistic:
        res["MGE"] = float(np.mean(adiff))
    if "RMSE" in statistic:
        res["RMSE"] = float(np.sqrt(np.mean(diff * diff)))

    # Normalized bias / error (sum-based)
    sum_obs = float(np.sum(yobs))
    if "NMB" in statistic:
        res["NMB"] = float(np.sum(diff) / sum_obs) if sum_obs != 0.0 else np.nan
    if "NMGE" in statistic:
        res["NMGE"] = float(np.sum(adiff) / sum_obs) if sum_obs != 0.0 else np.nan

    # Coefficient of efficiency (COE) & Index of agreement (IOA)
    denom_abs_obs = float(np.sum(np.abs(yobs - np.mean(yobs))))
    if "COE" in statistic:
        res["COE"] = float(1.0 - (np.sum(adiff) / denom_abs_obs)) if denom_abs_obs != 0.0 else np.nan
    if "IOA" in statistic:
        lhs = float(np.sum(adiff))
        rhs = float(2.0 * denom_abs_obs)
        if rhs == 0.0 and lhs == 0.0:
            res["IOA"] = 1.0
        elif rhs == 0.0:
            res["IOA"] = np.nan
        else:
            # Common bounded formulation
            res["IOA"] = float(1.0 - lhs / rhs) if lhs <= rhs else float(rhs / lhs - 1.0)

    # Correlation and p-value (also used for R^2)
    r_val = np.nan
    p_val = np.nan
    if ("r" in statistic) or ("R2" in statistic):
        try:
            r_val, p_val = _stats.pearsonr(yhat, yobs)
        except Exception:
            r_val, p_val = (np.nan, np.nan)

    # Pearson correlation with significance stars
    if "r" in statistic:
        res["r"] = float(r_val)
        # Significance stars based on two-sided p-value:
        #   "" (ns), "+" (p<0.1), "*" (p<0.05), "**" (p<0.01), "***" (p<0.001)
        if not np.isfinite(p_val) or p_val >= 0.1:
            res["p_level"] = ""
        elif p_val >= 0.05:
            res["p_level"] = "+"
        elif p_val >= 0.01:
            res["p_level"] = "*"
        elif p_val >= 0.001:
            res["p_level"] = "**"
        else:
            res["p_level"] = "***"

    # Coefficient of determination
    if "R2" in statistic:
        res["R2"] = float(r_val * r_val) if np.isfinite(r_val) else np.nan

    # Ensure all requested keys exist (and p_level if r is requested)
    keys_needed = set(statistic)
    if "r" in statistic:
        keys_needed |= {"p_level"}
    for k in keys_needed:
        res.setdefault(k, np.nan)

    return pd.DataFrame([res])


# ---------------------------------------------------------------------
# Public APIs
# ---------------------------------------------------------------------

_DEFAULT_STATS: List[str] = [
    "n", "FAC2", "MB", "MGE", "NMB", "NMGE", "RMSE", "r", "COE", "IOA", "R2"
]


def Stats(
    df: pd.DataFrame,
    mod: str = "value_predict",
    obs: str = "value",
    statistic: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Compute requested statistics from two DataFrame columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing columns with predictions and observations.
    mod : str, default "value_predict"
        Column name with model predictions.
    obs : str, default "value"
        Column name with ground-truth observations.
    statistic : List[str] | None
        Which metrics to compute. If None, a comprehensive default set is used.

    Returns
    -------
    pandas.DataFrame
        Single-row DataFrame with the requested statistics.
    """
    if statistic is None:
        statistic = _DEFAULT_STATS

    # Friendly validation for missing columns
    missing = [c for c in (mod, obs) if c not in df.columns]
    if missing:
        raise ValueError(f"Stats: columns not found in DataFrame: {missing}")

    arr = df[[mod, obs]].to_numpy()
    mask = np.isfinite(arr).all(axis=1)
    y_pred = arr[mask, 0].astype(float, copy=False)
    y_true = arr[mask, 1].astype(float, copy=False)
    return _stats_from_arrays(y_pred, y_true, statistic)


def modStats(
    df: pd.DataFrame,
    model: object,
    subset: Optional[str] = None,
    statistic: Optional[List[str]] = None,
    predictor: Optional[Callable[[object, pd.DataFrame], np.ndarray]] = None,
) -> pd.DataFrame:
    """
    Predict with a model on a DataFrame and compute statistics.

    Parameters
    ----------
    df : pandas.DataFrame
        Prepared dataset. Must contain target column "value".
        If a "set" column exists and `subset` is specified, only that subset is evaluated.
    model : object
        Trained model compatible with the package's `ml_predict` interface.
    subset : {"training","testing","all"} | None
        Which split to evaluate. If None and "set" exists, returns one row
        per split plus "all".
    statistic : List[str] | None
        Metrics to compute; defaults to a comprehensive set.
    predictor : callable(model, df) -> np.ndarray | None
        Optional override for the prediction function. If None, uses
        `..model.predict.ml_predict`.

    Returns
    -------
    pandas.DataFrame
        Tidy DataFrame of metrics with a "set" column indicating which slice
        was scored.
    """
    if statistic is None:
        statistic = _DEFAULT_STATS

    # Lazy import to avoid potential circular imports
    if predictor is None:
        from ..model.predict import ml_predict as _ml_predict
        predict_fn = _ml_predict
    else:
        predict_fn = predictor

    def _one(df_in: pd.DataFrame, tag: str) -> pd.DataFrame:
        y_pred = predict_fn(model, df_in)
        y_true = df_in["value"].to_numpy()
        st = _stats_from_arrays(y_pred, y_true, statistic)
        st["set"] = tag
        return st

    if subset is not None:
        # Evaluate only a specific subset ("training", "testing", or "all")
        if subset != "all":
            if "set" not in df.columns:
                raise ValueError("DataFrame has no 'set' column but a `subset` was requested.")
            df_use = df[df["set"] == subset]
        else:
            df_use = df
        return _one(df_use, subset)

    # subset=None: compute per split (if present) and overall "all"
    if "set" not in df.columns:
        return _one(df, "all")

    pieces: List[pd.DataFrame] = []
    for s in pd.unique(df["set"]):
        pieces.append(_one(df[df["set"] == s], s))
    pieces.append(_one(df, "all"))
    return pd.concat(pieces, ignore_index=True)
