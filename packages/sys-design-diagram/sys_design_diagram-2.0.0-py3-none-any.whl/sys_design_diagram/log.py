"""Copyright (c) 2024, Aydin Abdi.

This module contains the logging configuration for the application.
"""

import sys

from pathlib import Path
from typing import Any

from loguru import logger


__all__ = ["logger"]

LOGGING_FOLDER_NAME = "logs"
# Logging path shall be current directory/logs
LOGGING_PATH = Path.cwd() / LOGGING_FOLDER_NAME
LOGGING_PATH.mkdir(exist_ok=True)

LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message} | {extra[path]} | {extra[function]} | {extra[line]}"

# Three handlers are created for the logger. One info, one debug and terminal.
LOGGING_CONFIG = {
    "handlers": [
        {
            "sink": LOGGING_PATH / "debug.log",
            "level": "DEBUG",
            "format": LOG_FORMAT,
            "backtrace": True,
            "rotation": "1 week",
            "serialize": True,
        },
        {"sink": sys.stdout, "level": "INFO", "format": LOG_FORMAT, "backtrace": True, "serialize": True},
    ],
    "extra": {"path": "{file.path}", "function": "{function}", "line": "{line}"},
}


logger.configure(**LOGGING_CONFIG)


def configure_logging(**kwargs: Any) -> None:
    """Configure logging settings based on verbosity."""
    verbose = kwargs.get("verbose", False)

    if verbose:
        for handler in logger._core.handlers.values():
            handler._levelno = 10
    else:
        for handler in logger._core.handlers.values():
            handler._levelno = 20
