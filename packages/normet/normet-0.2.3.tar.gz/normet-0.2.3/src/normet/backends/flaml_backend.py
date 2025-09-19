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


def save_flaml(
    model,
    folder_path: Union[str, Path] = ".",
    filename: str = "automl.joblib",
) -> str:
    """
    Save a FLAML AutoML model to the specified directory with the given filename.

    Parameters
    ----------
    model : AutoML
        The FLAML AutoML model to save.
    folder_path : str | Path, default="."
        Directory path to save the model.
    filename : str, default="automl.joblib"
        Desired filename. If no extension is given, ``.joblib`` will be added.

    Returns
    -------
    str
        The path of the saved model.
    """
    joblib = require("joblib", hint="pip install joblib")  # <-- added
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)

    # Ensure extension
    if not Path(filename).suffix:
        filename = f"{filename}.joblib"

    model_path = folder / filename

    joblib.dump(model, str(model_path))
    log.info("Saved FLAML model to %s", model_path)
    return str(model_path)


def load_flaml(
    folder_path: Union[str, Path] = ".",
    filename: Optional[str] = None,
) -> object:
    """
    Load a FLAML model saved with ``save_flaml``.

    Resolution rules
    ----------------
    - If ``filename`` is provided, load exactly ``folder_path/filename``.
    - Otherwise, scan ``folder_path`` and pick the most recently modified
      ``.joblib`` or ``.pkl`` file.

    Parameters
    ----------
    folder_path : str | Path, default "."
        Directory containing the saved model, or a file path if you pass the
        file directly via ``filename=None`` and ``folder_path`` is a file.
    filename : str | None, optional
        Specific filename to load (e.g., "automl.joblib"). If None, auto-pick.

    Returns
    -------
    object
        The loaded FLAML AutoML object. Ensures ``backend == "flaml"``.

    Raises
    ------
    FileNotFoundError
        If no suitable model file is found.
    ImportError
        If ``joblib`` is not installed.
    """
    joblib = require("joblib", hint="pip install joblib")
    p = Path(folder_path)

    # If user passed a direct file path via folder_path and no filename
    if filename is None and p.is_file():
        target = p
        if target.suffix.lower() not in {".joblib", ".pkl"}:
            raise FileNotFoundError(f"Unsupported model file (expect .joblib/.pkl): '{target.name}'")
    else:
        folder = p if p.is_dir() else p.parent
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: '{folder}'")

        if filename:
            target = folder / filename
            if not target.exists():
                raise FileNotFoundError(f"Specified model file not found: {target}")
        else:
            candidates = [
                f for f in folder.iterdir()
                if f.is_file() and f.suffix.lower() in {".joblib", ".pkl"}
            ]
            if not candidates:
                raise FileNotFoundError(f"No FLAML model files (.joblib/.pkl) found under '{folder}'.")
            target = max(candidates, key=lambda f: f.stat().st_mtime)

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
        FLAML configuration overrides. Recognized keys and **defaults**:
          - ``time_budget`` : int (default 90)
          - ``metric`` : str (default "r2")
          - ``estimator_list`` : list[str] (default ["lgbm"])
          - ``task`` : {"regression","classification"} (default "regression")
          - ``eval_method`` : {"auto","cv","holdout"} (default "auto")
          - ``save_model`` : bool (default False)
          - ``folder_path`` : str (default ".")
          - ``filename`` : str (default "automl.joblib")
          - ``verbose`` : bool (defaults to this function's ``verbose``)

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

    # Defaults
    default_cfg: Dict[str, Any] = {
        "time_budget": 90,
        "metric": "r2",
        "estimator_list": ["lgbm"],
        "task": "regression",
        "eval_method": "auto",
        "save_model": False,
        "folder_path": ".",
        "filename": "automl.joblib",
        "verbose": verbose,
    }
    if model_config:
        default_cfg.update(model_config)

    # Build kwargs for AutoML.fit
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

    # Optional persistence
    if default_cfg.get("save_model", False):
        save_flaml(
            automl,
            folder_path=default_cfg.get("folder_path", "."),
            filename=default_cfg.get("filename", "automl.joblib"),
        )

    setattr(automl, "backend", "flaml")
    return automl
