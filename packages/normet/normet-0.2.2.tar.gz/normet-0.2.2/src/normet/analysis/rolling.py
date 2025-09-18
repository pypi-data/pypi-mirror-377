# src/normet/analysis/rolling.py
from __future__ import annotations

import os
import time
import pandas as pd
from typing import List, Optional

from ..utils.prepare import process_date, add_date_variables
from ..model.train import build_model
from .normalise import normalise
from ..utils.logging import get_logger

log = get_logger(__name__)


def rolling(
    df: Optional[pd.DataFrame] = None,
    model: Optional[object] = None,
    value: str = "value",
    backend: str = "flaml",
    feature_names: Optional[List[str]] = None,
    variables_resample: Optional[List[str]] = None,
    split_method: str = "random",
    fraction: float = 0.75,
    model_config: Optional[dict] = None,
    n_samples: int = 300,
    window_days: int = 14,
    rolling_every: int = 7,
    seed: int = 7654321,
    n_cores: Optional[int] = None,
    memory_save: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Apply rolling-window normalisation across a time series.

    Each window trains (or reuses) a model and applies deweathering by resampling
    specified predictors. This allows the normalised series to capture
    time-varying model fits in a moving-window fashion.

    Parameters
    ----------
    df : pandas.DataFrame, required
        Input dataset. Must include a datetime column (or DatetimeIndex) and a target column.
    model : object, optional
        Pre-trained model (FLAML or H2O). If ``None``, a new model is trained per run.
    value : str, default="value"
        Target column name in ``df``.
    backend : {"flaml","h2o"}, default="flaml"
        AutoML backend used if training a model.
    feature_names : List[str], optional
        Predictor variables for training and resampling. Required if training a model.
    variables_resample : List[str], optional
        Subset of ``feature_names`` to resample. If ``None``, defaults to
        all non-time features.
    split_method : str, default="random"
        Method for train/test split if model training is performed.
    fraction : float, default=0.75
        Training fraction for splitting.
    model_config : dict, optional
        Extra backend-specific training options.
    n_samples : int, default=300
        Number of resampling iterations passed to ``normalise``.
    window_days : int, default=14
        Rolling window length in days.
    rolling_every : int, default=7
        Step between successive windows in days.
    seed : int, default=7654321
        Random seed for reproducibility.
    n_cores : int, optional
        Number of parallel workers for resampling/prediction. Defaults to all cores minus one.
    memory_save : bool, default=False
        If True, use memory-efficient per-seed prediction in ``normalise``.
    verbose : bool, default=True
        If True, log progress and ETA.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by ``date`` with columns:
          - ``observed``: the original target series
          - ``rolling_0, rolling_1, …``: one normalised series per window

    Raises
    ------
    ValueError
        If required inputs are missing (e.g. ``df`` or ``value`` not found),
        or if the window is larger than the available date span.

    Notes
    -----
    - Each rolling window is half-open: ``[start, start+window_days)``.
    - Seeds are decorrelated across windows by adding ``i*997`` to the base seed.
    """
    if df is None:
        raise ValueError("`df` must be provided.")
    if value is None:
        raise ValueError("`value` (target column name) must be provided.")

    # Ensure 'date' exists and is sorted
    if "date" not in df.columns:
        df = process_date(df)  # raises if no datetime found
    df = df[df["date"].notna()].sort_values("date").reset_index(drop=True)

    # Alias target to 'value' for downstream pipeline
    if value not in df.columns:
        raise ValueError(f"`df` does not contain the target column '{value}'.")
    df_work = df.copy()
    if value != "value":
        df_work = df_work.rename(columns={value: "value"})

    # If time vars are needed by the model, ensure they exist
    def _maybe_add_time_vars(frame: pd.DataFrame) -> pd.DataFrame:
        time_vars = {"date_unix", "day_julian", "weekday", "hour"}
        if feature_names is None:
            return frame
        need = [v for v in time_vars if v in feature_names and v not in frame.columns]
        if need:
            try:
                frame = add_date_variables(frame)
            except Exception:
                if verbose:
                    log.warning("Missing time features not generated: %s", need)
        return frame

    df_work = _maybe_add_time_vars(df_work)

    # Train a model if not provided
    if model is None:
        if not feature_names:
            raise ValueError("When `model` is None you must provide `feature_names` for training.")
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

    # Feature list for normalise
    if variables_resample is None and feature_names is not None:
        time_vars = {"date_unix", "day_julian", "weekday", "hour"}
        variables_resample = [f for f in feature_names if f not in time_vars]
    # else let `normalise` decide

    # Workers
    n_cores = max(1, n_cores if n_cores is not None else (os.cpu_count() or 2) - 1)

    # Rolling windows by calendar days
    d_floor = df_work["date"].dt.floor("D")
    min_day = d_floor.min()
    max_day = d_floor.max()
    last_start = max_day - pd.Timedelta(days=window_days - 1)
    if last_start < min_day:
        raise ValueError("Window is larger than the entire time span of `df`.")
    start_days = pd.date_range(min_day, last_start, freq=f"{rolling_every}D")

    # Output frame
    result = df_work.set_index("date")[["value"]].rename(columns={"value": "observed"})

    # Loop windows with ETA
    t0 = time.time()
    total = len(start_days)

    for i, start_day in enumerate(start_days, start=1):
        end_excl = start_day + pd.Timedelta(days=window_days)  # half-open [start, end)
        mask = (d_floor >= start_day) & (d_floor < end_excl)
        dfa = df_work.loc[mask]

        if len(dfa) < 2:
            if verbose:
                log.info(
                    "%s: window %d skipped (not enough rows).",
                    pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), i - 1
                )
            continue

        try:
            df_norm = normalise(
                df=dfa,
                model=model,
                feature_names=feature_names if feature_names is not None else list(dfa.columns),
                variables_resample=variables_resample,
                n_samples=n_samples,
                aggregate=True,
                seed=seed + (i * 997),  # decorrelate across windows
                n_cores=n_cores,
                weather_df=None,
                memory_save=memory_save,
                verbose=False,
            )
            result[f"rolling_{i-1}"] = df_norm["normalised"]
        except Exception as e:
            if verbose:
                start_str = start_day.strftime("%Y-%m-%d")
                end_str = (end_excl - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
                log.warning(
                    "%s: error in window %d [%s..%s]: %s",
                    pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    i - 1, start_str, end_str, e
                )

        if verbose and (i == 1 or i % 10 == 0 or i == total):
            elapsed = time.time() - t0
            done = i
            eta = (elapsed / done) * (total - done)
            eta_str = f"{eta/60:.1f}m" if eta >= 60 else f"{eta:.1f}s"
            s0 = start_day.strftime("%Y-%m-%d")
            s1 = (end_excl - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            log.info(
                "%s: window %d/%d [%s..%s] | ETA %s",
                pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                i - 1, total - 1, s0, s1, eta_str
            )

    return result.sort_index()
