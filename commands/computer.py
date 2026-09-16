"""Direct computer commands: apps, websites and closing programs.

These handlers cover sentences that only need ``webbrowser`` or ``taskkill``
(for example *"close chrome"*), and they complement the agent/tool layer used
for the richer browser automation.
"""

from __future__ import annotations

import subprocess
import urllib.parse
import webbrowser

from config import USER_TITLE
from core.logger import get_logger
from tools.apps import registry
from tools.files import open_jarvis_folder

__all__ = ["PROCESSES", "WEBSITES", "execute_command"]

log = get_logger(__name__)

WEBSITES: dict[str, tuple[str, str]] = {
    "youtube": ("YouTube", "https://www.youtube.com"),
    "google": ("Google", "https://www.google.com"),
    "github": ("GitHub", "https://github.com"),
    "chatgpt": ("ChatGPT", "https://chatgpt.com"),
}

FOLDER_PHRASES: tuple[str, ...] = (
    "open folder",
    "open the folder",
    "open jarvis folder",
    "open the jarvis folder",
    "open project folder",
)

PROCESSES: dict[str, str] = {
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "paint": "mspaint.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
}


def execute_command(text: str) -> str | None:
    """Run a direct computer command.

    Args:
        text: What the user said.

    Returns:
        A sentence JARVIS can speak, or ``None`` when nothing matched.
    """

    command = (text or "").lower().strip()

    if not command:
        return None

    for handler in (
        _folder,
        _close,
        _open_app,
        _open_website,
        _search,
        _play,
    ):
        answer = handler(command)

        if answer:
            return answer

    return None


def _folder(command: str) -> str | None:
    """Open the JARVIS folder."""

    if any(phrase in command for phrase in FOLDER_PHRASES):
        return open_jarvis_folder()

    return None


def _close(command: str) -> str | None:
    """Close a known application."""

    if not command.startswith("close "):
        return None

    target = command[len("close ") :].strip().removeprefix("the ").strip()

    # Longest name first, so "google chrome" wins over "chrome".
    for name in sorted(PROCESSES, key=len, reverse=True):
        if name not in target:
            continue

        image = PROCESSES[name]

        try:
            subprocess.run(
                ["taskkill", "/IM", image, "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

        except OSError as error:
            log.error("Could not close %s: %s", name, error)
            return f"I couldn't close {name}, {USER_TITLE}."

        log.info("Closed %s (%s)", name, image)

        return f"Closing {name.title()}, {USER_TITLE}."

    return None


def _open_app(command: str) -> str | None:
    """Open a desktop application by name."""

    for prefix in ("open ", "start ", "launch "):
        if command.startswith(prefix):
            return registry.open(command[len(prefix) :].strip())

    return None


def _open_website(command: str) -> str | None:
    """Open one of the well known websites, or an explicit domain."""

    for name, (label, url) in WEBSITES.items():
        if command in (name, f"open {name}", f"go to {name}"):
            webbrowser.open(url)
            log.info("Opened %s", url)

            return f"Opening {label}, {USER_TITLE}."

    if command.startswith("open website "):
        site = command[len("open website ") :].strip()

        if site:
            url = site if site.startswith("http") else f"https://{site}"
            webbrowser.open(url)
            log.info("Opened %s", url)

            return f"Opening {site}, {USER_TITLE}."

    return None


def _search(command: str) -> str | None:
    """Search Google."""

    for prefix in ("search for ", "search ", "google "):
        if not command.startswith(prefix):
            continue

        query = command[len(prefix) :].strip()

        if not query:
            continue

        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)

        return f"Searching Google for {query}, {USER_TITLE}."

    return None


def _play(command: str) -> str | None:
    """Search YouTube."""

    if not command.startswith("play "):
        return None

    query = command[len("play ") :].strip()

    if not query:
        return None

    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(
        query
    )
    webbrowser.open(url)

    return f"Searching YouTube for {query}, {USER_TITLE}."