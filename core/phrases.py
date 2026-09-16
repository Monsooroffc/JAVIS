"""Short spoken phrases that are rotated so JARVIS does not repeat itself.

Used for the brief "thinking" line JARVIS says before an action that takes a
moment (a language model request, opening a page, a search, reading a page).

Example:
    >>> from core.phrases import PhraseSpinner
    >>> spinner = PhraseSpinner(["One moment, {title}."], title="bro")
    >>> spinner.next()
    'One moment, bro.'
"""

from __future__ import annotations

import threading
from collections.abc import Iterable

__all__ = ["PhraseSpinner"]


class PhraseSpinner:
    """Hands out phrases one after another and starts over when it runs out."""

    def __init__(self, phrases: Iterable[str], title: str = "") -> None:
        self._phrases: list[str] = [
            phrase.strip()
            for phrase in phrases or ()
            if phrase and phrase.strip()
        ]
        self.title = title
        self._index = 0
        self._lock = threading.Lock()

    def __len__(self) -> int:
        return len(self._phrases)

    @property
    def phrases(self) -> tuple[str, ...]:
        """The configured phrases, in order, before ``{title}`` substitution."""

        return tuple(self._phrases)

    @property
    def rendered(self) -> tuple[str, ...]:
        """The configured phrases with ``{title}`` already substituted."""

        return tuple(self._render(phrase) for phrase in self._phrases)

    def next(self) -> str:
        """Return the next phrase.

        Returns:
            The phrase with ``{title}`` filled in, or an empty string when no
            phrases are configured.
        """

        if not self._phrases:
            return ""

        with self._lock:
            phrase = self._phrases[self._index % len(self._phrases)]
            self._index += 1

        return self._render(phrase)

    def _render(self, phrase: str) -> str:
        """Fill ``{title}`` in ``phrase``, leaving broken placeholders alone."""

        try:
            return phrase.format(title=self.title)

        except (KeyError, IndexError, ValueError):
            return phrase

    def reset(self) -> None:
        """Start again from the first phrase."""

        with self._lock:
            self._index = 0