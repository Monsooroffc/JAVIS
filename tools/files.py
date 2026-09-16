"""Filesystem helpers: show the JARVIS folder in Windows Explorer.

The folder is taken from :data:`config.BASE_DIR`, so a cloned copy of the
project always opens the right directory (the old version hardcoded
``C:\\Users\\acer\\JARVIS``).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from config import BASE_DIR, USER_TITLE
from core.logger import get_logger

__all__ = ["JARVIS_FOLDER", "open_folder", "open_jarvis_folder"]

log = get_logger(__name__)

JARVIS_FOLDER: Path = Path(BASE_DIR)


def open_folder(path: str | Path | None = None) -> str | None:
    """Open ``path`` (the project folder by default) in Explorer.

    Returns:
        A sentence JARVIS can speak, or ``None`` when opening failed.
    """

    target = Path(path) if path is not None else JARVIS_FOLDER

    if not target.exists():
        log.error("Folder not found: %s", target)
        return f"I couldn't find the folder {target}."

    try:
        subprocess.Popen(["explorer.exe", str(target)])

    except OSError as error:
        log.error("Could not open %s: %s", target, error)
        return f"I couldn't open that folder, {USER_TITLE}."

    log.info("Opened folder %s", target)

    return f"Opening the JARVIS folder, {USER_TITLE}."


def open_jarvis_folder() -> str | None:
    """Open the JARVIS project folder in Explorer."""

    return open_folder()