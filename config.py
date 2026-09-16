"""Central configuration for JARVIS.

Every setting can be overridden with an environment variable, so the assistant
can be re-configured without editing code::

    set JARVIS_MODEL=llama3.2:3b
    set JARVIS_WAKE_WORD=computer
    set JARVIS_LOG_LEVEL=DEBUG
"""

from __future__ import annotations

import os
from pathlib import Path

# =========================
# PATHS
# =========================

BASE_DIR: Path = Path(__file__).resolve().parent
PROJECT_ROOT: Path = BASE_DIR
LOG_DIR: Path = BASE_DIR / "logs"
DATA_DIR: Path = BASE_DIR / "data"


def _env_str(name: str, default: str) -> str:
    """Return an environment variable as text, or ``default`` when unset."""

    value = os.getenv(name, "").strip()

    return value or default


def _env_int(name: str, default: int) -> int:
    """Return an environment variable as an integer, or ``default``."""

    raw = os.getenv(name, "").strip()

    if not raw:
        return default

    try:
        return int(raw)

    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    """Return an environment variable as a float, or ``default``."""

    raw = os.getenv(name, "").strip()

    if not raw:
        return default

    try:
        return float(raw)

    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    """Return an environment flag, or ``default`` when it is not set."""

    raw = os.getenv(name, "").strip().lower()

    if not raw:
        return default

    return raw in {"1", "true", "yes", "on"}


# =========================
# IDENTITY
# =========================

ASSISTANT_NAME: str = _env_str("JARVIS_NAME", "JARVIS")
VERSION: str = "7.1.0"
WAKE_WORD: str = _env_str("JARVIS_WAKE_WORD", "jarvis")
USER_TITLE: str = _env_str("JARVIS_USER_TITLE", "bro")

# =========================
# AI BRAIN (local Ollama model)
# =========================

MODEL: str = _env_str("JARVIS_MODEL", "qwen2.5:1.5b")
OLLAMA_HOST: str = _env_str("OLLAMA_HOST", "http://127.0.0.1:11434")
MAX_HISTORY: int = _env_int("JARVIS_MAX_HISTORY", 10)

SYSTEM_PROMPT: str = (
    f"You are {ASSISTANT_NAME}, a helpful personal AI assistant running "
    "locally on the user's computer. Keep answers short and natural because "
    "they are read aloud with text to speech. "
    f"Call the user {USER_TITLE} when appropriate."
)

# =========================
# VOICE
# =========================

LISTEN_TIMEOUT: int = _env_int("JARVIS_LISTEN_TIMEOUT", 5)
PHRASE_TIME_LIMIT: int = _env_int("JARVIS_PHRASE_TIME_LIMIT", 8)
AMBIENT_CALIBRATION_SECONDS: int = _env_int("JARVIS_CALIBRATION_SECONDS", 1)
SPEECH_LANGUAGE: str = _env_str("JARVIS_LANGUAGE", "en-US")
SPEECH_RATE: int = _env_int("JARVIS_SPEECH_RATE", 175)
SPEECH_VOLUME: float = _env_float("JARVIS_SPEECH_VOLUME", 1.0)

# =========================
# MEMORY
# =========================

MEMORY_FILE: Path = Path(
    _env_str("JARVIS_MEMORY_FILE", str(BASE_DIR / "memory.json"))
)

# =========================
# BROWSER TOOLS
# =========================

BROWSER_CHANNEL: str = _env_str("JARVIS_BROWSER_CHANNEL", "chrome")
BROWSER_HEADLESS: bool = _env_bool("JARVIS_BROWSER_HEADLESS", False)
BROWSER_TIMEOUT_MS: int = _env_int("JARVIS_BROWSER_TIMEOUT_MS", 15000)

# =========================
# LOGGING
# =========================

LOG_LEVEL: str = _env_str("JARVIS_LOG_LEVEL", "INFO")
LOG_TO_FILE: bool = _env_bool("JARVIS_LOG_TO_FILE", False)

# =========================
# SPOKEN FEEDBACK WHILE THINKING
# =========================

# When true JARVIS says a short line before an action that takes a moment,
# so it never goes silent after you stop talking. Disable with
# ``set JARVIS_THINKING=false``.
THINKING_ENABLED: bool = _env_bool("JARVIS_THINKING", True)

# Pipe separated list; ``{title}`` is replaced with JARVIS_USER_TITLE.
THINKING_PHRASES: tuple[str, ...] = tuple(
    phrase.strip()
    for phrase in _env_str(
        "JARVIS_THINKING_PHRASES",
        "One moment, {title}."
        "|Let me think, {title}."
        "|Checking that, {title}."
        "|On it, {title}.",
    ).split("|")
    if phrase.strip()
)

# Only these intents are preceded by a filler line: they are the ones that
# really make the user wait. Instant answers (time, date, apps) stay instant.
THINKING_INTENTS: frozenset[str] = frozenset(
    {
        "ai",
        "open_website",
        "google_search",
        "youtube_search",
        "browser_read",
    }
)

# =========================
# CONVERSATION
# =========================

SLEEP_PHRASES: tuple[str, ...] = (
    "goodbye",
    "go to sleep",
    "sleep",
    "stop listening",
    "that's all",
    "thats all",
    "exit conversation",
    "stop conversation",
)