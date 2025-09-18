# src/normet/model/io.py
from __future__ import annotations

from pathlib import Path
from typing import Union, Literal

from ..backends.flaml_backend import save_flaml, load_flaml
from ..backends.h2o_backend import save_h2o, load_h2o
from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = ["load_model", "save_model"]

# -------------------------
# Public API
# -------------------------
def load_model(
    folder_path: Union[str, Path] = ".",
    backend: Literal["flaml", "h2o"] = "flaml",
    filename: str = "automl.joblib",
) -> object:
    """
    Load a previously saved model.

    Parameters
    ----------
    folder_path : str | pathlib.Path, default="."
        Path to the saved model file or directory:
          - FLAML: a ``.joblib`` file, or a folder containing ``filename``.
          - H2O:   the exact path returned by ``h2o.save_model`` (usually a file),
                   or a directory that contains one.
    backend : {"flaml","h2o"}, default="flaml"
        Backend selector:
          - "flaml": load a ``.joblib``/``.pkl`` file.
          - "h2o":   load an H2O artifact.
    filename : str, default "automl.joblib"
        For FLAML: the expected filename if ``folder_path`` is a directory.
        For H2O:   optional; if provided, tries to load ``folder_path/filename``.

    Returns
    -------
    object
        The loaded model with attribute ``backend`` set to "flaml" or "h2o".

    Raises
    ------
    FileNotFoundError
        If no suitable model file is found.
    TypeError
        If backend is unsupported.
    """
    if backend == "flaml":
        # Delegate to FLAML loader
        return load_flaml(folder_path=folder_path, filename=filename)

    if backend == "h2o":
        # Delegate to H2O loader
        return load_h2o(folder_path=folder_path, filename=filename)

    raise TypeError(f"Unsupported backend '{backend}'. Expected 'flaml' or 'h2o'.")


def save_model(
    model: object,
    folder_path: Union[str, Path] = ".",
    filename: str = "automl.joblib",
) -> str:
    """
    Save a trained model by delegating to the appropriate backend saver.

    Parameters
    ----------
    model : object
        Trained model with attribute ``backend`` in {"flaml", "h2o"}.
    folder_path : str | Path, default="."
        Destination directory. Created if it does not exist.
    filename : str, default="automl.joblib"
        Output name:
          - FLAML: exact filename, must end with ``.joblib`` or ``.pkl``.
          - H2O:   desired artifact name; handled by renaming after save.

    Returns
    -------
    str
        Path to the saved artifact:
          - FLAML: full path to the ``.joblib``/``.pkl`` file.
          - H2O:   full path to the renamed model file.

    Raises
    ------
    AttributeError
        If model does not define a ``backend`` attribute.
    TypeError
        If backend is unsupported.
    """
    backend = getattr(model, "backend", None)
    if backend is None:
        raise AttributeError("Model must have a 'backend' attribute ('flaml' or 'h2o').")

    backend = str(backend).lower()

    if backend == "flaml":
        # Delegate to FLAML saver
        return save_flaml(model, folder_path=folder_path, filename=filename)

    if backend == "h2o":
        # Delegate to H2O saver
        return save_h2o(model, folder_path=folder_path, filename=filename)

    raise TypeError(f"Unsupported backend '{backend}'. Expected 'flaml' or 'h2o'.")
