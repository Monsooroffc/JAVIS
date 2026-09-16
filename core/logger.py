"""Logging helpers shared by every JARVIS module.

Console output stays clean (``LEVEL: message``) while the optional rotating
file handler keeps the detailed timestamped log used for debugging.

Example::

    from core.logger import get_logger

    log = get_logger(__name__)
    log.info("JARVIS is online")
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import LOG_DIR, LOG_LEVEL, LOG_TO_FILE

LOGGER_NAME = "jarvis"

_CONSOLE_FORMAT = "%(levelname)s: %(message)s"
_FILE_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

_configured = False


def configure_logging(
    level: str | int | None = None,
    log_to_file: bool | None = None,
) -> logging.Logger:
    """Configure the root JARVIS logger once and return it.

    Args:
        level: Logging level name or number. Defaults to ``config.LOG_LEVEL``.
        log_to_file: Write to ``logs/jarvis.log`` as well as the console.
            Defaults to ``config.LOG_TO_FILE``.
    """

    global _configured

    logger = logging.getLogger(LOGGER_NAME)

    if level is None:
        level = LOG_LEVEL

    if log_to_file is None:
        log_to_file = LOG_TO_FILE

    if isinstance(level, str):
        level = logging.getLevelName(level.upper())

        if not isinstance(level, int):
            level = logging.INFO

    logger.setLevel(level)

    if _configured:
        return logger

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(_CONSOLE_FORMAT))
    logger.addHandler(console)

    if log_to_file:
        _attach_file_handler(logger, level)

    logger.propagate = False
    _configured = True

    return logger


def _attach_file_handler(logger: logging.Logger, level: int) -> None:
    """Add a rotating file handler, ignoring filesystem problems."""

    try:
        log_dir: Path = Path(LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            log_dir / "jarvis.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )

        handler.setFormatter(logging.Formatter(_FILE_FORMAT))
        handler.setLevel(level)

        logger.addHandler(handler)

    except OSError:  # pragma: no cover - depends on the host filesystem
        logger.debug("File logging is unavailable on this system.")


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a configured child logger for ``name``."""

    configure_logging()

    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")

    return logging.getLogger(LOGGER_NAME)
