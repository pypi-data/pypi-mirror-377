# src/normet/backends/h2o_backend.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..utils._lazy import require
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = [
    "init_h2o",
    "train_h2o",
    "save_h2o",
    "load_h2o",
    "stop_h2o",
]


def _import_h2o() -> Any:
    """Lazy import h2o (optional dependency)."""
    return require("h2o", hint="pip install h2o==3.*")


def init_h2o(
    n_cores: Optional[int] = None,
    max_mem_size: str = "8G",
    silent: bool = True,
) -> Any:
    """
    Start (or reuse) an H2O cluster with given resources.

    Parameters
    ----------
    n_cores : int | None
        Number of cores for H2O backend. None or <= 0 uses all available cores.
    max_mem_size : str
        JVM heap size, e.g. "8G".
    silent : bool, default=True
        If True, reduce H2O init chatter by setting log_level="WARN".

    Returns
    -------
    Any
        The imported `h2o` module (already initialized).
    """
    h2o = _import_h2o()
    cl = h2o.init(
        nthreads=(n_cores if (n_cores and n_cores > 0) else -1),
        max_mem_size=max_mem_size,
        log_level="WARN" if silent else "INFO",
        bind_to_localhost=True,
    )
    try:
        log.info(
            "H2O cluster up | version=%s | nthreads=%s | mem=%s",
            getattr(cl, "cluster_version", lambda: "?")(),
            getattr(cl, "nthreads", "?"),
            max_mem_size,
        )
    except Exception:
        pass
    return h2o


def _to_h2o_frame(df: pd.DataFrame) -> Any:
    """Convert a pandas DataFrame to an H2OFrame."""
    h2o = _import_h2o()
    return h2o.H2OFrame(df)


def _coerce_numeric(h2o_frame: Any, numeric_cols: List[str]) -> Any:
    """
    Ensure numeric columns are numeric in an H2OFrame.
    """
    for c in numeric_cols:
        try:
            h2o_frame[c] = h2o_frame[c].asnumeric()
        except Exception:
            pass
    return h2o_frame


def save_h2o(model: Any, model_path: Union[str, Path], model_name: str) -> str:
    """
    Save an H2O model using ``h2o.save_model``.

    Parameters
    ----------
    model : Any
        Trained H2O model object.
    model_path : str | pathlib.Path
        Directory where the model will be saved (created if needed).
    model_name : str
        Logical model name (used for logging only by this helper).

    Returns
    -------
    str
        The path (string) returned by ``h2o.save_model``.
    """
    h2o = _import_h2o()
    p = Path(model_path)
    p.mkdir(parents=True, exist_ok=True)
    out = h2o.save_model(model=model, path=str(p), force=True)
    log.info("Saved H2O model (%s) to %s", model_name, out)
    return out


def load_h2o(
    model_path: Union[str, Path],
    *,
    init_if_needed: bool = True,
    n_cores: Optional[int] = None,
    max_mem_size: str = "8G",
    silent: bool = True,
) -> object:
    """
    Load an H2O model previously saved with ``h2o.save_model``.

    Parameters
    ----------
    model_path : str | pathlib.Path
        Path to a saved model file, or a directory containing one.
    init_if_needed : bool, default True
        If True, ensure an H2O cluster exists (init if missing).
    n_cores : int | None, optional
        Cores to allocate if initializing a cluster.
    max_mem_size : str, default "8G"
        JVM heap size if initializing a cluster.
    silent : bool, default True
        If True, use quieter H2O logging.

    Returns
    -------
    object
        The loaded H2O model. Attribute ``backend`` is set to "h2o".
    """
    h2o = _import_h2o()
    p = Path(model_path)

    # Ensure a cluster exists
    if init_if_needed:
        try:
            cl = None
            try:
                cl = h2o.cluster()
            except Exception:
                pass
            if cl is None:
                from .h2o_backend import init_h2o as _init
                _init(n_cores=n_cores, max_mem_size=max_mem_size, silent=silent)
        except Exception as e:
            log.warning("Could not initialize/attach H2O cluster automatically: %s", e)
    else:
        try:
            if h2o.cluster() is None:
                raise RuntimeError("No H2O cluster attached. Call init_h2o() or set init_if_needed=True.")
        except Exception as e:
            raise RuntimeError("No H2O cluster available for loading models.") from e

    def _pick_file_from_dir(d: Path) -> Optional[Path]:
        files = [f for f in d.iterdir() if f.is_file()]
        model_like = [f for f in files if "_model_" in f.name]
        if model_like:
            return max(model_like, key=lambda f: f.stat().st_mtime)
        return max(files, key=lambda f: f.stat().st_mtime) if files else None

    if p.is_dir():
        target = _pick_file_from_dir(p)
        if target is None:
            raise FileNotFoundError(f"No H2O model files found under directory '{p}'.")
    else:
        if not p.exists():
            raise FileNotFoundError(f"Model file not found: '{p}'.")
        target = p

    model = h2o.load_model(path=str(target))
    if getattr(model, "backend", None) != "h2o":
        try:
            setattr(model, "backend", "h2o")
        except Exception:
            pass
    log.info("Loaded H2O model from %s", target)
    return model


def train_h2o(
    df: pd.DataFrame,
    value: str = "value",
    variables: Optional[List[str]] = None,
    model_config: Optional[Dict[str, Any]] = None,
    seed: int = 7654321,
    n_cores: Optional[int] = None,
    verbose: bool = True,
) -> object:
    """
    Train an H2O AutoML (or restricted algos) model and return the leader.

    Parameters
    ----------
    df : pandas.DataFrame
        Prepared dataset containing predictors and target column.
        If a ``'set'`` column is present, rows with ``set == 'training'`` are used.
    value : str, default "value"
        Name of the target column.
    variables : List[str], optional
        Predictor variable names. Must be non-empty and unique.
    model_config : dict, optional
        Extra H2O AutoML configuration to override defaults. Common keys:
          - ``max_models`` (int)
          - ``nfolds`` (int)
          - ``include_algos`` (list of algo names)
          - ``sort_metric`` (str)
          - ``max_mem_size`` (str, used for cluster init)
          - ``save_model`` (bool), ``model_name`` (str), ``model_path`` (str)
    seed : int, default 7654321
        Random seed for reproducibility.
    n_cores : int | None, optional
        CPU cores for H2O cluster init; None = all cores.
    verbose : bool, default True
        Whether to emit progress logs.

    Returns
    -------
    object
        The H2O AutoML leader model with ``backend="h2o"``.

    Raises
    ------
    ValueError
        If variables are missing/empty/duplicated, or columns are not found.
    RuntimeError
        If H2O AutoML training fails.
    """
    if not variables:
        raise ValueError("`variables` must be a non-empty list.")
    if len(variables) != len(set(variables)):
        raise ValueError("`variables` contains duplicates.")
    missing = set(variables + [value]) - set(df.columns)
    if missing:
        raise ValueError(f"Columns not found in df: {sorted(missing)}")

    # Partition
    if "set" in df.columns:
        df_train = df.loc[df["set"] == "training", [value] + variables]
        if df_train.empty:
            df_train = df[[value] + variables]
    else:
        df_train = df[[value] + variables]

    # Config (defaults)
    cfg: Dict[str, Any] = {
        "max_models": 10,
        "nfolds": 5,
        "max_mem_size": "16G",
        "include_algos": ["GBM"],
        "sort_metric": "deviance",
        "save_model": False,
        "model_name": "automl",
        "model_path": "./",
        "seed": seed,
        "verbose": verbose,
    }
    if model_config:
        cfg.update(model_config)

    # Init cluster
    h2o = init_h2o(
        n_cores=n_cores,
        max_mem_size=cfg.get("max_mem_size", "16G"),
        silent=not verbose,
    )

    # Frame
    fr = _to_h2o_frame(df_train)
    response = value
    predictors = [c for c in fr.columns if c != response]
    if not predictors:
        raise ValueError("No predictor columns available after preprocessing.")
    fr = _coerce_numeric(fr, predictors)

    # Train
    try:
        H2OAutoML = h2o.automl.H2OAutoML
        if verbose:
            log.info(
                "Training H2O AutoML: X=%d cols, target='%s' (max_models=%s, nfolds=%s, include_algos=%s)",
                len(predictors), response, cfg["max_models"], cfg["nfolds"], cfg.get("include_algos"),
            )
        aml = H2OAutoML(
            max_models=cfg["max_models"],
            nfolds=cfg["nfolds"],
            seed=cfg["seed"],
            sort_metric=cfg.get("sort_metric", "deviance"),
            include_algos=cfg.get("include_algos"),
            verbosity="info" if verbose else None,
        )
        aml.train(x=predictors, y=response, training_frame=fr)
        leader = aml.leader
        if verbose:
            lid = aml.leaderboard[0, "model_id"]
            log.info("H2O AutoML leader: %s", lid)
    except Exception as e:
        log.error("H2O AutoML training failed: %s", e)
        raise RuntimeError("H2O AutoML training failed.") from e

    if cfg.get("save_model", False):
        save_h2o(leader, cfg.get("model_path", "./"), cfg.get("model_name", "automl"))

    setattr(leader, "backend", "h2o")
    return leader


def stop_h2o(quiet: bool = True) -> None:
    """
    Shut down the attached H2O cluster if available.

    Parameters
    ----------
    quiet : bool, default True
        If True, do not prompt on shutdown.
    """
    try:
        h2o = _import_h2o()
        cl = h2o.cluster()
        if cl is not None:
            cl.shutdown(prompt=not quiet)
            log.info("H2O cluster shutdown requested.")
    except Exception as e:
        log.debug("H2O shutdown skipped: %s", e)
