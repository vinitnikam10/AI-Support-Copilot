"""
Shared logging setup.

Cloud Run picks up anything written to stdout/stderr and routes it to
Cloud Logging, so a plain stream handler is enough. Format is kept simple
and readable rather than JSON — easier to scan locally and still parseable.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured by a previous import.
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(handler)
    logger.propagate = False
    return logger
