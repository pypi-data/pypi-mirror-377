# src/normet/backends/h2o_backend.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import shutil
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
    """
    h2o = _import_h2o()
    cl = h2o.init(
        nthreads=(n_cores if (n_cores and n_cores > 0) else -1),
        max_mem_size=max_mem_size,
        log_level="WARN" if silent else "INFO",
        bind_to_localhost=True,
    )
    try:
        ver = getattr(cl, "cluster_version", None)
        ver = ver() if callable(ver) else ver
        nthreads = getattr(cl, "nthreads", "?")
        log.info("H2O cluster up | version=%s | nthreads=%s | mem=%s", ver, nthreads, max_mem_size)
    except Exception:
        pass
    return h2o


def _to_h2o_frame(df: pd.DataFrame) -> Any:
    """Convert a pandas DataFrame to an H2OFrame."""
    h2o = _import_h2o()
    return h2o.H2OFrame(df)


def _coerce_numeric(h2o_frame: Any, numeric_cols: List[str]) -> Any:
    """Ensure numeric columns are numeric in an H2OFrame."""
    for c in numeric_cols:
        try:
            h2o_frame[c] = h2o_frame[c].asnumeric()
        except Exception:
            pass
    return h2o_frame


def save_h2o(
    model: Any,
    folder_path: Union[str, Path] = ".",
    filename: str = "automl",
) -> str:
    """
    Save an H2O model, then rename the artifact to the given filename
    (file extension preserved if the original is a file and no extension provided).
    """
    h2o = _import_h2o()  # <- missing before
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)

    saved_path = Path(h2o.save_model(model=model, path=str(folder), force=True))

    target = folder / filename
    if saved_path.is_file() and not Path(filename).suffix:
        target = target.with_suffix(saved_path.suffix)

    if target.exists():
        if target.is_file() or target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)

    shutil.move(str(saved_path), str(target))
    return str(target)


def load_h2o(
    folder_path: Union[str, Path] = ".",
    filename: Optional[str] = None,
    *,
    init_if_needed: bool = True,
    n_cores: Optional[int] = None,
    max_mem_size: str = "8G",
    silent: bool = True,
) -> object:
    """
    Load an H2O model previously saved with `h2o.save_model` (possibly renamed by `save_h2o`).
    """
    h2o = _import_h2o()
    folder = Path(folder_path)

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

    if filename:
        target = folder / filename
        if not target.exists():
            raise FileNotFoundError(f"Specified H2O model artifact not found: {target}")
    else:
        if not folder.exists() or not folder.is_dir():
            raise FileNotFoundError(f"Folder not found or not a directory: '{folder}'")
        items = list(folder.iterdir())
        candidates = [f for f in items if (f.is_dir()) or (f.is_file() and f.suffix.lower() == ".zip")]
        if not candidates:
            raise FileNotFoundError(
                f"No H2O model artifacts found under '{folder}'. Expected a directory or a .zip file."
            )
        target = max(candidates, key=lambda f: f.stat().st_mtime)

    model = h2o.load_model(str(target))
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
    Train an H2O AutoML model and return the leader. Optionally save the leader with a custom name.
    """
    if not variables:
        raise ValueError("`variables` must be a non-empty list.")
    if len(variables) != len(set(variables)):
        raise ValueError("`variables` contains duplicates.")
    missing = set(variables + [value]) - set(df.columns)
    if missing:
        raise ValueError(f"Columns not found in df: {sorted(missing)}")

    if "set" in df.columns:
        df_train = df.loc[df["set"] == "training", [value] + variables]
        if df_train.empty:
            df_train = df[[value] + variables]
    else:
        df_train = df[[value] + variables]

    cfg: Dict[str, Any] = {
        "max_models": 10,
        "nfolds": 5,
        "max_mem_size": "16G",
        "include_algos": ["GBM"],
        "sort_metric": "deviance",
        "save_model": False,
        "folder_path": ".",
        "filename": "automl",
        "seed": seed,
        "verbose": verbose,
    }
    if model_config:
        cfg.update(model_config)

    h2o = init_h2o(
        n_cores=n_cores,
        max_mem_size=cfg.get("max_mem_size", "16G"),
        silent=not verbose,
    )

    fr = _to_h2o_frame(df_train)
    response = value
    predictors = [c for c in fr.columns if c != response]
    if not predictors:
        raise ValueError("No predictor columns available after preprocessing.")
    fr = _coerce_numeric(fr, predictors)

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
        save_h2o(leader, folder_path=cfg.get("folder_path", "."), filename=cfg.get("filename", "automl"))

    setattr(leader, "backend", "h2o")
    return leader


def stop_h2o(quiet: bool = True) -> None:
    """
    Shut down the attached H2O cluster if available.
    """
    try:
        h2o = _import_h2o()
        cl = h2o.cluster()
        if cl is not None:
            cl.shutdown(prompt=not quiet)
            log.info("H2O cluster shutdown requested.")
    except Exception as e:
        log.debug("H2O shutdown skipped: %s", e)
