# src/normet/utils/logging.py
from __future__ import annotations

import logging
import os
from typing import Literal, Union, Optional

_LOGGER_NAME = "normet"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a namespaced logger with a NullHandler attached.

    Notes
    -----
    - This ensures importing the package never configures global logging.
    - Users can call :func:`enable_default_logging` for quick stdout logging
      in scripts or notebooks.

    Parameters
    ----------
    name : str | None
        Child logger name (e.g. "backends.h2o_backend").
        If None, return the package root logger "normet".

    Returns
    -------
    logging.Logger
    """
    logger_name = f"{_LOGGER_NAME}.{name}" if name else _LOGGER_NAME
    logger = logging.getLogger(logger_name)

    # Attach a NullHandler once (avoids "No handler found" warnings).
    if not any(isinstance(h, logging.NullHandler) for h in logger.handlers):
        logger.addHandler(logging.NullHandler())

    return logger


def enable_default_logging(
    level: Union[int, Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"], None] = None,
    fmt: Optional[str] = None,
    propagate: bool = False,
) -> None:
    """
    Attach a StreamHandler to the root "normet" logger for quick, opt-in logging.

    Parameters
    ----------
    level : int | str | None
        Logging level. If None, falls back to env var ``NORMET_LOGLEVEL``.
        Defaults to INFO if neither is provided.
    fmt : str | None
        Log format string. Defaults to a concise format
        ``"%(levelname)s | %(name)s | %(message)s"``.
    propagate : bool, default=False
        Whether to propagate logs up to the global root logger.

    Notes
    -----
    - Intended for interactive use (Jupyter notebooks, quick scripts).
    - Larger applications should configure logging explicitly.
    """
    logger = get_logger()

    # Avoid stacking multiple stream handlers if called repeatedly
    if any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        return

    # Resolve log level: explicit arg > env var > default INFO
    env_level = os.getenv("NORMET_LOGLEVEL", "").upper()
    if isinstance(level, str):
        level_obj = getattr(logging, level.upper(), logging.INFO)
    elif isinstance(level, int):
        level_obj = level
    elif env_level:
        level_obj = getattr(logging, env_level, logging.INFO)
    else:
        level_obj = logging.INFO

    # Configure stream handler
    handler = logging.StreamHandler()
    handler.setLevel(level_obj)
    handler.setFormatter(logging.Formatter(fmt or "%(levelname)s | %(name)s | %(message)s"))

    # Attach to package root logger
    logger.setLevel(level_obj)
    logger.addHandler(handler)
    logger.propagate = propagate
