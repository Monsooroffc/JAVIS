"""Spoken output: text to speech through ``pyttsx3``.

One engine instance is reused for the whole session (creating a new one for
every sentence leaks COM objects on Windows) and calls are serialised with a
lock because ``runAndWait`` is not re-entrant.
"""

from __future__ import annotations

import threading

from config import SPEECH_RATE, SPEECH_VOLUME
from core.logger import get_logger

__all__ = ["Speaker", "speak", "speaker"]

log = get_logger(__name__)


class Speaker:
    """Speaks text out loud, quietly ignoring audio problems."""

    def __init__(
        self,
        rate: int = SPEECH_RATE,
        volume: float = SPEECH_VOLUME,
        enabled: bool = True,
    ) -> None:
        self.rate = rate
        self.volume = volume
        self.enabled = enabled
        self._engine: object | None = None
        self._lock = threading.Lock()

    @property
    def engine(self) -> object:
        """The lazily created ``pyttsx3`` engine."""

        if self._engine is None:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            self._engine = engine

        return self._engine

    def say(self, text: str) -> None:
        """Speak ``text`` out loud.

        Args:
            text: The sentence to read. Empty values are ignored.
        """

        sentence = str(text or "").strip()

        if not sentence:
            return

        if not self.enabled:
            log.debug("Speech disabled, skipping: %s", sentence)
            return

        log.debug("Speaking: %s", sentence)

        with self._lock:
            try:
                engine = self.engine
                engine.say(sentence)  # type: ignore[attr-defined]
                engine.runAndWait()  # type: ignore[attr-defined]

            except Exception as error:  # noqa: BLE001 - audio drivers vary a lot
                log.error("Speech error: %s", error)

    def stop(self) -> None:
        """Stop the engine and release it."""

        with self._lock:
            engine = self._engine

            if engine is None:
                return

            try:
                engine.stop()  # type: ignore[attr-defined]

            except Exception as error:  # noqa: BLE001 - best effort shutdown
                log.debug("Speech engine shutdown problem: %s", error)

            self._engine = None


speaker = Speaker()


def speak(text: str) -> None:
    """Speak ``text`` with the shared speaker."""

    speaker.say(text)