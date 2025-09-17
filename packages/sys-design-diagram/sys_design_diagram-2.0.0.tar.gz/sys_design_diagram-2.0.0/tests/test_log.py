"""Copyright (c) 2024, Aydin Abdi.

This module contains tests for the logging configuration in the sys_design_diagram.log module.
"""

import pytest
import sys
import json
from pathlib import Path
import shutil
from sys_design_diagram import log


@pytest.fixture(scope="function")
def log_dir(tmp_path):
    """Create a temporary directory to store log files."""
    log_path = tmp_path / "logs"
    log_path.mkdir()
    yield log_path
    # Clean up the log directory after the test
    shutil.rmtree(log_path)


@pytest.fixture(scope="function", autouse=True)
def setup_logging(log_dir):
    """Configure the logging system before running the tests."""
    LOG_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message} | {extra[path]} | {extra[function]} | {extra[line]}"
    )
    LOGGING_CONFIG = {
        "handlers": [
            {
                "sink": log_dir / "debug.log",
                "level": "DEBUG",
                "format": LOG_FORMAT,
                "backtrace": True,
                "rotation": "1 week",
                "serialize": True,
            },
            {
                "sink": sys.stdout,
                "level": "INFO",
                "format": LOG_FORMAT,
                "backtrace": True,
                "colorize": True,
                "serialize": True,
            },
        ],
        "extra": {"path": "{module}", "function": "{function}", "line": "{line}"},
    }
    log.logger.configure(**LOGGING_CONFIG)
    yield


def test_logging_level_info(caplog):
    """Test that the logging level is set to INFO when verbose=False."""
    log.configure_logging(verbose=False)

    log.logger.debug("This is a debug message")
    log.logger.info("This is an info message")

    # Only the info message should be printed to stdout
    assert "This is a debug message" not in caplog.text
    assert "This is an info message" in caplog.text


def test_logging_level_debug(caplog):
    """Test that the logging level is set to DEBUG when verbose=True."""
    log.configure_logging(verbose=True)

    log.logger.debug("This is a debug message")
    log.logger.info("This is an info message")

    # Both the debug and info messages should be printed to stdout
    assert "This is a debug message" in caplog.text
    assert "This is an info message" in caplog.text
