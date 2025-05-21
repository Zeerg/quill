import logging
import os
from typing import Optional


def get_logger(name: str, debug: Optional[bool] = None) -> logging.Logger:
    """
    Returns a logger configured once per process.
    - debug: if True, forces DEBUG level; if False, INFO;
             if None, read from DEBUG env var.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    # decide level
    if debug is None:
        debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")
    level = logging.DEBUG if debug else logging.INFO

    # set up handler + formatter
    handler = logging.StreamHandler()
    handler.setLevel(level)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
