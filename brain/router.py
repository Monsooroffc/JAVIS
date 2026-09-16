"""
Rule-based intent routing for JARVIS V7.2.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

__all__ = [
    "Intent",
    "Route",
    "normalize",
    "route_command",
]


class Intent(StrEnum):
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

    BROWSER_BACK = "browser_back"
    BROWSER_FORWARD = "browser_forward"
    BROWSER_REFRESH = "browser_refresh"

    AI = "ai"


@dataclass(frozen=True, slots=True)
class Route:
    intent: Intent
    command: str
    query: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "type": str(self.intent),
            "command": self.command,
            "query": self.query,
        }


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


def normalize(text: str) -> str:
    """Normalize spoken input."""

    if not text:
        return ""

    cleaned = text.strip().lower().replace("\u2019", "'")
    cleaned = _FILLER_PATTERN.sub(" ", cleaned)

    return _WHITESPACE_PATTERN.sub(" ", cleaned).strip()


# ============================================================
# APPLICATIONS
# ============================================================

APP_ALIASES: tuple[str, ...] = (
    "notepad",
    "calculator",
    "calc",
    "paint",
    "google chrome",
    "chrome",
)


# ============================================================
# BASIC COMMANDS
# ============================================================

EXIT_COMMANDS: frozenset[str] = frozenset(
    {
        "exit",
        "quit",
        "goodbye",
        "shutdown",
    }
)

MEMORY_QUESTIONS: tuple[str, ...] = (
    "what do you remember",
    "show my memory",
    "what do you know about me",
)


# ============================================================
# BROWSER COMMANDS
# ============================================================

SCROLL_COMMANDS: frozenset[str] = frozenset(
    {
        "scroll",
        "scroll down",
        "scroll up",
        "scroll the page",
        "scroll down the page",
        "scroll up the page",
    }
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
        "read this",
    }
)

BACK_COMMANDS: frozenset[str] = frozenset(
    {
        "back",
        "go back",
        "browser back",
        "previous page",
        "go to previous page",
    }
)

FORWARD_COMMANDS: frozenset[str] = frozenset(
    {
        "forward",
        "go forward",
        "browser forward",
        "next page",
        "go to next page",
    }
)

REFRESH_COMMANDS: frozenset[str] = frozenset(
    {
        "refresh",
        "refresh page",
        "reload",
        "reload page",
        "refresh the page",
    }
)


# ============================================================
# WEBSITE COMMANDS
# ============================================================

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


# ============================================================
# SEARCH COMMANDS
# ============================================================

SEARCH_PREFIXES: tuple[str, ...] = (
    "search for ",
    "search ",
    "google ",
    "look up ",
)


# ============================================================
# SYSTEM
# ============================================================

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


# ============================================================
# FILES
# ============================================================

FOLDER_COMMANDS: frozenset[str] = frozenset(
    {
        "open folder",
        "open the folder",
        "open jarvis folder",
        "open the jarvis folder",
        "open project folder",
    }
)


# ============================================================
# ROUTER
# ============================================================

def route_command(text: str) -> Route:
    """Convert a command into a deterministic JARVIS route."""

    command = normalize(text)

    if not command:
        return Route(Intent.AI, command, None)

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if command in EXIT_COMMANDS:
        return Route(Intent.EXIT, command)

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if any(question in command for question in MEMORY_QUESTIONS):
        return Route(Intent.MEMORY, command)

    if command == "remember" or command.startswith("remember "):
        return Route(
            Intent.REMEMBER,
            command,
            command[len("remember"):].strip(),
        )

    # --------------------------------------------------------
    # APPLICATIONS
    # --------------------------------------------------------

    for app in APP_ALIASES:
        if command in (
            app,
            f"open {app}",
            f"start {app}",
            f"launch {app}",
        ):
            return Route(
                Intent.OPEN_APP,
                command,
                app,
            )

    # --------------------------------------------------------
    # BROWSER SCROLL
    # --------------------------------------------------------

    if command in SCROLL_COMMANDS:

        if "up" in command:
            return Route(
                Intent.BROWSER_SCROLL,
                command,
                "up",
            )

        return Route(
            Intent.BROWSER_SCROLL,
            command,
            "down",
        )

    # --------------------------------------------------------
    # READ PAGE
    # --------------------------------------------------------

    if command in READ_COMMANDS:
        return Route(
            Intent.BROWSER_READ,
            command,
        )

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    if command in BACK_COMMANDS:
        return Route(
            Intent.BROWSER_BACK,
            command,
        )

    # --------------------------------------------------------
    # FORWARD
    # --------------------------------------------------------

    if command in FORWARD_COMMANDS:
        return Route(
            Intent.BROWSER_FORWARD,
            command,
        )

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    if command in REFRESH_COMMANDS:
        return Route(
            Intent.BROWSER_REFRESH,
            command,
        )

    # --------------------------------------------------------
    # BROWSER INTERACTION
    # --------------------------------------------------------

    browser_actions = (
        (Intent.BROWSER_TYPE, "type "),
        (Intent.BROWSER_PRESS, "press "),
        (Intent.BROWSER_CLICK, "click "),
        (Intent.BROWSER_FIND, "find "),
    )

    for intent, prefix in browser_actions:

        if command.startswith(prefix):

            query = command[len(prefix):].strip()

            if query:
                return Route(
                    intent,
                    command,
                    query,
                )

    # --------------------------------------------------------
    # JARVIS FOLDER
    # --------------------------------------------------------

    if command in FOLDER_COMMANDS:
        return Route(
            Intent.OPEN_JARVIS_FOLDER,
            command,
        )

    # --------------------------------------------------------
    # WEBSITE
    # IMPORTANT:
    # This was missing in your previous router.
    # --------------------------------------------------------

    for prefix in WEBSITE_PREFIXES:

        if command.startswith(prefix):

            site = command[len(prefix):].strip()

            if site.endswith(" website"):
                site = site[:-len(" website")].strip()

            if site:
                return Route(
                    Intent.OPEN_WEBSITE,
                    command,
                    site,
                )

    # --------------------------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------------------------

    for prefix in SEARCH_PREFIXES:

        if command.startswith(prefix):

            query = command[len(prefix):].strip()

            if query:
                return Route(
                    Intent.GOOGLE_SEARCH,
                    command,
                    query,
                )

    # --------------------------------------------------------
    # YOUTUBE
    # --------------------------------------------------------

    if command.startswith("play "):

        query = command[5:].strip()

        if query:
            return Route(
                Intent.YOUTUBE_SEARCH,
                command,
                query,
            )

    if command.startswith("youtube search "):

        query = command[len("youtube search "):].strip()

        if query:
            return Route(
                Intent.YOUTUBE_SEARCH,
                command,
                query,
            )

    if command.startswith("search youtube for "):

        query = command[len("search youtube for "):].strip()

        if query:
            return Route(
                Intent.YOUTUBE_SEARCH,
                command,
                query,
            )

    # --------------------------------------------------------
    # CLOSE APPLICATION
    # --------------------------------------------------------

    if command.startswith("close "):

        query = command[6:].strip()

        if query:
            return Route(
                Intent.CLOSE_APP,
                command,
                query,
            )

    # --------------------------------------------------------
    # SYSTEM
    # --------------------------------------------------------

    if command in SYSTEM_COMMANDS:
        return Route(
            Intent.SYSTEM,
            command,
        )

    # --------------------------------------------------------
    # AI FALLBACK
    # --------------------------------------------------------

    return Route(
        Intent.AI,
        command,
        command,
    )