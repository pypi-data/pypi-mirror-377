# src/normet/backends/flaml_backend.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..utils._lazy import require
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = [
    "train_flaml",
    "save_flaml",
    "load_flaml",
]


def _import_flaml_automl():
    """Dynamically import FLAML's AutoML class."""
    AutoML = require("flaml.automl:AutoML", hint="pip install flaml")
    return AutoML


def save_flaml(model: object, model_path: Union[str, Path], model_name: str) -> str:
    """
    Save a FLAML model to disk using joblib.

    Parameters
    ----------
    model : object
        Trained FLAML AutoML object.
    model_path : str | Path
        Directory where the model will be saved (created if needed).
    model_name : str
        Base filename for the saved model (without extension).

    Returns
    -------
    str
        Full path to the saved ``.joblib`` file.
    """
    joblib = require("joblib", hint="pip install joblib")
    p = Path(model_path)
    p.mkdir(parents=True, exist_ok=True)
    out = p / f"{model_name}.joblib"
    joblib.dump(model, str(out))
    log.info("Saved FLAML model to %s", out)
    return str(out)


def load_flaml(model_path: Union[str, Path], model_name: str = "automl") -> object:
    """
    Load a FLAML model saved with ``save_flaml``.

    Resolution rules
    ----------------
    - If ``model_path`` is a file ending with ``.joblib``/``.pkl``: load it.
    - If ``model_path`` is a directory:
        * prefer ``{model_name}.joblib`` if present;
        * else pick the newest ``.joblib``/``.pkl`` file in the directory.

    Parameters
    ----------
    model_path : str | Path
        File or directory path.
    model_name : str, default "automl"
        Expected base filename if ``model_path`` is a directory.

    Returns
    -------
    object
        The loaded FLAML AutoML object. Ensures ``backend == "flaml"``.

    Raises
    ------
    FileNotFoundError
        If no suitable model file is found.
    """
    joblib = require("joblib", hint="pip install joblib")
    p = Path(model_path)

    def _pick_from_dir(d: Path) -> Optional[Path]:
        cand = d / f"{model_name}.joblib"
        if cand.exists():
            return cand
        files = [f for f in d.iterdir() if f.is_file() and f.suffix.lower() in {".joblib", ".pkl"}]
        return max(files, key=lambda f: f.stat().st_mtime) if files else None

    if p.is_dir():
        target = _pick_from_dir(p)
        if target is None:
            raise FileNotFoundError(f"No FLAML model found under directory '{p}'.")
    else:
        if p.suffix.lower() not in {".joblib", ".pkl"}:
            raise FileNotFoundError(f"Unsupported model file (expect .joblib/.pkl): '{p.name}'")
        target = p

    model = joblib.load(str(target))
    if getattr(model, "backend", None) != "flaml":
        try:
            setattr(model, "backend", "flaml")
        except Exception:
            pass
    log.info("Loaded FLAML model from %s", target)
    return model


def train_flaml(
    df: pd.DataFrame,
    value: str = "value",
    variables: Optional[List[str]] = None,
    model_config: Optional[Dict[str, Any]] = None,
    seed: int = 7654321,
    verbose: bool = True,
) -> object:
    """
    Train a model with FLAML AutoML and tag it with ``backend='flaml'``.

    Parameters
    ----------
    df : pandas.DataFrame
        Training dataset containing predictors and target column.
        If a ``'set'`` column is present, rows with ``set == 'training'`` are used.
    value : str, default="value"
        Name of the target column.
    variables : List[str], optional
        Predictor variable names. Must be non-empty and unique.
    model_config : dict, optional
        Extra FLAML configuration to override defaults. Common keys:
          - ``time_budget`` (int, seconds)
          - ``metric`` (e.g., "r2")
          - ``estimator_list`` (e.g., ["lgbm"])
          - ``task`` ("regression" / "classification")
          - ``eval_method`` ("auto", "cv", "holdout")
          - ``save_model`` (bool), ``model_name`` (str), ``model_path`` (str)
    seed : int, default=7654321
        Random seed for reproducibility.
    verbose : bool, default=True
        Whether to log progress.

    Returns
    -------
    object
        A trained FLAML AutoML model, tagged with ``backend="flaml"``.

    Raises
    ------
    ValueError
        If variables are missing/empty, duplicated, or columns are not found.
    """
    if not variables:
        raise ValueError("`variables` must be a non-empty list.")
    if len(variables) != len(set(variables)):
        raise ValueError("`variables` contains duplicates.")
    missing = set(variables + [value]) - set(df.columns)
    if missing:
        raise ValueError(f"Columns not found in df: {sorted(missing)}")

    # Pick training rows if a split is present
    if "set" in df.columns:
        df_train = df.loc[df["set"] == "training", [value] + variables]
        if df_train.empty:
            df_train = df[[value] + variables]
    else:
        df_train = df[[value] + variables]

    if df_train[variables].shape[1] == 0:
        raise ValueError("No predictor columns available after preprocessing.")

    default_cfg: Dict[str, Any] = {
        "time_budget": 90,
        "metric": "r2",
        "estimator_list": ["lgbm"],
        "task": "regression",
        "eval_method": "auto",
        "save_model": False,
        "model_name": "automl",
        "model_path": "./",
        "verbose": verbose,
    }
    if model_config:
        default_cfg.update(model_config)

    passthrough = {"time_budget", "metric", "estimator_list", "task", "eval_method", "verbose"}
    automl_kwargs = {k: default_cfg[k] for k in passthrough if k in default_cfg}

    AutoML = _import_flaml_automl()
    automl = AutoML()

    if verbose:
        log.info("Training FLAML AutoML: X shape=%s, target='%s'", df_train[variables].shape, value)

    automl.fit(
        X_train=df_train[variables],
        y_train=df_train[value],
        seed=seed,
        **automl_kwargs,
    )

    if verbose:
        log.info("FLAML best_estimator=%s | best_config=%s", automl.best_estimator, automl.best_config)

    if default_cfg.get("save_model", False):
        save_flaml(automl, default_cfg.get("model_path", "./"), default_cfg.get("model_name", "automl"))

    setattr(automl, "backend", "flaml")
    return automl
