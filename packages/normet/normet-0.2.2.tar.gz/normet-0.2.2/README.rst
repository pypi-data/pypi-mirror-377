normet: Normalisation, Decomposition, and Counterfactual Modelling for Environmental Time-series
================================================================================================

``normet`` is a Python package for **environmental time-series analysis**.
It provides tools for:

- **Normalisation / deweathering** of pollutant concentrations.
- **Counterfactual modelling** using AutoML backends (FLAML, H2O).
- **Synthetic control methods** (ASCM, ML-ASCM).
- **Uncertainty quantification** via bootstrapping and placebo tests.
- **Evaluation metrics** tailored for environmental data.

The package is designed for **air-quality research**, **causal inference**, and **policy evaluation**.

---

Features
--------

- High-level pipelines for normalisation and synthetic control.
- Rolling weather normalisation for short-term trend analysis.
- Time-series decomposition separating emissions-driven and meteorology-driven variability.
- Multiple backends: `FLAML <https://microsoft.github.io/FLAML/>`_, `H2O AutoML <https://docs.h2o.ai/>`_.
- Placebo-in-space and placebo-in-time analyses for robustness checks.
- Bootstrap and jackknife-based uncertainty bands.
- Rich evaluation metrics: RMSE, FAC2, IOA, R², etc.
- Parallel execution for large panel datasets.

---

Installation
------------

Basic installation (core functionality, no AutoML backends):

.. code-block:: bash

    pip install normet

Optional backends:

- FLAML (lightweight, recommended for most users):

  .. code-block:: bash

      conda install flaml -c conda-forge

- H2O (heavier, requires Java):

  .. code-block:: bash

      pip install h2o

Install both:

.. code-block:: bash

    pip install normet[all]

---

Quick Start
-----------

A quick example with the :func:`do_all` pipeline:

.. code-block:: python

    import pandas as pd
    from normet import do_all, modStats

    # Example dataset (must contain datetime + target + predictors)
    df = pd.read_csv("example.csv")

    # Run the pipeline
    out, model, df_prep = do_all(
        df,
        value="pm25",
        backend="flaml",
        feature_names=["temp", "wind", "humidity"],
        n_samples=300,
    )

    # Results
    print(out.head())        # Normalised (deweathered) time-series
    print(df_prep.head())    # Prepared dataset with splits & features
    print(model)             # Trained AutoML model

    # Evaluate model performance manually
    stats = modStats(df_prep, model)
    print(stats)

The pipeline performs:

1. **Data preparation** — parse datetime, validate target/features, impute values, add date-based covariates, and split into training/testing.
2. **Model training** — trains a model using AutoML (FLAML or H2O).
3. **Normalisation** — resamples weather covariates and estimates counterfactual ("deweathered") series.

Returned values:

- ``out``: DataFrame with observed and normalised series (and resample outputs if ``aggregate=False``).
- ``model``: the trained AutoML model object.
- ``df_prep``: prepared dataset after preprocessing and splitting.

---

EMI decomposition (emissions-driven component):

.. code-block:: python

    from normet.analysis.decomposition import decom_emi

    emi = decom_emi(
        df=df,
        value="pm25",
        backend="flaml",
        feature_names=["temp", "wind", "humidity"],
        n_samples=200,
    )

    print(emi.head())
    # Columns include:
    # observed, date_unix, day_julian, weekday, hour,
    # emi_total, emi_noise, emi_base

MET decomposition (meteorology-driven component):

.. code-block:: python

    from normet.analysis.decomposition import decom_met

    met = decom_met(
        df=df,
        value="pm25",
        backend="flaml",
        feature_names=["temp", "wind", "humidity"],
        n_samples=200,
    )

    print(met.head())
    # Columns include:
    # observed, emi_total, <each meteorological feature>,
    # met_total, met_base, met_noise

---

Run augmented synthetic control (ASCM):

.. code-block:: python

    from normet.scm import _run_syn

    syn = _run_syn(
        df=df_panel,
        date_col="date",
        unit_col="city",
        outcome_col="pm25",
        treated_unit="Beijing",
        cutoff_date="2017-01-01",
        donors=["Shanghai", "Guangzhou", "Chengdu"],
        ascm_backend="ascm",
    )

    print(syn.head())  # observed, synthetic, effect

Placebo-in-space test:

.. code-block:: python

    from normet.scm import placebo_in_space, effect_bands_space

    out = placebo_in_space(
        df=df_panel,
        date_col="date",
        unit_col="city",
        outcome_col="pm25",
        treated_unit="Beijing",
        cutoff_date="2017-01-01",
    )

    bands = effect_bands_space(out, level=0.95)
    print(bands.head())

Placebo-in-time test:

.. code-block:: python

    from normet.scm import placebo_in_time

    out_time = placebo_in_time(
        df=df_panel,
        date_col="date",
        unit_col="city",
        outcome_col="pm25",
        treated_unit="Beijing",
        cutoff_date="2017-01-01",
        ascm_backend="ascm", #'ascm' or 'mlascm'
        n_rep=50,  # number of pseudo cutoffs to test
    )

    print(out_time.head())

---

Uncertainty Quantification
--------------------------

Uncertainty bands can be constructed using either **bootstrap** or **jackknife** methods:

.. code-block:: python

    from normet.scm import uncertainty_bands, plot_uncertainty_bands

    # Bootstrap version
    boot = uncertainty_bands(
        df=df_panel,
        date_col="date",
        unit_col="city",
        outcome_col="pm25",
        treated_unit="Beijing",
        cutoff_date="2017-01-01",
        ascm_backend="ascm",
        method="bootstrap",   # donor/time resampling
        B=200,
    )

    plot_uncertainty_bands(boot, cutoff_date="2017-01-01")

    # Jackknife version
    jack = uncertainty_bands(
        df=df_panel,
        date_col="date",
        unit_col="city",
        outcome_col="pm25",
        treated_unit="Beijing",
        cutoff_date="2017-01-01",
        ascm_backend="ascm",
        method="jackknife",   # leave-one-donor-out
        ci_level=0.95,
    )

    plot_uncertainty_bands(jack, cutoff_date="2017-01-01")

---

Requirements
------------

- Python >= 3.9
- numpy >= 1.22
- pandas >= 1.5
- scipy >= 1.10
- joblib >= 1.2
- matplotlib >= 3.6

Optional:
- flaml >= 2.1
- h2o >= 3.44

---

Citation
--------

If you use ``normet`` in your research, please cite:

::

    Song, C. (2025).
    normet: Normalisation, Decomposition, and Counterfactual Modelling for Environmental Time-series.
    University of Manchester. GitHub repository: https://github.com/dsncas/normet

---

License
-------

This project is licensed under the MIT License.

---

Contributing
------------

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with clear description and tests.

Bug reports and feature requests can be submitted via
the `issue tracker <https://github.com/dsncas/normet/issues>`_.
