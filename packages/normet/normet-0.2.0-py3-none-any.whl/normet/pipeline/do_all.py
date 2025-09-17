# src/normet/pipeline/do_all.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import time

from ..utils.prepare import prepare_data
from ..model.train import build_model
from ..analysis.normalise import normalise
from ..utils.metrics import modStats
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = ["do_all", "do_all_unc"]


def do_all(
    df: pd.DataFrame,
    value: str,
    backend: str = "flaml",
    feature_names: Optional[List[str]] = None,
    variables_resample: Optional[List[str]] = None,
    split_method: str = "random",
    fraction: float = 0.75,
    model_config: Optional[Dict[str, Any]] = None,
    n_samples: int = 300,
    seed: int = 7_654_321,
    n_cores: Optional[int] = None,
    memory_save: bool = False,
    verbose: bool = True,
    *,
    aggregate: bool = True,
) -> Tuple[pd.DataFrame, object, pd.DataFrame]:
    """
    High-level convenience pipeline: prepare → train → normalise.

    Steps:
      1) Prepare dataset (date parsing, feature checks, splitting)
      2) Train an AutoML model using the requested backend
      3) Run :func:`normalise` with the trained model and return results

    Parameters
    ----------
    df : pandas.DataFrame
        Raw input data containing a datetime column (or DatetimeIndex),
        the target variable, and predictors.
    value : str
        Target column name in ``df`` (e.g., pollutant concentration).
    backend : {"flaml","h2o"}, default="flaml"
        AutoML backend used for model training.
    feature_names : List[str], optional
        Predictor columns used for training and normalisation.
    variables_resample : List[str], optional
        Subset of predictors to resample inside :func:`normalise`.
        Defaults to non-time features from ``feature_names``.
    split_method : {"random","ts","season","month"}, default="random"
        Train/test split method.
    fraction : float, default=0.75
        Training fraction for data splitting.
    model_config : dict, optional
        Backend-specific training options.
    n_samples : int, default=300
        Number of resamples in :func:`normalise`.
    seed : int, default=7654321
        Random seed for reproducibility.
    n_cores : int, optional
        Parallel workers (passed to :func:`normalise`).
    memory_save : bool, default=False
        If True, use a memory-efficient (but slower) path in :func:`normalise`.
    verbose : bool, default=True
        If True, log progress.
    aggregate : bool, default=True
        Whether :func:`normalise` should aggregate the resamples to a single
        normalised series (True) or return the full resample matrix/details (False).

    Returns
    -------
    out : pandas.DataFrame
        Indexed by ``date`` with at least:
          - observed
          - normalised          (if aggregate=True)
          - or resample outputs (if aggregate=False; see :func:`normalise` docs).
    model : object
        Trained AutoML model, tagged with ``backend`` ("flaml" or "h2o").
    df_prep : pandas.DataFrame
        The prepared dataset after preprocessing, splitting, and imputation.
        Can be reused for evaluation via :func:`modStats`.
    """
    log.info("Starting do_all | backend=%s | value=%s | n_samples=%d", backend, value, n_samples)

    # 1) Prepare data
    df_prep = prepare_data(
        df, value=value, feature_names=feature_names,
        split_method=split_method, fraction=fraction, seed=seed
    )
    log.info(
        "Data prepared: %d rows (%d training, %d testing)",
        len(df_prep),
        int((df_prep.get("set") == "training").sum()) if "set" in df_prep else len(df_prep),
        int((df_prep.get("set") == "testing").sum()) if "set" in df_prep else 0,
    )

    # 2) Train model
    df_prep, model = build_model(
        df=df_prep,
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
    log.info("Model trained with backend=%s", backend)

    # 3) Normalise
    out = normalise(
        df=df_prep,
        model=model,
        feature_names=feature_names or [c for c in df_prep.columns if c not in {"value"}],
        variables_resample=variables_resample,
        n_samples=n_samples,
        aggregate=aggregate,
        seed=seed,
        n_cores=n_cores,
        memory_save=memory_save,
        verbose=verbose,
    )

    # 4) Evaluate model
    mod_stats = modStats(df=df_prep, model=model, subset=None, statistic=None)

    log.info("do_all finished: %d timestamps", len(out))
    return out, model, df_prep


def do_all_unc(
    df: pd.DataFrame,
    value: str,
    backend: str = "flaml",
    feature_names: Optional[List[str]] = None,
    variables_resample: Optional[List[str]] = None,
    split_method: str = "random",
    fraction: float = 0.75,
    model_config: Optional[Dict[str, Any]] = None,
    n_samples: int = 300,
    n_models: int = 10,
    confidence_level: float = 0.95,
    seed: int = 7_654_321,
    n_cores: Optional[int] = None,
    weather_df: Optional[pd.DataFrame] = None,
    memory_save: bool = False,
    verbose: bool = True,
    weighted_method: str = "r2",   # {"r2","rmse"}
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Train/evaluate multiple models (different seeds), aggregate their
    deweathered predictions, and build uncertainty bands.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset containing a datetime column, target, and predictors.
    value : str
        Target column name in ``df``.
    backend : {"flaml","h2o"}, default "flaml"
        AutoML backend to use for training.
    feature_names : List[str], optional
        Predictor columns.
    variables_resample : List[str], optional
        Subset of predictors to resample inside normalisation.
    split_method : {"random","ts","season","month"}, default "random"
        Train/test split method.
    fraction : float, default 0.75
        Training fraction for data splitting.
    model_config : dict, optional
        Backend-specific training options.
    n_samples : int, default 300
        Number of resamples in the normalisation step.
    n_models : int, default 10
        Number of independent models (different seeds) to train.
    confidence_level : float, default 0.95
        Confidence level for uncertainty bands.
    seed : int, default 7654321
        Random seed for reproducibility.
    n_cores : int, optional
        Number of parallel workers.
    memory_save : bool, default False
        If True, use memory-efficient path in normalisation.
    verbose : bool, default True
        If True, log progress.
    weighted_method : {"r2","rmse"}, default "r2"
        Method to compute weights for the final ``weighted`` blend:
          - "r2":  weight ∝ max(R2, 0)
          - "rmse": weight ∝ 1 / (RMSE + eps)

    Returns
    -------
    out : pandas.DataFrame
        Indexed by ``date`` with columns:
          - observed
          - normalised_<seed> (each model’s output)
          - mean, std, median
          - lower_bound, upper_bound
          - weighted (performance-weighted blend)
    mod_stats : pandas.DataFrame
        Concatenated evaluation metrics across seeds, with an added ``weight`` column.
    """
    weighted_method = (weighted_method or "r2").lower()
    if weighted_method not in {"r2", "rmse"}:
        raise ValueError("`weighted_method` must be 'r2' or 'rmse'.")

    rng = np.random.default_rng(seed)
    seeds = rng.choice(1_000_001, size=n_models, replace=False).tolist()

    series_list: List[pd.DataFrame] = []
    stats_list: List[pd.DataFrame] = []
    observed_ref: Optional[pd.Series] = None

    t0 = time.time()
    for i, s in enumerate(seeds, start=1):
        if verbose:
            elapsed = time.time() - t0
            eta = (elapsed / max(1, i - 1)) * (n_models - (i - 1)) if i > 1 else None
            eta_str = "" if eta is None else (f"ETA {eta/60:.1f}m" if eta >= 60 else f"ETA {eta:.1f}s")
            log.info("do_all_unc: running model %d/%d (seed=%d) %s", i, n_models, s, eta_str)

        # `do_all` now returns: (out_i, model_i, df_prep_i)
        out_i, model_i, df_prep_i = do_all(
            df=df,
            value=value,
            backend=backend,
            feature_names=feature_names,
            variables_resample=variables_resample,
            split_method=split_method,
            fraction=fraction,
            model_config=model_config,
            n_samples=n_samples,
            seed=int(s),
            n_cores=n_cores,
            memory_save=memory_save,
            verbose=False,
            aggregate=True,
        )

        if observed_ref is None:
            observed_ref = out_i["observed"].copy()

        # Collect per-model normalised series
        col = f"normalised_{s}"
        series_list.append(out_i[["normalised"]].rename(columns={"normalised": col}))

        # Compute metrics for weighting using the prepared df + model
        try:
            stats_i = modStats(df=df_prep_i, model=model_i, subset=None, statistic=None)
            if isinstance(stats_i, pd.DataFrame) and not stats_i.empty:
                stats_i = stats_i.copy()
                stats_i["seed"] = int(s)
                stats_list.append(stats_i)
        except Exception as e:
            log.warning("Failed to compute metrics for seed %d: %s", s, e)

    if observed_ref is None:
        raise RuntimeError("do_all_unc produced no outputs — verify inputs and seeds.")

    # Merge observed + per-seed normalised outputs
    out = observed_ref.to_frame(name="observed")
    for s in series_list:
        out = out.join(s, how="outer")

    pred_cols = [c for c in out.columns if c.startswith("normalised_")]
    P = out[pred_cols]

    # Aggregate stats across models
    out["mean"] = P.mean(axis=1)
    out["std"] = P.std(axis=1)
    out["median"] = P.median(axis=1)

    alpha = (1.0 - confidence_level) / 2.0
    out["lower_bound"] = P.quantile(alpha, axis=1)
    out["upper_bound"] = P.quantile(1.0 - alpha, axis=1)

    # ----------------------------
    # Compute performance-based weights
    # ----------------------------
    def _pick_metric(df_in: pd.DataFrame, names: List[str]) -> Optional[float]:
        """Pick first available metric value from a DataFrame."""
        for n in names:
            if n in df_in.columns:
                try:
                    return float(df_in[n].iloc[0])
                except Exception:
                    continue
        return None

    # Extract metrics for each seed
    perf_rows = []
    for si in stats_list:
        sd = int(si["seed"].iloc[0])
        r2_val = _pick_metric(si, ["r2", "R2", "r_squared", "R2_score"])
        rmse_val = _pick_metric(si, ["rmse", "RMSE", "root_mean_squared_error"])
        perf_rows.append({"seed": sd, "r2": r2_val, "rmse": rmse_val})
    perf_df = pd.DataFrame(perf_rows).set_index("seed") if perf_rows else pd.DataFrame(columns=["r2", "rmse"])

    # Parse seeds from column names
    def _parse_seed(col: str) -> Optional[int]:
        try:
            return int(col.split("_", 1)[1])
        except Exception:
            return None

    seeds_in_P = [s for s in map(_parse_seed, pred_cols)]

    # Build raw scores
    scores = np.zeros(len(seeds_in_P), dtype=float)
    if not perf_df.empty:
        if weighted_method == "r2":
            for i, s in enumerate(seeds_in_P):
                if s is None or s not in perf_df.index:
                    continue
                r2 = perf_df.loc[s, "r2"]
                if pd.notna(r2):
                    scores[i] = max(float(r2), 0.0)  # negative R² → 0
        else:  # "rmse"
            eps = 1e-9
            for i, s in enumerate(seeds_in_P):
                if s is None or s not in perf_df.index:
                    continue
                rmse = perf_df.loc[s, "rmse"]
                if pd.notna(rmse):
                    scores[i] = 1.0 / (float(rmse) + eps)

    # Normalise scores → weights; fallback to equal weights if all invalid
    if np.all(~np.isfinite(scores)) or np.all(scores <= 0):
        w = np.full(len(pred_cols), 1.0 / len(pred_cols)) if pred_cols else np.array([])
    else:
        scores = np.where(np.isfinite(scores) & (scores > 0), scores, 0.0)
        ssum = scores.sum()
        w = scores / ssum if ssum > 0 else np.full(len(pred_cols), 1.0 / len(pred_cols))

    # Apply weights to predictions
    if pred_cols:
        out["weighted"] = (P.values * w[np.newaxis, :]).sum(axis=1)
    else:
        out["weighted"] = np.nan

    # Save weights back to mod_stats for transparency
    w_by_seed = {s: float(w[i]) for i, s in enumerate(seeds_in_P) if i < len(w)}
    mod_stats = pd.concat(stats_list, ignore_index=True) if stats_list else pd.DataFrame()
    if not mod_stats.empty and "seed" in mod_stats.columns:
        mod_stats["weight"] = mod_stats["seed"].map(w_by_seed).astype(float)

    return out, mod_stats
