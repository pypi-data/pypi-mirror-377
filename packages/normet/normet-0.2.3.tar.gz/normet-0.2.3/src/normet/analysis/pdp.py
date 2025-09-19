# src/normet/analysis/pdp.py
import os
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from typing import List, Optional, Tuple

from ..utils.features import extract_features
from ..model.predict import ml_predict
from ..utils.logging import get_logger

log = get_logger(__name__)


def pdp(
    df: pd.DataFrame,
    model: object,
    var_list: Optional[List[str]] = None,
    training_only: bool = True,
    n_cores: Optional[int] = None,
    grid_points: int = 50,
    quantile_range: Tuple[float, float] = (0.01, 0.99),
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Compute Partial Dependence values for one or more features.

    Works with models trained via FLAML (sklearn-like predict) or H2O.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset containing features (and optionally a 'set' column == 'training').
    model : object
        Trained model with `backend` in {'flaml','h2o'} and a predict interface
        supported by `ml_predict`.
    var_list : List[str] | None
        Variables to compute PDP for. If None, use model feature names.
    training_only : bool, default True
        If True and df has a 'set' column, use only rows with `set == "training"`.
    n_cores : int | None
        Parallel workers for the FLAML path. H2O runs sequentially due to
        pickling constraints. Default: all cores - 1.
    grid_points : int, default 50
        Number of evaluation points on the value grid.
    quantile_range : (float, float), default (0.01, 0.99)
        Range of the feature values to cover.
    verbose : bool, default False
        If True, emit info logs.

    Returns
    -------
    pandas.DataFrame
        Columns: ['variable', 'value', 'pdp_mean', 'pdp_std'].
    """
    # --- model type guard ---
    model_type = getattr(model, "backend", None)
    if model_type not in {"flaml", "h2o"}:
        raise TypeError("Unsupported model type. `backend` must be 'flaml' or 'h2o'.")

    # --- resolve features ---
    try:
        feature_names = [str(c) for c in extract_features(model)]
    except Exception:
        if var_list:
            feature_names = [str(c) for c in var_list if str(c) in df.columns]
        else:
            raise ValueError("Cannot infer model features; please provide `var_list`.")

    feature_names = [c for c in feature_names if c in df.columns]
    if not feature_names:
        raise ValueError("No valid model features present in `df`.")

    # PDP target variables
    if var_list is None:
        vars_for_pdp = feature_names
    else:
        vars_for_pdp = [v for v in var_list if v in feature_names]
        missing = [v for v in var_list if v not in feature_names]
        if verbose and missing:
            log.info("Skipping vars not present in features: %s", missing)

    # --- choose data subset ---
    if "set" in df.columns and training_only:
        X_df = df.loc[df["set"] == "training", feature_names].copy()
        if X_df.empty:
            X_df = df[feature_names].copy()
    else:
        X_df = df[feature_names].copy()

    # --- H2O path (sequential) ---
    if model_type == "h2o":
        try:
            import h2o  # optional dependency
        except Exception as e:
            raise ImportError("H2O is required for PDP with H2O models. Install with: pip install h2o") from e

        if verbose and (n_cores is not None and n_cores != 1):
            log.info("H2O PDP runs sequentially (n_cores ignored).")

        df_h2o = h2o.H2OFrame(X_df)

        pieces: List[pd.DataFrame] = []
        for var in vars_for_pdp:
            try:
                fr = model.partial_plot(frame=df_h2o, cols=[var], plot=False)[0].as_data_frame()
                value_col = var
                mean_col = "mean_response" if "mean_response" in fr.columns else "pdp_mean"
                std_col = "stddev_response" if "stddev_response" in fr.columns else None

                out = pd.DataFrame(
                    {
                        "variable": var,
                        "value": fr[value_col],
                        "pdp_mean": fr[mean_col],
                        "pdp_std": fr[std_col] if (std_col and std_col in fr.columns) else np.nan,
                    }
                )
                pieces.append(out)
            except Exception as e:
                if verbose:
                    log.warning("PDP failed for '%s' (H2O): %s", var, e)
                pieces.append(pd.DataFrame(columns=["variable", "value", "pdp_mean", "pdp_std"]))

        return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(
            columns=["variable", "value", "pdp_mean", "pdp_std"]
        )

    # --- FLAML / sklearn-like path ---
    def _grid(series: pd.Series) -> Optional[np.ndarray]:
        s = pd.to_numeric(series, errors="coerce")
        s = s[np.isfinite(s)]
        if s.empty:
            return None
        lo, hi = np.quantile(s, quantile_range)
        if not np.isfinite(lo) or not np.isfinite(hi) or lo == hi:
            v = lo if np.isfinite(lo) else hi
            return None if not np.isfinite(v) else np.array([float(v)])
        return np.linspace(float(lo), float(hi), int(max(2, grid_points)))

    X_df = X_df.copy()
    n_cores_eff = max(1, n_cores if n_cores is not None else (os.cpu_count() or 2) - 1)

    def _one_flaml(var: str) -> pd.DataFrame:
        grid = _grid(X_df[var])
        if grid is None or len(grid) == 0:
            if verbose:
                log.info("Variable '%s' has insufficient numeric spread; skipping.", var)
            return pd.DataFrame(columns=["variable", "value", "pdp_mean", "pdp_std"])

        X_work = X_df.copy()
        means: List[float] = []
        stds: List[float] = []
        for g in grid:
            X_work[var] = g
            yhat = ml_predict(model, X_work)
            yhat = np.asarray(yhat, dtype=float)
            means.append(float(np.nanmean(yhat)) if yhat.size else np.nan)
            stds.append(float(np.nanstd(yhat)) if yhat.size else np.nan)

        return pd.DataFrame({"variable": var, "value": grid, "pdp_mean": means, "pdp_std": stds})

    pieces = Parallel(n_jobs=n_cores_eff)(delayed(_one_flaml)(v) for v in vars_for_pdp)
    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(
        columns=["variable", "value", "pdp_mean", "pdp_std"]
    )
