"""Reliable Windows text-to-speech for JARVIS V7.2."""

from __future__ import annotations

import threading

from config import SPEECH_RATE, SPEECH_VOLUME
from core.logger import get_logger

__all__ = ["Speaker", "speak", "speaker"]

log = get_logger(__name__)


class Speaker:
    """Reliable Windows SAPI5 speaker."""

    def __init__(
        self,
        rate: int = SPEECH_RATE,
        volume: float = SPEECH_VOLUME,
        enabled: bool = True,
    ) -> None:
        self.rate = rate
        self.volume = volume
        self.enabled = enabled
        self._lock = threading.RLock()

    def _speak_once(self, text: str) -> None:
        """Create a fresh SAPI5 engine for every speech request."""

        import pyttsx3

        engine = None

        try:
            engine = pyttsx3.init("sapi5")

            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            # Prefer an English Windows voice.
            try:
                voices = engine.getProperty("voices")

                for voice in voices:
                    name = str(getattr(voice, "name", "")).lower()
                    languages = str(
                        getattr(voice, "languages", "")
                    ).lower()

                    if (
                        "english" in name
                        or "en_" in languages
                        or "en-" in languages
                    ):
                        engine.setProperty("voice", voice.id)
                        break

            except Exception as error:
                log.debug("Voice selection skipped: %s", error)

            log.info("JARVIS SPEAKING: %s", text)

            engine.say(text)
            engine.runAndWait()

        finally:
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass

    def say(self, text: str) -> None:
        """Speak text using a fresh SAPI5 engine."""

        sentence = str(text or "").strip()

        if not sentence or not self.enabled:
            return

        with self._lock:
            try:
                self._speak_once(sentence)

            except Exception as error:
                log.error("TTS error: %s", error)

                # One clean retry.
                try:
                    self._speak_once(sentence)

                except Exception as retry_error:
                    log.error(
                        "TTS recovery failed: %s",
                        retry_error,
                    )

    def stop(self) -> None:
        """Compatibility method."""

        # Each speech request owns its own engine,
        # so there is no persistent engine to release.
        return


speaker = Speaker()


def speak(text: str) -> None:
    """Speak using the shared JARVIS speaker."""

    speaker.say(text)