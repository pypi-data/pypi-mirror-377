# --- Core methods ------------------------------------------------------------
from .ascm import ascm

# mlascm may require optional deps; fail gracefully with a helpful error.
try:
    from .mlascm import mlascm
    _HAS_MLASCM = True
except Exception as _e:
    _HAS_MLASCM = False
    _MLASCM_IMPORT_ERR = _e

    def mlascm(*args, **kwargs):  # type: ignore[override]
        raise ImportError(
            "mlascm is unavailable because its optional dependencies failed to import. "
            f"Original error: {_MLASCM_IMPORT_ERR}\n"
            "Install an AutoML backend (e.g., flaml or h2o) and ensure it's importable."
        )

# --- Placebo tests -----------------------------------------------------------
from .placebo import placebo_in_space, placebo_in_time

# --- Bands & uncertainty -----------------------------------------------------
from .bands import (
    effect_bands_space,
    effect_bands_time,
    uncertainty_bands,
    plot_effect_with_bands,
    plot_uncertainty_bands)

# --- Batch runner ------------------------------------------------------------
from .batch import scm_all

# --- Simple backend registry -------------------------------------------------
BACKENDS = {
    "ascm": ascm,
    "mlascm": mlascm,
}

__all__ = [
    # core
    "ascm",
    "mlascm",
    # placebo
    "placebo_in_space",
    "placebo_in_time",
    # bands
    "effect_bands_space",
    "effect_bands_time",
    "uncertainty_bands",
    "plot_effect_with_bands",
    "plot_uncertainty_bands",
    # batch
    "scm_all",
    # registry
    "BACKENDS",
]
