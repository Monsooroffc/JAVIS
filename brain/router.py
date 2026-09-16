"""Rule based intent routing for JARVIS.

Turns free text (usually produced by speech recognition) into a :class:`Route`
describing what JARVIS should do next. Routing is deterministic and completely
offline; anything that is not recognised falls back to :attr:`Intent.AI` so the
local language model can answer instead.

Example:
    >>> from brain.router import Intent, route_command
    >>> route_command("open notepad").intent is Intent.OPEN_APP
    True
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

__all__ = ["Intent", "Route", "normalize", "route_command"]


class Intent(StrEnum):
    """Every action JARVIS knows how to perform."""

    EXIT = "exit"
    MEMORY = "memory"
    REMEMBER = "remember"
    SYSTEM = "system"
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    OPEN_WEBSITE = "open_website"
    GOOGLE_SEARCH = "google_search"
    YOUTUBE_SEARCH = "youtube_search"
    OPEN_JARVIS_FOLDER = "open_jarvis_folder"
    BROWSER_SCROLL = "browser_scroll"
    BROWSER_READ = "browser_read"
    BROWSER_TYPE = "browser_type"
    BROWSER_PRESS = "browser_press"
    BROWSER_CLICK = "browser_click"
    BROWSER_FIND = "browser_find"
    AI = "ai"


@dataclass(frozen=True, slots=True)
class Route:
    """A matched intent together with the text pulled out of the sentence."""

    intent: Intent
    command: str
    query: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        """Return the route as a plain dictionary (handy for logs and JSON)."""

        return {
            "type": str(self.intent),
            "command": self.command,
            "query": self.query,
        }


# Words people add to a sentence without changing the meaning of a command.
FILLER_WORDS: tuple[str, ...] = (
    "please",
    "could you",
    "can you",
    "would you",
    "will you",
    "i want you to",
    "i need you to",
    "hey jarvis",
    "jarvis",
    "bro",
)

_FILLER_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(word) for word in FILLER_WORDS) + r")\b"
)
_WHITESPACE_PATTERN = re.compile(r"\s+")

APP_ALIASES: tuple[str, ...] = (
    "notepad",
    "calculator",
    "calc",
    "paint",
    "google chrome",
    "chrome",
)

EXIT_COMMANDS: frozenset[str] = frozenset(
    {"exit", "quit", "goodbye", "shutdown jarvis"}
)

MEMORY_QUESTIONS: tuple[str, ...] = (
    "what do you remember",
    "show my memory",
    "what do you know about me",
)

SCROLL_COMMANDS: frozenset[str] = frozenset(
    {"scroll", "scroll down", "scroll up", "scroll the page"}
)

READ_COMMANDS: frozenset[str] = frozenset(
    {
        "read page",
        "read this page",
        "read the page",
        "read website",
        "read this website",
        "what is on this page",
        "what's on this page",
    }
)

WEBSITE_PREFIXES: tuple[str, ...] = (
    "open website ",
    "go to website ",
    "visit website ",
    "launch website ",
    "open ",
    "go to ",
    "visit ",
    "launch ",
)

SEARCH_PREFIXES: tuple[str, ...] = (
    "search for ",
    "search ",
    "google ",
    "look up ",
)

SYSTEM_COMMANDS: frozenset[str] = frozenset(
    {
        "time",
        "what time is it",
        "what is the time",
        "date",
        "what date is it",
        "what is today's date",
        "what day is it",
    }
)

# "jarvis" is a filler word, so "open jarvis folder" normalises to
# "open folder" - both spellings must be accepted here.
FOLDER_COMMANDS: frozenset[str] = frozenset(
    {
        "open folder",
        "open the folder",
        "open jarvis folder",
        "open the jarvis folder",
        "open project folder",
    }
)


def normalize(text: str) -> str:
    """Lower-case ``text``, drop filler words and collapse the whitespace."""

    if not text:
        return ""

    cleaned = text.strip().lower().replace("\u2019", "'")
    cleaned = _FILLER_PATTERN.sub(" ", cleaned)

    return _WHITESPACE_PATTERN.sub(" ", cleaned).strip()


def route_command(text: str) -> Route:
    """Match ``text`` against every known command and return the best route."""

    command = normalize(text)

    if command in EXIT_COMMANDS:
        return Route(Intent.EXIT, command)

    if any(question in command for question in MEMORY_QUESTIONS):
        return Route(Intent.MEMORY, command)

    if command == "remember" or command.startswith("remember "):
        return Route(Intent.REMEMBER, command, command[len("remember") :].strip())

    for app in APP_ALIASES:
        if command in (app, f"open {app}", f"start {app}", f"launch {app}"):
            return Route(Intent.OPEN_APP, command, app)

    if command in SCROLL_COMMANDS:
        return Route(Intent.BROWSER_SCROLL, command)

    if command in READ_COMMANDS:
        return Route(Intent.BROWSER_READ, command)

    for intent, prefix in (
        (Intent.BROWSER_TYPE, "type "),
        (Intent.BROWSER_PRESS, "press "),
        (Intent.BROWSER_CLICK, "click "),
        (Intent.BROWSER_FIND, "find "),
    ):
        if command.startswith(prefix):
            return Route(intent, command, command[len(prefix) :].strip())

    # Checked before the generic "open ..." website rule so that the folder
    # command is not swallowed by it.
    if command in FOLDER_COMMANDS:
        return Route(Intent.OPEN_JARVIS_FOLDER, command)

    for prefix in WEBSITE_PREFIXES:
        if command.startswith(prefix):
            site = command[len(prefix) :].strip()

            if site.endswith(" website"):
                site = site[: -len(" website")].strip()

            if site:
                return Route(Intent.OPEN_WEBSITE, command, site)

    for prefix in SEARCH_PREFIXES:
        if command.startswith(prefix):
            query = command[len(prefix) :].strip()

            if query:
                return Route(Intent.GOOGLE_SEARCH, command, query)

    if command.startswith("play "):
        query = command[5:].strip()

        if query:
            return Route(Intent.YOUTUBE_SEARCH, command, query)

    if command.startswith("close "):
        return Route(Intent.CLOSE_APP, command, command[6:].strip())

    if command in SYSTEM_COMMANDS:
        return Route(Intent.SYSTEM, command)

    return Route(Intent.AI, command, command)
