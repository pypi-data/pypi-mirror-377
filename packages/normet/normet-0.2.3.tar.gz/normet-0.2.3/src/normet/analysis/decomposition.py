# src/normet/analysis/decomposition.py
from __future__ import annotations

import os
import time
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple

from .normalise import normalise
from ..utils.features import extract_features
from ..model.train import build_model
from ..utils.prepare import process_date, add_date_variables
from ..utils.logging import get_logger

log = get_logger(__name__)


def _effective_cores(n_cores: Optional[int]) -> int:
    """Resolve parallel worker count (>=1)."""
    return max(1, n_cores if n_cores is not None else (os.cpu_count() or 2) - 1)


def decom_emi(
    df: Optional[pd.DataFrame] = None,
    model: Optional[object] = None,
    value: str = "value",
    backend: str = "flaml",
    feature_names: Optional[List[str]] = None,
    split_method: str = "random",
    fraction: float = 0.75,
    model_config: Optional[Dict[str, Any]] = None,
    n_samples: int = 300,
    seed: int = 7654321,
    n_cores: Optional[int] = None,
    memory_save: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Decompose a time series into emission-related components by progressively
    freezing time-related variables during resampling.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset. Must include a datetime column (or DatetimeIndex) and
        the target column.
    model : object, optional
        Pre-trained FLAML or H2O model. If None, a new model is trained.
    value : str, default="value"
        Target column name (will be aliased to "value" internally).
    backend : {"flaml","h2o"}, default="flaml"
        AutoML backend to use if training is required.
    feature_names : List[str], optional
        Predictor variables (including time vars if needed).
    split_method : str, default="random"
        Data split strategy if training.
    fraction : float, default=0.75
        Training fraction if training.
    model_config : dict, optional
        Extra backend-specific config for AutoML.
    n_samples : int, default=300
        Number of resamples in each `normalise` run.
    seed : int, default=7654321
        Random seed.
    n_cores : int, optional
        Parallel workers for `normalise`. Default all cores - 1.
    memory_save : bool, default=False
        Use memory-efficient path in `normalise`.
    verbose : bool, default=True
        If True log progress at INFO level, otherwise DEBUG.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by date with columns:
          - observed       : raw observed values
          - base           : fully resampled baseline
          - date_unix      : contribution from timestamp trend
          - day_julian     : contribution from seasonal (day-of-year) pattern
          - weekday        : contribution from weekday pattern
          - hour           : contribution from diurnal pattern
          - emi_total      : recomposed emission-driven series
          - emi_noise      : residual high-frequency noise around base
          - emi_base       : long-term mean emission baseline
    """
    if df is None:
        raise ValueError("`df` must be provided.")
    if value is None:
        raise ValueError("`value` (target column name) must be provided.")

    # Ensure we have a 'date' column
    df_work = process_date(df.copy()) if "date" not in df.columns else df.copy()
    if "date" not in df_work.columns:
        raise ValueError("Could not find or create a 'date' column. Ensure `process_date(df)` is available.")

    if value not in df_work.columns:
        raise ValueError(f"`df` does not contain the target column '{value}'.")

    # Keep observed as user's original name; alias to 'value' for pipeline
    observed_series = df_work[value].copy()
    if value != "value":
        df_work = df_work.rename(columns={value: "value"})

    # Clean rows & sort
    mask_valid = df_work["date"].notna() & df_work["value"].notna()
    df_work = df_work.loc[mask_valid].sort_values("date").reset_index(drop=True)
    observed_series = observed_series.loc[mask_valid].reset_index(drop=True)

    # Add time vars if requested but missing
    if feature_names:
        need_time = [v for v in ["date_unix", "day_julian", "weekday", "hour"]
                     if v in feature_names and v not in df_work.columns]
        if need_time:
            try:
                df_work = add_date_variables(df_work)
                (log.info if verbose else log.debug)("Generated time variables: %s", need_time)
            except Exception:
                log.warning("Could not generate some time features: %s", need_time, exc_info=False)

    # Train if needed
    if model is None:
        if not feature_names:
            raise ValueError("When `model` is None you must provide `feature_names` for training.")
        (log.info if verbose else log.debug)(
            "Training model via backend='%s' with features=%d...", backend, len(feature_names)
        )
        df_work, model = build_model(
            df=df_work,
            value="value",
            backend=backend,
            feature_names=feature_names,
            split_method=split_method,
            fraction=fraction,
            model_config=model_config,
            seed=seed,
            n_cores=n_cores,
            verbose=verbose,
        )

    # Determine model features to use
    try:
        model_feats = [str(c) for c in extract_features(model)]
    except Exception:
        if not feature_names:
            raise ValueError("Cannot infer model features; please provide `feature_names`.")
        model_feats = [str(c) for c in feature_names]

    model_feats = [c for c in model_feats if c in df_work.columns]
    if not model_feats:
        raise ValueError("No valid model features found in the provided `df` for decomposition.")

    # Base output
    result = (
        pd.DataFrame({"date": df_work["date"].to_numpy(), "observed": observed_series.to_numpy()})
        .set_index("date")
        .sort_index()
    )

    # Decomposition order (present time vars + conceptual base)
    time_vars_order = ["base", "date_unix", "day_julian", "weekday", "hour"]
    present_time_vars = ["base"] + [v for v in time_vars_order[1:] if v in model_feats and v in df_work.columns]

    n_cores_eff = _effective_cores(n_cores)

    start = time.time()
    total = len(present_time_vars)

    for i, var_to_exclude in enumerate(present_time_vars, start=1):
        # Freeze var by excluding it from resampling
        resample_vars = [v for v in model_feats if v != var_to_exclude and v != "value"]

        elapsed = time.time() - start
        eta = (elapsed / max(i - 1, 1)) * (total - (i - 1)) if i > 1 else None
        eta_str = "" if eta is None else (
            f" | ETA: {eta:.1f}s" if eta < 60 else f" | ETA: {eta/60:.1f}m" if eta < 3600 else f" | ETA: {eta/3600:.1f}h"
        )
        (log.info if verbose else log.debug)("%s: Decomposing %s%s", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), var_to_exclude, eta_str)

        df_norm = normalise(
            df=df_work,
            model=model,
            feature_names=model_feats,
            variables_resample=resample_vars,
            n_samples=n_samples,
            replace=True,
            aggregate=True,
            seed=seed,
            n_cores=n_cores_eff,
            weather_df=None,
            memory_save=memory_save,
            verbose=False,
        )
        if "normalised" not in df_norm.columns:
            log.exception("`normalise` did not return 'normalised' column (aggregate=True).")
            raise RuntimeError("`normalise` must return a DataFrame with column 'normalised' when aggregate=True.")

        result[var_to_exclude] = df_norm.reindex(result.index)["normalised"].to_numpy()

    # Recompose (no base mean inside date_unix; emi_base separate)
    result["emi_total"] = result.get("hour", result["observed"])

    for a, b, out in [
        ("hour", "weekday", "hour"),
        ("weekday", "day_julian", "weekday"),
        ("day_julian", "date_unix", "day_julian"),
        ("date_unix", "base", "date_unix"),
    ]:
        if a in result.columns and b in result.columns:
            result[out] = result[a] - result[b]

    base_mean = float(result["base"].mean())
    result["emi_noise"] = result["base"] - base_mean
    result["emi_base"] = base_mean
    del result['base']

    return result


def decom_met(
    df: Optional[pd.DataFrame] = None,
    model: Optional[object] = None,
    value: str = "value",
    backend: str = "flaml",
    feature_names: Optional[List[str]] = None,
    split_method: str = "random",
    fraction: float = 0.75,
    model_config: Optional[Dict[str, Any]] = None,
    n_samples: int = 300,
    seed: int = 7654321,
    importance_ascending: bool = False,
    n_cores: Optional[int] = None,
    memory_save: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Decompose a time series into meteorological contributions ranked by model
    feature importance.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset. Must include a datetime column (or DatetimeIndex) and
        the target column.
    model : object, optional
        Pre-trained FLAML or H2O model. If None, a new model is trained.
    value : str, default="value"
        Target column name (will be aliased to "value" internally).
    backend : {"flaml","h2o"}, default="flaml"
        AutoML backend to use if training is required.
    feature_names : List[str], optional
        Predictor variables (excluding time vars for contributions).
    split_method : str, default="random"
        Data split strategy if training.
    fraction : float, default=0.75
        Training fraction if training.
    model_config : dict, optional
        Extra backend-specific config for AutoML.
    n_samples : int, default=300
        Number of resamples in each `normalise` run.
    seed : int, default=7654321
        Random seed.
    importance_ascending : bool, default=False
        If True, sort features ascending by importance.
    n_cores : int, optional
        Parallel workers for `normalise`. Default all cores - 1.
    memory_save : bool, default=False
        Use memory-efficient path in `normalise`.
    verbose : bool, default=True
        If True log progress at INFO level, otherwise DEBUG.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by date with columns:
          - observed     : raw observed values
          - emi_total    : baseline with all meteorology resampled
          - <feature_i>  : contribution of each meteorological variable (ordered)
          - met_total    : observed - emi_total
          - met_base     : long-term mean of met_total
          - met_noise    : residual unexplained meteorological noise
    """
    if df is None:
        raise ValueError("`df` must be provided.")
    if value is None:
        raise ValueError("`value` (target column name) must be provided.")

    # Ensure 'date'
    if "date" not in df.columns:
        df = process_date(df)
    df = df[df["date"].notna()].sort_values("date").reset_index(drop=True)

    if value not in df.columns:
        raise ValueError(f"`df` does not contain the target column '{value}'.")
    observed_series = df[value].copy()

    df_work = df.copy()
    if value != "value":
        df_work = df_work.rename(columns={value: "value"})

    # Add time vars if needed
    def _maybe_add_time_vars(frame: pd.DataFrame) -> pd.DataFrame:
        time_vars = ["date_unix", "day_julian", "weekday", "hour"]
        need = [v for v in time_vars if (feature_names and v in feature_names) and v not in frame.columns]
        if need:
            try:
                frame = add_date_variables(frame)
                (log.info if verbose else log.debug)("Generated time variables: %s", need)
            except Exception:
                log.warning("Missing time features not generated: %s", need, exc_info=False)
        return frame

    df_work = _maybe_add_time_vars(df_work)

    # Train if needed
    if model is None:
        if not feature_names:
            raise ValueError("When `model` is None you must provide `feature_names` for training.")
        (log.info if verbose else log.debug)(
            "Training model via backend='%s' with features=%d...", backend, len(feature_names)
        )
        df_work, model = build_model(
            df=df_work,
            value="value",
            backend=backend,
            feature_names=feature_names,
            split_method=split_method,
            fraction=fraction,
            model_config=model_config,
            seed=seed,
            verbose=verbose,
        )

    # Feature order by importance
    try:
        feat_sorted = extract_features(model, importance_ascending=importance_ascending)
    except Exception:
        if not feature_names:
            raise ValueError("Cannot infer model features; please provide `feature_names`.")
        feat_sorted = list(feature_names)

    feat_sorted = [f for f in feat_sorted if f in df_work.columns]
    if not feat_sorted:
        raise ValueError("No valid model features found in `df`.")

    # Exclude time variables from the meteorological contribution set
    time_vars = {"hour", "weekday", "day_julian", "date_unix"}
    contrib_candidates = [f for f in feat_sorted if f not in time_vars]

    # Base frame
    result = (
        pd.DataFrame({"date": df_work["date"].to_numpy(), "observed": observed_series.to_numpy()})
        .set_index("date")
        .sort_index()
    )

    n_cores_eff = _effective_cores(n_cores)

    # Decomposition order: first 'emi_total' (all met resampled), then freeze each met feature
    decomp_order = ["emi_total"] + contrib_candidates[:]
    resample_vars = contrib_candidates[:]

    start = time.time()
    total = len(decomp_order)
    tmp: Dict[str, np.ndarray] = {}

    for i, var in enumerate(decomp_order, start=1):
        if var != "emi_total" and var in resample_vars:
            resample_vars = [v for v in resample_vars if v != var]

        elapsed = time.time() - start
        eta = (elapsed / max(i - 1, 1)) * (total - (i - 1)) if i > 1 else None
        eta_str = "" if eta is None else (
            f" | ETA: {eta:.1f}s" if eta < 60 else f" | ETA: {eta/60:.1f}m" if eta < 3600 else f" | ETA: {eta/3600:.1f}h"
        )
        (log.info if verbose else log.debug)("%s: Decomposing %s%s", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), var, eta_str)

        df_norm = normalise(
            df=df_work,
            model=model,
            feature_names=feat_sorted,
            variables_resample=resample_vars,
            n_samples=n_samples,
            replace=True,
            aggregate=True,
            seed=seed,
            n_cores=n_cores_eff,
            weather_df=None,
            memory_save=memory_save,
            verbose=False,
        )
        if "normalised" not in df_norm.columns:
            log.exception("`normalise` did not return 'normalised' column (aggregate=True).")
            raise RuntimeError("`normalise` must return a DataFrame with column 'normalised' when aggregate=True.")

        tmp[var] = df_norm.reindex(result.index)["normalised"].to_numpy()

    # Compose outputs
    result["emi_total"] = tmp["emi_total"]

    # Per-feature contributions as chained differences
    prev_key = "emi_total"
    for feat in contrib_candidates:
        result[feat] = tmp[feat] - tmp[prev_key]
        prev_key = feat

    # met_total, met_base, met_noise
    result["met_total"] = result["observed"] - result["emi_total"]
    result["met_base"] = float(result["met_total"].mean())
    contrib_sum = result[contrib_candidates].sum(axis=1) if contrib_candidates else 0.0
    result["met_noise"] = result["met_total"] - (result["met_base"] + contrib_sum)

    return result
