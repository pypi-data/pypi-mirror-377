# src/normet/model/predict.py
from __future__ import annotations

import os
from typing import Optional, List

import numpy as np
import pandas as pd

from ..utils.features import extract_features
from ..utils._lazy import require
from ..utils.logging import get_logger

log = get_logger(__name__)


def ml_predict(model, newdata: pd.DataFrame, parallel: bool = True) -> np.ndarray:
    """
    Predict using a trained AutoML model (H2O or FLAML).

    Parameters
    ----------
    model : object
        Trained model with attribute ``backend`` in {"h2o","flaml"} and a
        ``predict`` method compatible with that backend.
    newdata : pandas.DataFrame
        Feature matrix for prediction. Must contain the columns used by the model.
    parallel : bool, default True
        H2O only: request multi-threaded conversion when bringing predictions
        to NumPy.

    Returns
    -------
    numpy.ndarray
        1D float array of predictions aligned to ``newdata`` rows used.

    Raises
    ------
    TypeError
        If the model's backend is unsupported.
    ValueError
        If none of the model's features are present in ``newdata``.
    """
    model_type = getattr(model, "backend", None)
    if model_type not in {"h2o", "flaml"}:
        raise TypeError("Unsupported model type: `backend` must be 'h2o' or 'flaml'.")

    # Try to respect the model's feature order
    try:
        feature_cols: List[str] = extract_features(model)
        use_cols = [c for c in feature_cols if c in newdata.columns]
        if len(use_cols) != len(feature_cols):
            missing = [c for c in feature_cols if c not in newdata.columns]
            if missing:
                log.warning("Missing features in newdata (excluded from prediction): %s", missing)
        if not use_cols:
            raise ValueError("No model features found in `newdata`.")
        X = newdata.loc[:, use_cols]
    except Exception as e:
        log.debug("extract_features failed (%s); falling back to all columns in `newdata`.", e)
        X = newdata
        if X.shape[1] == 0:
            raise ValueError("`newdata` has no columns to predict on.") from e

    n_rows = len(X)
    if n_rows == 0:
        return np.array([], dtype=float)

    try:
        if model_type == "h2o":
            h2o = require("h2o", hint="pip install h2o==3.*")

            # Heuristic batch sizing to avoid large H2OFrames blowing up memory
            target_mb = _auto_target_mb(model)
            try:
                jvm_expand = float(os.getenv("NM_H2O_JVM_EXPANSION", "1.5"))
            except Exception:
                jvm_expand = 1.5
            jvm_expand = min(max(jvm_expand, 1.0), 4.0)

            bytes_total = int(max(1, X.memory_usage(deep=True).sum()))
            bytes_per_row = int(max(1, bytes_total // n_rows))
            target_bytes = int(target_mb * 1024 * 1024)
            est_row_bytes = int(max(1, bytes_per_row * jvm_expand))
            auto_batch = int(max(1, min(n_rows, target_bytes // est_row_bytes)))
            # clamp to a practical range
            auto_batch = int(max(10_000, min(auto_batch, 1_000_000)))

            use_mt = bool(parallel)
            coltypes = {c: "real" for c in X.columns}

            if n_rows <= auto_batch:
                hf = h2o.H2OFrame(X, column_types=coltypes)
                try:
                    preds_df = model.predict(hf).as_data_frame(use_multi_thread=use_mt)
                finally:
                    try:
                        h2o.remove(hf)
                    except Exception:
                        pass
                yhat = preds_df.to_numpy()[:, 0]
            else:
                parts: List[np.ndarray] = []
                for start in range(0, n_rows, auto_batch):
                    stop = min(start + auto_batch, n_rows)
                    hchunk = h2o.H2OFrame(X.iloc[start:stop], column_types=coltypes)
                    try:
                        p = model.predict(hchunk).as_data_frame(use_multi_thread=use_mt).to_numpy()
                    finally:
                        try:
                            h2o.remove(hchunk)
                        except Exception:
                            pass
                    parts.append(p[:, 0])
                yhat = np.concatenate(parts, axis=0)

        else:  # FLAML / sklearn-like
            yhat = model.predict(X)

        return np.asarray(yhat, dtype=float).reshape(-1)

    except AttributeError:
        log.exception("Prediction failed: missing method or invalid input.")
        raise
    except Exception:
        log.exception("Unexpected error during prediction.")
        raise


def _auto_target_mb(model) -> int:
    """
    Resolve target batch size (MB) for H2O predictions.

    Priority:
      1) ``model._predict_batch_mb`` (int-like)
      2) env ``NM_H2O_BATCH_MB`` (int)
      3) ~25% of available RAM (via psutil), clamped to [128, 4096] MB;
         fallback 512 MB if psutil unavailable.
    """
    val = getattr(model, "_predict_batch_mb", None)
    if val is not None:
        try:
            mb = int(val)
            return max(64, min(mb, 4096))
        except Exception:
            pass

    env_val = os.getenv("NM_H2O_BATCH_MB")
    if env_val is not None:
        try:
            mb = int(env_val)
            return max(64, min(mb, 4096))
        except Exception:
            pass

    try:
        psutil = require("psutil", hint="pip install psutil")
        avail_bytes = psutil.virtual_memory().available
        auto_mb = int((avail_bytes * 0.25) // (1024 * 1024))
        return int(max(128, min(auto_mb, 4096)))
    except Exception:
        return 512
