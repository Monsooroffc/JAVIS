"""Assistant state machine: is JARVIS running, and is it in a conversation?"""

from __future__ import annotations

from core.logger import get_logger

__all__ = ["JarvisEngine"]

log = get_logger(__name__)


class JarvisEngine:
    """Tracks the lifecycle of the assistant."""

    def __init__(self) -> None:
        self.running: bool = True
        self.conversation_mode: bool = False

    def start_conversation(self) -> None:
        """Switch to continuous conversation mode."""

        self.conversation_mode = True
        log.info("Conversation mode: ON")

    def stop_conversation(self) -> None:
        """Leave continuous conversation mode."""

        self.conversation_mode = False
        log.info("Conversation mode: OFF")

    def should_continue(self) -> bool:
        """True while the assistant is allowed to keep running."""

        return self.running

    def shutdown(self) -> None:
        """Stop the assistant."""

        self.running = False
        self.conversation_mode = False
        log.info("Engine stopped.")
