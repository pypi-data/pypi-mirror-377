# src/normet/causal/__init__.py
# --- Core methods ------------------------------------------------------------
from .scm import scm

# mlscm may require optional deps; fail gracefully with a helpful error.
try:
    from .mlscm import mlscm
    _HAS_MLSCM = True
except Exception as _e:
    _HAS_MLSCM = False
    _MLSCM_IMPORT_ERR = _e

    def mlscm(*args, **kwargs):  # type: ignore[override]
        raise ImportError(
            "mlscm is unavailable because its optional dependencies failed to import. "
            f"Original error: {_MLSCM_IMPORT_ERR}\n"
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
    "scm": scm,
    "mlscm": mlscm,
}

__all__ = [
    # core
    "scm",
    "mlscm",
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
