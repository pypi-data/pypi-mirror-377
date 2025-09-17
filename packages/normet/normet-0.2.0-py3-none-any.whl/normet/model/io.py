# src/normet/model/io.py
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union, Literal

from ..backends.flaml_backend import save_flaml
from ..backends.h2o_backend import _import_h2o, save_h2o
from ..utils._lazy import require
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = ["load_model", "save_model"]


# -------------------------
# Helpers
# -------------------------
def _detect_backend(model_path: Path) -> Optional[str]:
    """
    Best-effort backend detection from files on disk.

    Rules:
      - If a *.joblib file is given (or the directory contains a single *.joblib),
        assume FLAML.
      - Otherwise assume H2O if the path exists (H2O stores non-joblib artifacts).
      - Return None if nothing exists / ambiguous.
    """
    if model_path.is_file():
        if model_path.suffix.lower() == ".joblib":
            return "flaml"
        # H2O save_model returns a *file* path without .joblib; treat as H2O
        return "h2o"

    if model_path.is_dir():
        joblibs = list(model_path.glob("*.joblib"))
        if len(joblibs) == 1:
            return "flaml"
        if len(joblibs) > 1:
            # Ambiguous, but overwhelmingly this is a FLAML model zoo; still return 'flaml'
            return "flaml"
        # No joblibs found: likely an H2O directory or a bare path for load_model
        return "h2o"

    return None


def _resolve_flaml_file(model_path: Path, model_name: str) -> Path:
    """Return the FLAML .joblib file to load, trying model_name then single *.joblib in the dir."""
    if model_path.is_file() and model_path.suffix.lower() == ".joblib":
        return model_path

    if model_path.is_dir():
        candidate = model_path / f"{model_name}.joblib"
        if candidate.exists():
            return candidate
        joblibs = list(model_path.glob("*.joblib"))
        if len(joblibs) == 1:
            return joblibs[0]

    raise FileNotFoundError(
        f"Could not find FLAML joblib under '{model_path}'. "
        f"Tried '{model_name}.joblib' and scanning for a single *.joblib file."
    )


# -------------------------
# Public API
# -------------------------
def load_model(
    model_path: Union[str, Path],
    backend: Optional[Literal["flaml", "h2o"]] = None,
    model_name: str = "automl",
) -> object:
    """
    Load a previously saved model, with backend auto-detection.

    Parameters
    ----------
    model_path : str | pathlib.Path
        Path to the saved model directory or file:
          - FLAML: a ``.joblib`` file, or a folder containing ``<model_name>.joblib``.
          - H2O: the exact path returned by ``h2o.save_model`` (usually a file),
                 or a directory that contains that file.
    backend : {"flaml","h2o"} | None, optional
        If provided, forces the loader for that backend. If None, the loader tries
        to detect the backend from files on disk.
    model_name : str, default "automl"
        Base name used to locate FLAML joblib if ``model_path`` is a directory.

    Returns
    -------
    object
        The loaded model with ``backend`` attribute set to "flaml" or "h2o".
    """
    p = Path(model_path)

    # Decide backend
    use_backend = (backend or "").lower() or _detect_backend(p)
    if not use_backend:
        raise RuntimeError(
            f"Could not auto-detect backend from '{p}'. "
            f"Pass backend='flaml' or backend='h2o' explicitly."
        )

    if use_backend == "flaml":
        joblib = require("joblib", hint="pip install joblib")
        file_path = _resolve_flaml_file(p, model_name)
        model = joblib.load(str(file_path))
        setattr(model, "backend", "flaml")
        log.info("Loaded FLAML model from %s", file_path)
        return model

    if use_backend == "h2o":
        h2o = _import_h2o()

        # h2o.load_model expects the FULL file path returned by save_model.
        # If a directory is given, try to find a single non-joblib file inside.
        load_target = p
        if p.is_dir():
            # Prefer files that look like H2O model artifacts (no .joblib)
            candidates = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() != ".joblib"]
            if len(candidates) == 1:
                load_target = candidates[0]
            elif len(candidates) == 0:
                # Fall back to passing the directory; h2o.load_model may still resolve it.
                pass
            else:
                # If multiple files exist, we cannot be sure—ask user to point to exact file
                raise FileNotFoundError(
                    f"Multiple files found in '{p}'. Please provide the exact H2O model file path."
                )

        if not load_target.exists():
            raise FileNotFoundError(f"H2O model path not found: {load_target}")

        model = h2o.load_model(str(load_target))
        setattr(model, "backend", "h2o")
        log.info("Loaded H2O model from %s", load_target)
        return model

    raise TypeError(f"Unsupported backend '{backend}'. Expected 'flaml' or 'h2o'.")


def save_model(model: object, model_path: Union[str, Path], model_name: str = "automl") -> str:
    """
    Save a model by delegating to the appropriate backend saver.

    Parameters
    ----------
    model : object
        Trained model with ``backend`` attribute in {"flaml","h2o"}.
    model_path : str | pathlib.Path
        Destination directory (created if needed).
    model_name : str, default "automl"
        Base filename (FLAML) or label (H2O logging only).

    Returns
    -------
    str
        Path to the saved artifact:
          - FLAML: full path to ``.joblib`` file.
          - H2O:   path string returned by ``h2o.save_model``.
    """
    b = getattr(model, "backend", None)
    if b is None:
        raise AttributeError("Model must have a 'backend' attribute ('flaml' or 'h2o').")

    b = str(b).lower()
    model_path = str(model_path)

    if b == "flaml":
        return save_flaml(model, model_path, model_name)

    if b == "h2o":
        return save_h2o(model, model_path, model_name)

    raise TypeError(f"Unsupported backend '{b}'. Expected 'flaml' or 'h2o'.")
