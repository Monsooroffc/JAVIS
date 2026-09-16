"""Opening desktop applications on Windows.

Applications are described as data (:class:`App`) instead of nested ``if``
statements, so adding a new program is a one line change.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from config import USER_TITLE
from core.logger import get_logger

__all__ = ["App", "AppRegistry", "DEFAULT_APPS", "open_app", "registry"]

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class App:
    """An application JARVIS can launch."""

    name: str
    aliases: tuple[str, ...]
    command: str
    candidates: tuple[str, ...] = ()

    def executable(self) -> str | None:
        """Return the path of the executable, or ``None`` when not installed."""

        found = shutil.which(self.command)

        if found:
            return found

        for candidate in self.candidates:
            path = Path(os.path.expandvars(candidate))

            if path.is_file():
                return str(path)

        return None


DEFAULT_APPS: tuple[App, ...] = (
    App("Notepad", ("notepad",), "notepad.exe"),
    App("Calculator", ("calculator", "calc"), "calc.exe"),
    App("Paint", ("paint", "mspaint"), "mspaint.exe"),
    App(
        "Google Chrome",
        ("chrome", "google chrome"),
        "chrome.exe",
        (
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
        ),
    ),
)


class AppRegistry:
    """Finds and launches known applications."""

    def __init__(self, apps: tuple[App, ...] = DEFAULT_APPS) -> None:
        self.apps = apps
        self._by_alias = {
            alias: app for app in apps for alias in app.aliases
        }

    def find(self, name: str) -> App | None:
        """Return the application matching ``name`` (or an alias)."""

        return self._by_alias.get((name or "").strip().lower())

    def open(self, name: str) -> str | None:
        """Launch an application.

        Returns:
            A sentence JARVIS can speak, or ``None`` when the name is unknown.
        """

        app = self.find(name)

        if app is None:
            log.warning("Unknown application: %s", name)
            return None

        executable = app.executable()

        if executable is None:
            log.error("%s is not installed.", app.name)
            return f"I couldn't find {app.name}, {USER_TITLE}."

        try:
            subprocess.Popen([executable], close_fds=True)

        except OSError as error:
            log.error("Could not start %s: %s", app.name, error)
            return f"I couldn't open {app.name}, {USER_TITLE}."

        log.info("Opened %s", app.name)

        return f"Opening {app.name}, {USER_TITLE}."


registry = AppRegistry()


def open_app(name: str) -> str | None:
    """Open an application by name using the default registry."""

    return registry.open(name)