# src/normet/pipeline/interface.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Tuple, Literal, Mapping, List
import pandas as pd

# --- Import your existing primitives ---
from .do_all import do_all, do_all_unc
from ..analysis.rolling import rolling

# =========================
# Config dataclasses
# =========================
Backend = Literal["flaml", "h2o"]
SplitMethod = Literal["random", "ts", "season", "month"]

@dataclass
class SingleConfig:
    value: str
    backend: Backend = "flaml"
    feature_names: List[str] = field(default_factory=list)
    variables_resample: Optional[List[str]] = None
    split_method: SplitMethod = "random"
    fraction: float = 0.75
    model_config: Optional[dict] = None
    n_samples: int = 300
    aggregate: bool = True
    seed: int = 7_654_321
    n_cores: Optional[int] = None
    memory_save: bool = False
    verbose: bool = True

@dataclass
class UncConfig(SingleConfig):
    n_models: int = 10
    confidence_level: float = 0.95
    # Note: do_all_unc always aggregates internally; SingleConfig.aggregate is ignored.

@dataclass
class RollingConfig:
    value: str
    backend: Backend = "flaml"
    feature_names: Optional[List[str]] = None
    variables_resample: Optional[List[str]] = None
    split_method: SplitMethod = "random"
    fraction: float = 0.75
    model_config: Optional[dict] = None
    n_samples: int = 300
    window_days: int = 14
    rolling_every: int = 7
    seed: int = 7_654_321
    n_cores: Optional[int] = None
    memory_save: bool = False
    verbose: bool = True

# =========================
# Adapters (align with function signatures)
# =========================
def _single_adapter(cfg: SingleConfig) -> dict:
    # do_all(...) → (out, model, mod_stats)
    return dict(
        value=cfg.value,
        backend=cfg.backend,
        feature_names=cfg.feature_names or None,
        variables_resample=cfg.variables_resample,
        split_method=cfg.split_method,
        fraction=cfg.fraction,
        model_config=cfg.model_config,
        n_samples=cfg.n_samples,
        aggregate=cfg.aggregate,
        seed=cfg.seed,
        n_cores=cfg.n_cores,
        memory_save=cfg.memory_save,
        verbose=cfg.verbose,
    )

def _unc_adapter(cfg: UncConfig) -> dict:
    # do_all_unc(...) → (out, mod_stats)
    base = _single_adapter(cfg)
    base.update(
        n_models=cfg.n_models,
        confidence_level=cfg.confidence_level,
    )
    base.pop("aggregate", None)
    return base

def _rolling_adapter(cfg: RollingConfig) -> dict:
    # rolling(...) returns a DataFrame
    return dict(
        value=cfg.value,
        backend=cfg.backend,
        feature_names=cfg.feature_names,
        variables_resample=cfg.variables_resample,
        split_method=cfg.split_method,
        fraction=cfg.fraction,
        model_config=cfg.model_config,
        n_samples=cfg.n_samples,
        window_days=cfg.window_days,
        rolling_every=cfg.rolling_every,
        seed=cfg.seed,
        n_cores=cfg.n_cores,
        memory_save=cfg.memory_save,
        verbose=cfg.verbose,
    )

Mode = Literal["single", "unc", "rolling"]

_REGISTRY: Mapping[
    Mode,
    Tuple[Callable[..., Any], Callable[[Any], dict]]
] = {
    "single":  (lambda *, df, **kw: do_all(df=df, **kw), _single_adapter),
    "unc":     (lambda *, df, **kw: do_all_unc(df=df, **kw), _unc_adapter),
    "rolling": (lambda *, df, **kw: rolling(df=df, **kw), _rolling_adapter),
}

# =========================
# Entry point
# =========================
def run_workflow(mode: Mode, df: pd.DataFrame, config: Any) -> Any:
    """
    Run a workflow by mode with its config dataclass.

    Returns
    -------
    - mode == "single" : (out: DataFrame, model: object, mod_stats: DataFrame)
    - mode == "unc"    : (out: DataFrame, mod_stats: DataFrame)
    - mode == "rolling": out: DataFrame
    """
    if mode not in _REGISTRY:
        raise ValueError(f"Unknown mode '{mode}'. Available: {list(_REGISTRY)}")

    runner, adapter = _REGISTRY[mode]
    kwargs = adapter(config)
    return runner(df=df, **kwargs)
