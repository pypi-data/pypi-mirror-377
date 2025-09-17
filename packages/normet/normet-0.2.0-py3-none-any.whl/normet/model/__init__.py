# src/normet/model/__init__.py
"""
Model training, prediction, and persistence utilities
=====================================================

This subpackage provides a unified interface for training,
predicting, saving, and loading models across supported
AutoML backends (FLAML, H2O).
"""

from .train import build_model, train_model
from .predict import ml_predict
from .io import load_model, save_model

__all__ = [
    "build_model",
    "train_model",
    "ml_predict",
    "load_model",
    "save_model",
]
