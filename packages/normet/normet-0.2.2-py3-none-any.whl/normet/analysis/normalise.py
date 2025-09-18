# src/normet/analysis/normalise.py
import os
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from typing import List, Optional

from ..model.predict import ml_predict
from ..utils.prepare import process_date, check_data
from ..utils.logging import get_logger

log = get_logger(__name__)


def generate_resampled(
    df: pd.DataFrame,
    variables_resample: List[str],
    replace: bool,
    seed: int,
    verbose: bool,
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate a resampled copy of the dataset by replacing selected predictors
    with values drawn from a weather reference pool.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset to be resampled. Must include the target ``value`` and
        a ``date`` column.
    variables_resample : List[str]
        Predictor columns to resample from ``weather_df``.
    replace : bool
        If True, sample with replacement. If False, sample without replacement.
    seed : int
        Random seed for reproducibility of the resampling.
    verbose : bool
        Retained for API compatibility; progress is logged via logger.
    weather_df : pandas.DataFrame
        Pool of data used to resample the specified predictors. Must contain
        all columns listed in ``variables_resample``.

    Returns
    -------
    pandas.DataFrame
        Copy of ``df`` with:
          - specified ``variables_resample`` columns replaced by resampled values,
          - a new column ``seed`` indicating the resampling seed used.
    """
    missing = [c for c in variables_resample if c not in weather_df.columns]
    if missing:
        raise ValueError(f"`weather_df` is missing columns: {missing}")

    pool = weather_df[variables_resample].sample(
        n=len(df), replace=replace, random_state=seed
    ).reset_index(drop=True)

    out = df.copy(deep=False).reset_index(drop=True)
    out.loc[:, variables_resample] = pool.to_numpy()
    out.loc[:, "seed"] = seed
    return out


def normalise(
    df: pd.DataFrame,
    model: object,
    feature_names: List[str],
    variables_resample: Optional[List[str]] = None,
    n_samples: int = 300,
    replace: bool = True,
    aggregate: bool = True,
    seed: int = 7_654_321,
    n_cores: Optional[int] = None,
    weather_df: Optional[pd.DataFrame] = None,
    memory_save: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Normalise a time series using a trained model and Monte Carlo resampling.

    This function resamples meteorological variables (or user-specified
    predictors), predicts with the supplied model, and aggregates results
    to provide deweathered estimates of the target variable.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset containing at least ``date`` (datetime64) and target
        column ``value``.
    model : object
        Trained model tagged with ``backend`` ("flaml" or "h2o").
        Must be compatible with :func:`ml_predict`.
    feature_names : List[str]
        Predictor columns used by the model.
    variables_resample : List[str], optional
        Predictors to resample from ``weather_df``. Defaults to all
        non-time predictors in ``feature_names``.
    n_samples : int, default=300
        Number of resampling iterations (unique seeds).
    replace : bool, default=True
        Whether to resample with replacement.
    aggregate : bool, default=True
        If True, average predictions across resamples. If False, return
        a wide frame with one column per seed.
    seed : int, default=7654321
        Base RNG seed (used to generate per-sample seeds).
    n_cores : int, optional
        Parallel workers. Default: all cores minus one.
    weather_df : pandas.DataFrame, optional
        External resampling pool. Defaults to ``df``.
    memory_save : bool, default=False
        If True, predicts one resample at a time to reduce peak memory.
        If False, generates all resamples and predicts in batch.
    verbose : bool, default=True
        If True, logs at INFO level; if False, logs at DEBUG.

    Returns
    -------
    pandas.DataFrame
        If ``aggregate=True``:
            Indexed by ``date`` with columns:
              - observed
              - normalised
        If ``aggregate=False``:
            Indexed by ``date`` with columns:
              - observed
              - one column per seed (e.g., ``12345``).
    """
    # Preprocess and validate input data
    df = process_date(df).pipe(check_data, feature_names, "value")
    if "date" not in df.columns:
        raise ValueError("`df` must contain a 'date' column.")

    weather_df = df if weather_df is None else weather_df
    time_vars = {"date_unix", "day_julian", "weekday", "hour"}
    variables_resample = variables_resample or [c for c in feature_names if c not in time_vars]

    # Ensure variables exist in weather_df
    missing = [c for c in variables_resample if c not in weather_df.columns]
    if missing:
        raise ValueError(f"`weather_df` is missing columns required for resampling: {missing}")

    # Parallelism
    n_cores = max(1, n_cores if n_cores is not None else (os.cpu_count() or 2) - 1)

    # Unique, reproducible seeds
    rng = np.random.default_rng(seed)
    random_seeds = rng.choice(1_000_000, size=n_samples, replace=False)

    msg = (f"Normalising with {n_samples} resamples "
           f"(aggregate={aggregate}, memory_save={memory_save}, n_cores={n_cores}).")
    (log.info if verbose else log.debug)(msg)

    # Per-seed worker (used when memory_save=True)
    def process_one(seed_i: int) -> Optional[pd.DataFrame]:
        try:
            df_resampled = generate_resampled(df, variables_resample, replace, int(seed_i), verbose, weather_df)
            preds = ml_predict(model, df_resampled)
            return pd.DataFrame({
                "date": df_resampled["date"].to_numpy(),
                "observed": df_resampled["value"].to_numpy(),
                "normalised": preds,
                "seed": int(seed_i),
            })
        except Exception as e:
            log.exception(f"Error in seed {seed_i}: {e}")
            return None

    # Branch: memory-saving per-seed prediction vs. batched
    if memory_save:
        import concurrent.futures
        results: List[pd.DataFrame] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_cores) as ex:
            futures = [ex.submit(process_one, int(s)) for s in random_seeds]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res is not None:
                    results.append(res)
        if not results:
            raise RuntimeError("No successful resamples produced results.")
        df_result = pd.concat(results, ignore_index=True)
    else:
        # Generate all resamples in parallel (structure only)
        resampled_list = Parallel(n_jobs=n_cores)(
            delayed(generate_resampled)(
                df, variables_resample, replace, int(s), False, weather_df
            ) for s in random_seeds
        )
        df_all = pd.concat(resampled_list, ignore_index=True)

        # Single batched prediction
        preds = ml_predict(model, df_all)

        df_result = pd.DataFrame({
            "date": df_all["date"].to_numpy(),
            "observed": df_all["value"].to_numpy(),
            "normalised": preds,
            "seed": df_all["seed"].to_numpy(),
        })

    # Aggregate or wide output
    if aggregate:
        (log.info if verbose else log.debug)(f"Aggregating {n_samples} predictions.")
        df_out = df_result.groupby("date", as_index=True)[["observed", "normalised"]].mean()
    else:
        observed = df_result.drop_duplicates(subset=["date"]).set_index("date")[["observed"]]
        wide = df_result.pivot(index="date", columns="seed", values="normalised")
        df_out = pd.concat([observed, wide], axis=1)

    (log.info if verbose else log.debug)("Finished normalisation.")
    return df_out
