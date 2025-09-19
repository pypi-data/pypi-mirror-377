"""
normet: Normalisation, Decomposition, and Counterfactual Modelling for Environmental Time-series
=================================================

High-level entry points for normalisation, decomposition,
synthetic control, modelling, and evaluation.
"""
# --- Modelling ---
from .model import (
    build_model,
    train_model,
    ml_predict,
    load_model,
    save_model,
)

# --- Evaluation & utils ---
from .utils import (
    modStats,
    prepare_data,
    process_date,
    check_data,
    impute_values,
    add_date_variables,
    split_into_sets,
)

# --- Pipelines ---
from .pipeline import do_all, do_all_unc, run_workflow

# --- Analysis ---
from .analysis import normalise, rolling, pdp, decom_emi, decom_met

# --- Synthetic control ---
from .causal import (
    scm,
    mlscm,
    placebo_in_space,
    placebo_in_time,
    effect_bands_space,
    effect_bands_time,
    uncertainty_bands,
    plot_effect_with_bands,
    plot_uncertainty_bands,
    scm_all,
)

__all__ = [
    # --- Pipelines ---
    "do_all",
    "do_all_unc",
    "run_workflow",

    # --- Analysis ---
    "normalise",
    "rolling",
    "pdp",
    "decom_emi",
    "decom_met",

    # --- Synthetic control ---
    "scm",
    "mlscm",
    "placebo_in_space",
    "placebo_in_time",
    "effect_bands_space",
    "effect_bands_time",
    "uncertainty_bands",
    "plot_effect_with_bands",
    "plot_uncertainty_bands",
    "scm_all",

    # --- Modelling ---
    "build_model",
    "train_model",
    "ml_predict",
    "load_model",
    "save_model",


    # --- Evaluation & utilities ---
    "modStats",
    "prepare_data",
    "process_date",
    "check_data",
    "impute_values",
    "add_date_variables",
    "split_into_sets",
]
