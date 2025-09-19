# src/normet/causal/scm.py
from __future__ import annotations

import time
import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from scipy.optimize import minimize, LinearConstraint, Bounds
from typing import Any, Dict, List, Optional

from ..utils.logging import get_logger

log = get_logger(__name__)

__all__ = ["scm"]


def scm(
    df: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "code",
    outcome_col: str = "poll",
    treated_unit: Optional[str] = None,
    cutoff_date: Optional[str] = None,
    donors: Optional[List[str]] = None,
    pre_covariates: Optional[List[str]] = None,
    alphas: Optional[List[float]] = None,
    allow_negative_weights: bool = False,
) -> Dict[str, Any]:
    """
    Augmented Synthetic Control Method (SCM) for a single treated unit.

    Fits a ridge-augmented outcome model at each time point using pre-treatment
    information, then balances donor residuals to construct a synthetic counterfactual
    for the treated unit. Returns the treated series, synthetic series, and effect
    (observed − synthetic), plus donor weights and per-time ridge alphas.

    Parameters
    ----------
    df : pandas.DataFrame
        Long panel with columns at least `[date_col, unit_col, outcome_col]`.
    date_col : str, optional
        Name of the time index column. Default "date".
    unit_col : str, optional
        Name of the unit identifier column. Default "code".
    outcome_col : str, optional
        Name of the outcome variable column. Default "poll".
    treated_unit : str, optional
        Identifier of the treated unit. Required.
    cutoff_date : str, optional
        Treatment start date in "YYYY-MM-DD" format. Required.
    donors : List[str] | None, optional
        Donor pool. If None, uses all units except `treated_unit` that appear in `df`.
    pre_covariates : List[str] | None, optional
        Additional unit-level covariates to augment ridge features using *pre-period means*.
        If provided, rows with missing pre-period means are dropped for affected units.
    alphas : List[float] | None, optional
        RidgeCV alpha grid. Default is `[0.1, 0.2, ..., 10.0]`.
    allow_negative_weights : bool, optional
        If True, donor weights may be negative (sum-to-one constraint retained).
        If False (default), simplex constraints are enforced: w_j ≥ 0, ∑ w_j = 1.

    Returns
    -------
    dict
        {
          "synthetic": pandas.DataFrame,
              # index: date
              # columns: ["observed", "synthetic", "effect"]
          "weights": pandas.Series,
              # donor weights indexed by donor unit (sum=1 if negatives not allowed)
          "alpha": dict
              # mapping timestamp -> chosen RidgeCV alpha (diagnostics)
        }

    Raises
    ------
    ValueError
        If required inputs are missing, the treated unit is not in the panel,
        no valid donors remain after filtering, or there are insufficient aligned
        pre-period rows to estimate weights.

    Notes
    -----
    - The ridge features are constructed from *pre-treatment* outcomes (and optional
      pre-period covariate means), held fixed across time when fitting/predicting.
    - Residual balancing solves a quadratic program with an equality constraint
      (weights sum to 1) and optional non-negativity bounds.
    - Very short pre-periods or heavy missingness can lead to unstable estimates.
    """
    t0 = time.time()

    if treated_unit is None or cutoff_date is None:
        raise ValueError("Both `treated_unit` and `cutoff_date` must be provided.")

    # --- Parse/validate dates without renaming the column ---
    df = df.copy()
    if date_col not in df.columns:
        raise ValueError(f"`date_col` '{date_col}' not found in df.")
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    if df[date_col].isna().any():
        n_bad = int(df[date_col].isna().sum())
        raise ValueError(f"{n_bad} rows have invalid {date_col} values.")
    cutoff_ts = pd.to_datetime(cutoff_date)

    # --- Pivot to wide panel: rows=time, cols=units, values=outcome ---
    panel = (
        df.pivot_table(index=date_col, columns=unit_col, values=outcome_col, aggfunc="mean")
          .sort_index()
    )
    if treated_unit not in panel.columns:
        raise ValueError(f"Treated unit '{treated_unit}' not in panel.")
    if donors is None:
        donors = [u for u in panel.columns if u != treated_unit]
    else:
        donors = [u for u in donors if u in panel.columns and u != treated_unit]
    if not donors:
        raise ValueError("No valid donors after filtering.")

    # --- Pre/post masks & slices ---
    pre_idx = panel.index < cutoff_ts
    post_idx = ~pre_idx
    dates_pre = panel.index[pre_idx]
    dates_post = panel.index[post_idx]
    if dates_pre.size < 3:
        log.warning("Very short pre-period (%d timestamps); results may be unstable.", dates_pre.size)

    # --- Build ridge feature matrices using *pre* outcomes (+ covariates means if provided) ---
    Y_pre = panel.loc[dates_pre, donors + [treated_unit]]
    Y_pre = Y_pre.dropna(how="any")  # ensure aligned outcome vectors for all donors+treated in pre
    if Y_pre.empty or Y_pre.shape[0] < 3:
        raise ValueError("Not enough complete pre-treatment rows after dropping NaNs.")

    X_donors = Y_pre[donors].T.values                       # shape: J x T_pre
    X_treated = Y_pre[treated_unit].values.reshape(1, -1)   # shape: 1 x T_pre

    # Optional: augment with pre-period covariate means
    if pre_covariates:
        cov_df = (
            df.loc[df[date_col] < cutoff_ts, [unit_col] + pre_covariates]
              .groupby(unit_col, dropna=False)[pre_covariates].mean()
        )
        cov_df = cov_df.reindex(donors + [treated_unit])
        if cov_df.isna().any().any():
            log.warning("Missing covariate means for some units; rows with NaN will be dropped.")
            cov_df = cov_df.dropna(how="any")
            # reindex donors list accordingly if needed
            valid_units = cov_df.index.tolist()
            donors = [u for u in donors if u in valid_units]
            if treated_unit not in valid_units or not donors:
                raise ValueError("Covariates removal left no valid donor/treated units.")
            # rebuild Y_pre / X matrices to match filtered units
            Y_pre = panel.loc[dates_pre, donors + [treated_unit]].dropna(how="any")
            X_donors = Y_pre[donors].T.values
            X_treated = Y_pre[treated_unit].values.reshape(1, -1)

        X_donors = np.hstack([X_donors, cov_df.loc[donors].values])
        X_treated = np.hstack([X_treated, cov_df.loc[[treated_unit]].values])

    # --- Ridge helper over donors at each time t (using X from pre) ---
    if alphas is None:
        alphas = [i / 10 for i in range(1, 101)]  # 0.1..10

    def fit_ridge(y_donors: np.ndarray, Xd: np.ndarray, Xt: np.ndarray):
        """Fit RidgeCV (donor outcomes y at time t) ~ Xd; predict for treated Xt and donors Xd."""
        mask = np.isfinite(y_donors)
        if mask.sum() < 3:
            return np.nan, np.nan, np.full_like(y_donors, np.nan, dtype=float)
        mdl = RidgeCV(alphas=alphas, fit_intercept=True)
        mdl.fit(Xd[mask], y_donors[mask])
        return mdl.alpha_, float(mdl.predict(Xt)[0]), mdl.predict(Xd)

    # --- Augmented predictions per time t ---
    alpha_map: Dict[pd.Timestamp, float] = {}
    m_treated = pd.Series(index=panel.index, dtype=float)
    m_donors = pd.DataFrame(index=panel.index, columns=donors, dtype=float)

    log.info("Fitting ridge augmentation across %d timestamps …", len(panel.index))
    for t in panel.index:
        y_t = panel.loc[t, donors].to_numpy()
        a_t, mtr, mdon = fit_ridge(y_t, X_donors, X_treated)
        alpha_map[t] = a_t
        m_treated.loc[t] = mtr
        m_donors.loc[t] = mdon

    # --- Residuals (observed - augmented prediction) ---
    R_don = panel[donors] - m_donors
    r_treat = panel[treated_unit] - m_treated

    # Align pre-period residual matrices (avoid separate dropna that misaligns)
    pre_common = R_don.loc[dates_pre].dropna(how="any")
    r_pre = r_treat.loc[pre_common.index].to_numpy()
    R_pre = pre_common.to_numpy()

    if R_pre.shape[0] < 3:
        raise ValueError("Insufficient aligned pre-period residual rows to estimate weights.")

    # --- Quadratic program: minimize || r_pre - R_pre w ||^2 subject to constraints ---
    def obj(w: np.ndarray) -> float:
        return float(np.sum((r_pre - R_pre @ w) ** 2))

    def grad(w: np.ndarray) -> np.ndarray:
        return (2.0 * R_pre.T @ (R_pre @ w - r_pre)).astype(float)

    J = len(donors)
    Aeq, beq = np.ones((1, J)), np.array([1.0])
    bounds = (
        Bounds([-np.inf] * J, [np.inf] * J)
        if allow_negative_weights
        else Bounds([0.0] * J, [1.0] * J)
    )
    cons = [LinearConstraint(Aeq, beq, beq)]
    w0 = np.full(J, 1.0 / J)

    res = minimize(obj, w0, jac=grad, method="trust-constr", constraints=cons, bounds=bounds)
    if not res.success:
        log.warning("Weight optimization did not converge (status: %s). Using initial weights.", res.status)
        w = w0
    else:
        w = res.x
    if not allow_negative_weights:
        w = np.maximum(w, 0.0)
        s = w.sum()
        w = w / s if s > 0 else w0

    weights = pd.Series(w, index=donors, name="weight")

    # --- Synthetic path over full horizon ---
    synth = m_treated + (R_don @ weights)
    out = pd.DataFrame({"observed": panel[treated_unit], "synthetic": synth})
    out["effect"] = out["observed"] - out["synthetic"]

    log.info("SCM finished in %.2fs | pre T=%d | donors=%d", time.time() - t0, len(dates_pre), len(donors))
    return {"synthetic": out, "weights": weights, "alpha": alpha_map}
