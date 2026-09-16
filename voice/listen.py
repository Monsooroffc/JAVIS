"""Microphone input: calibration plus speech-to-text.

The microphone and recogniser are created lazily, so importing this module (or
running the unit tests) works on machines without an input device.
"""

from __future__ import annotations

import speech_recognition as sr

from config import (
    AMBIENT_CALIBRATION_SECONDS,
    LISTEN_TIMEOUT,
    PHRASE_TIME_LIMIT,
    SPEECH_LANGUAGE,
)
from core.logger import get_logger

__all__ = ["Listener", "calibrate", "listen", "listener"]

log = get_logger(__name__)


class Listener:
    """Listens to the microphone and returns recognised text."""

    def __init__(
        self,
        language: str = SPEECH_LANGUAGE,
        timeout: int = LISTEN_TIMEOUT,
        phrase_time_limit: int = PHRASE_TIME_LIMIT,
        calibration_seconds: int = AMBIENT_CALIBRATION_SECONDS,
    ) -> None:
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        self.calibration_seconds = calibration_seconds
        self._recognizer: sr.Recognizer | None = None
        self._microphone: sr.Microphone | None = None
        self.calibrated = False

    # =========================
    # LAZY DEVICES
    # =========================

    @property
    def recognizer(self) -> sr.Recognizer:
        """The shared recogniser, created on first use."""

        if self._recognizer is None:
            self._recognizer = sr.Recognizer()

        return self._recognizer

    @property
    def microphone(self) -> sr.Microphone:
        """The default microphone, opened on first use."""

        if self._microphone is None:
            self._microphone = sr.Microphone()

        return self._microphone

    # =========================
    # PUBLIC API
    # =========================

    def calibrate(self) -> bool:
        """Measure the ambient noise level.

        Returns:
            ``True`` when calibration succeeded, ``False`` when the microphone
            is unavailable.
        """

        log.info("Calibrating microphone, please stay quiet...")

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=self.calibration_seconds,
                )

        except Exception as error:  # noqa: BLE001 - sound drivers vary a lot
            log.error("Microphone error: %s", error)
            return False

        self.calibrated = True
        log.info("Microphone ready.")

        return True

    def listen(self) -> str:
        """Listen once and return the recognised text.

        Returns:
            Lower-cased text, or an empty string when nothing usable was heard.
        """

        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit,
                )

        except sr.WaitTimeoutError:
            log.debug("No speech detected.")
            return ""

        except Exception as error:  # noqa: BLE001 - sound drivers vary a lot
            log.error("Microphone error: %s", error)
            return ""

        try:
            text = self.recognizer.recognize_google(audio, language=self.language)

        except sr.UnknownValueError:
            log.debug("Speech was not understood.")
            return ""

        except sr.RequestError as error:
            log.error("Speech recognition service unavailable: %s", error)
            return ""

        log.debug("Heard: %s", text)

        return text.lower().strip()


listener = Listener()


def calibrate() -> bool:
    """Calibrate the shared listener."""

    return listener.calibrate()


def listen() -> str:
    """Listen once with the shared listener."""

    return listener.listen()