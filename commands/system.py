"""Time, date and day answers.

Pure functions taking an optional ``datetime``, which makes them trivial to
test and keeps the clock out of the rest of the code base.
"""

from __future__ import annotations

from datetime import datetime

from config import USER_TITLE

__all__ = ["date_answer", "day_answer", "system_command", "time_answer"]


def time_answer(now: datetime | None = None) -> str:
    """Return the current time as a spoken sentence."""

    moment = now or datetime.now()
    clock = moment.strftime("%I:%M %p").lstrip("0")

    return f"It is {clock}, {USER_TITLE}."


def date_answer(now: datetime | None = None) -> str:
    """Return today's date as a spoken sentence."""

    moment = now or datetime.now()

    return f"Today is {moment.strftime('%d %B %Y')}."


def day_answer(now: datetime | None = None) -> str:
    """Return the current weekday as a spoken sentence."""

    moment = now or datetime.now()

    return f"Today is {moment.strftime('%A')}."


def system_command(text: str) -> str | None:
    """Answer a time/date question.

    Args:
        text: What the user said.

    Returns:
        The answer, or ``None`` when the text is not a time/date question.
    """

    command = (text or "").lower().strip()

    if "what day" in command:
        return day_answer()

    if "what time" in command or command == "time":
        return time_answer()

    if "date" in command:
        return date_answer()

    return None
