# src/normet/utils/features.py
from __future__ import annotations

from typing import List, Set, Optional
import numpy as np

from ..utils.logging import get_logger

log = get_logger(__name__)


def extract_features(model, importance_ascending: bool = False) -> List[str]:
    """
    Extract and sort feature names from an AutoML model.

    Supports models trained via H2O or FLAML. For FLAML, LightGBM booster
    importances are preferred when available; otherwise falls back to
    scikit-learn–style attributes.

    Parameters
    ----------
    model : object
        Trained AutoML model with attribute ``backend`` in {"h2o","flaml"}.
    importance_ascending : bool, default=False
        If True, sort features by importance ascending (least → most).
        If False (default), sort descending (most → least).

    Returns
    -------
    List[str]
        Feature names ordered by importance. If all importances are equal
        or unavailable, returns the raw feature order.

    Raises
    ------
    AttributeError
        If the model does not expose feature names/importances.
    TypeError
        If ``backend`` is unsupported.
    """
    model_type = getattr(model, "backend", None)

    # -------------------------
    # H2O path
    # -------------------------
    if model_type == "h2o":
        # H2O GBM/AutoML exposes varimp via model.varimp(use_pandas=True)
        try:
            varimp_df = model.varimp(use_pandas=True)
        except Exception as e:
            raise AttributeError(f"H2O model has no usable varimp table: {e}") from e

        # Some model types may return None or a list—handle defensively
        if varimp_df is None:
            raise AttributeError("H2O model returned None for varimp().")

        # If it's a pandas DataFrame, expect 'variable' and 'relative_importance'
        try:
            cols = set(getattr(varimp_df, "columns", []))
            if {"variable", "relative_importance"} <= cols:
                df = varimp_df[["variable", "relative_importance"]].dropna()
                df = df.sort_values("relative_importance", ascending=importance_ascending)
                names = df["variable"].astype(str).tolist()
            else:
                # Fallback: maybe it's a list of tuples [(var, rel_imp, ...), ...]
                try:
                    names = [str(t[0]) for t in varimp_df]
                except Exception:
                    raise AttributeError(
                        "H2O varimp not recognized; expected DataFrame with "
                        "['variable','relative_importance'] or list of tuples."
                    )
        except Exception as e:
            raise AttributeError(f"Failed to parse H2O varimp: {e}") from e

        # Deduplicate while keeping order
        seen: Set[str] = set()
        return [f for f in names if not (f in seen or seen.add(f))]

    # -------------------------
    # FLAML / sklearn-like path
    # -------------------------
    elif model_type == "flaml":
        est = getattr(model, "model", None)  # FLAML AutoML.model
        booster = None  # LightGBM booster if present
        feature_names: Optional[List[str]] = None
        importances: Optional[List[float]] = None

        # Try to grab LightGBM booster for consistent importances
        try:
            lgb_est = getattr(est, "estimator", est)  # handle nested estimators
            booster = getattr(lgb_est, "booster_", None) or getattr(lgb_est, "booster", None)
        except Exception:
            booster = None

        if booster is not None:
            try:
                feature_names = list(map(str, booster.feature_name()))
                importances = list(booster.feature_importance(importance_type="gain"))
            except Exception as e:
                log.debug("LightGBM booster feature importance failed: %s", e)
                booster = None  # fall through to sklearn-style

        # Fallbacks: sklearn-style attributes
        if booster is None:
            # Probe a few plausible objects for attrs
            candidates = [model, est, getattr(est, "estimator", None)]

            def _first_attr(obj, names):
                for n in names:
                    if obj is not None and hasattr(obj, n):
                        return getattr(obj, n)
                return None

            for obj in candidates:
                feature_names = _first_attr(obj, ("feature_name_", "feature_names_in_"))
                importances = _first_attr(obj, ("feature_importances_",))
                if feature_names is not None and importances is not None:
                    feature_names = list(map(str, list(feature_names)))
                    importances = list(importances)
                    log.debug("Using sklearn-style feature importances.")
                    break

        if feature_names is None or importances is None:
            raise AttributeError("FLAML estimator does not expose feature names/importances.")

        # Sanitize importances to floats; treat non-finite as 0
        clean_imps: List[float] = []
        for i in importances:
            try:
                v = float(i)
                if np.isnan(v) or not np.isfinite(v):
                    v = 0.0
            except Exception:
                v = 0.0
            clean_imps.append(v)

        # If all identical, just return the raw order
        if len(set(clean_imps)) <= 1:
            return [str(n) for n in feature_names]

        # Order by (importance, name) for deterministic tie-breaking
        order = sorted(
            range(len(feature_names)),
            key=lambda k: (clean_imps[k], str(feature_names[k])),
            reverse=not importance_ascending,
        )
        return [str(feature_names[i]) for i in order]

    # -------------------------
    # Unsupported backend
    # -------------------------
    else:
        raise TypeError(f"Unsupported model type '{model_type}'. Expected 'h2o' or 'flaml'.")
