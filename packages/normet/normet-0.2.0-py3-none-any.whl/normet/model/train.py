# src/normet/model/train.py
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from ..utils.prepare import prepare_data
from ..backends import train_flaml, train_h2o
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = ["build_model", "train_model"]


def build_model(
    df: pd.DataFrame,
    value: str,
    backend: Optional[str] = None,
    feature_names: Optional[List[str]] = None,
    split_method: str = "random",
    fraction: float = 0.75,
    model_config: Optional[Dict[str, Any]] = None,
    seed: int = 7654321,
    n_cores: Optional[int] = None,
    verbose: bool = True,
    drop_time_features: bool = False,
) -> Tuple[pd.DataFrame, object]:
    """
    Prepare the data and train a model with the selected AutoML backend.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw input data.
    value : str
        Target column in `df`.
    backend : {"flaml","h2o"}, optional
        AutoML backend. Default "flaml".
    feature_names : List[str], optional
        Predictors to use. Must be non-empty when training a model.
    split_method : str, default="random"
        Data split strategy for training.
    fraction : float, default=0.75
        Train fraction for the split.
    model_config : dict, optional
        Backend-specific configuration passed through to the trainer.
    seed : int, default=7654321
        Random seed.
    n_cores : int | None, optional
        CPU cores (used by H2O).
    verbose : bool, default=True
        Verbose logging.
    drop_time_features : bool, default=False
        If True, drop helper time features like {"date_unix","day_julian","weekday","hour"}.
        By default we keep them.

    Returns
    -------
    (pandas.DataFrame, object)
        Tuple of (prepared_df, trained_model).
    """
    backend = (backend or "flaml").lower()

    if not feature_names:
        raise ValueError("`feature_names` must be provided and non-empty.")

    # Optionally drop helper time features (default: keep them)
    if drop_time_features:
        drop_cols = {"date_unix", "day_julian", "weekday", "hour"}
        variables = [c for c in feature_names if c not in drop_cols]
    else:
        variables = list(feature_names)

    # Prepare data (ensures 'date', renames target to 'value', splits sets, etc.)
    df_prep = prepare_data(
        df=df,
        value=value,
        feature_names=variables,
        split_method=split_method,
        fraction=fraction,
        seed=seed,
    )

    # Align variables to what survived prepare_data (be explicit if none remain)
    variables = [c for c in variables if c in df_prep.columns]
    if not variables:
        raise ValueError(
            "None of the requested features remain after prepare_data(). "
            "Check `feature_names` and your input columns."
        )

    # Resolve target column consistently
    if "value" in df_prep.columns:
        target_col = "value"
    elif value in df_prep.columns:
        target_col = value
        df_prep = df_prep.copy()
        df_prep["value"] = df_prep[value]
    else:
        raise ValueError(
            "Target column not found after prepare_data(); "
            f"tried 'value' and '{value}'. Columns: {list(df_prep.columns)}"
        )

    # Train
    model = train_model(
        df=df_prep,
        value=target_col,
        backend=backend,
        variables=variables,
        model_config=model_config,
        seed=seed,
        n_cores=n_cores,
        verbose=verbose,
    )

    log.info("Model trained with backend=%s", backend)
    return df_prep, model


def train_model(
    df: pd.DataFrame,
    value: str = "value",
    backend: str = "flaml",
    variables: Optional[List[str]] = None,
    model_config: Optional[Dict[str, Any]] = None,
    seed: int = 7654321,
    n_cores: Optional[int] = None,
    verbose: bool = True,
) -> object:
    """
    Train an AutoML model with FLAML or H2O.

    Parameters
    ----------
    df : pandas.DataFrame
        Prepared dataset (should contain 'value' and features; may include 'set').
    value : str, default="value"
        Target column to fit.
    backend : {"flaml","h2o"}, default="flaml"
        AutoML backend.
    variables : List[str], optional
        Predictor names (non-empty, unique).
    model_config : dict, optional
        Backend-specific configuration.
    seed : int, default=7654321
        Random seed.
    n_cores : int | None, optional
        CPU cores (H2O only; default all-1).
    verbose : bool, default=True
        Verbose logging.

    Returns
    -------
    object
        Trained model with attribute ``backend`` in {'flaml','h2o'}.

    Raises
    ------
    ValueError
        If variables are missing/empty/duplicated, or columns are not found.
    """
    backend = (backend or "flaml").lower()

    if not variables:
        raise ValueError("`variables` must be a non-empty list.")
    if len(variables) != len(set(variables)):
        raise ValueError("`variables` contains duplicates.")
    missing = set(variables + [value]) - set(df.columns)
    if missing:
        raise ValueError(f"Columns not found in df: {sorted(missing)}")

    if n_cores is None:
        n_cores = max(1, (os.cpu_count() or 2) - 1)

    if backend == "flaml":
        model = train_flaml(
            df,
            value=value,
            variables=variables,
            model_config=model_config,
            seed=seed,
            verbose=verbose,
        )
        return model

    if backend == "h2o":
        model = train_h2o(
            df,
            value=value,
            variables=variables,
            model_config=model_config,
            seed=seed,
            n_cores=n_cores,
            verbose=verbose,
        )
        return model

    raise ValueError("`backend` must be 'flaml' or 'h2o'.")
