# src/normet/utils/logging.py
from __future__ import annotations

import logging
import os
import sys
from typing import Literal, Union, Optional

_LOGGER_NAME = "normet"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a namespaced logger for the ``normet`` package.

    The logger is guaranteed to have a ``NullHandler`` attached so
    that importing ``normet`` never configures or interferes with
    global logging state.

    Parameters
    ----------
    name : str or None, optional
        Child logger name (e.g., "analysis.decomposition").
        If None, returns the package root logger "normet".

    Returns
    -------
    logging.Logger
        Logger instance scoped to the package or submodule.
    """
    logger_name = f"{_LOGGER_NAME}.{name}" if name else _LOGGER_NAME
    logger = logging.getLogger(logger_name)
    if not any(isinstance(h, logging.NullHandler) for h in logger.handlers):
        logger.addHandler(logging.NullHandler())
    return logger


def enable_default_logging(
    level: Union[int, Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"], None] = None,
    fmt: Optional[str] = None,
    propagate: bool = False,
    *,
    prefer_rich: bool = True,
) -> None:
    """
    Attach a default handler to the root "normet" logger.

    Behavior
    --------
    - If ``prefer_rich`` and Rich is installed → use RichHandler.
    - Otherwise → use plain StreamHandler.

    Parameters
    ----------
    level : int | str | None
        Logging level (e.g., "INFO"). If None, falls back to env
        ``NORMET_LOGLEVEL`` or INFO by default.
    fmt : str, optional
        Format string for non-Rich handlers. Defaults to
        ``"%(levelname)s | %(name)s | %(message)s"``.
    propagate : bool, default False
        Whether to propagate logs to the global root logger.
    prefer_rich : bool, default True
        Try to use RichHandler if available.

    Notes
    -----
    - This function is intended for interactive use in notebooks
      and scripts. Larger applications should configure logging
      explicitly.
    - Calling this function multiple times will not attach duplicate
      stream handlers.
    """
    logger = get_logger()

    # Avoid stacking multiple handlers
    if any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        return

    # Resolve log level
    env_level = os.getenv("NORMET_LOGLEVEL", "").upper()
    if isinstance(level, str):
        lvl = getattr(logging, level.upper(), logging.INFO)
    elif isinstance(level, int):
        lvl = level
    elif env_level:
        lvl = getattr(logging, env_level, logging.INFO)
    else:
        lvl = logging.INFO

    # Choose handler
    if prefer_rich:
        try:
            from rich.logging import RichHandler  # type: ignore
            handler = RichHandler(rich_tracebacks=True, markup=True)
        except Exception:
            handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setLevel(lvl)

    # Apply formatter for plain handler
    if 'rich' not in handler.__class__.__module__:
        handler.setFormatter(logging.Formatter(fmt or "%(levelname)s | %(name)s | %(message)s"))

    logger.setLevel(lvl)
    logger.addHandler(handler)
    logger.propagate = propagate
