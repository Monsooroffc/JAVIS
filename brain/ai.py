"""The local AI brain: a small, well behaved wrapper around Ollama."""

from __future__ import annotations

from dataclasses import dataclass

from config import MAX_HISTORY, MODEL, OLLAMA_HOST, SYSTEM_PROMPT
from core.logger import get_logger

__all__ = ["FALLBACK_ANSWER", "JarvisBrain", "Message", "ask_ai", "brain"]

log = get_logger(__name__)

FALLBACK_ANSWER = (
    "Sorry bro. I couldn't reach my local AI brain. "
    "Please make sure Ollama is running."
)


@dataclass(slots=True)
class Message:
    """One entry of the conversation history."""

    role: str
    content: str

    def as_dict(self) -> dict[str, str]:
        """Return the message in the shape the Ollama API expects."""

        return {"role": self.role, "content": self.content}


class JarvisBrain:
    """Talks to the local Ollama model and remembers the recent conversation.

    The class never raises: any problem with Ollama is logged and turned into
    :data:`FALLBACK_ANSWER` so the assistant can keep listening.
    """

    def __init__(
        self,
        model: str = MODEL,
        history_size: int = MAX_HISTORY,
    ) -> None:
        self.model = model
        self.history_size = max(1, history_size)
        self.host = OLLAMA_HOST
        self._history: list[Message] = []

    @property
    def history(self) -> tuple[Message, ...]:
        """The conversation so far (read only)."""

        return tuple(self._history)

    def reset(self) -> None:
        """Forget the conversation history."""

        self._history.clear()

    def ask(self, text: str) -> str:
        """Answer ``text`` using the local model.

        Args:
            text: The user's question or remark.

        Returns:
            The model's reply, or :data:`FALLBACK_ANSWER` when Ollama is
            unreachable.
        """

        question = (text or "").strip()

        if not question:
            return ""

        self._history.append(Message("user", question))

        try:
            answer = self._chat(self._payload())

        except Exception as error:  # noqa: BLE001 - Ollama raises many types
            log.error("Ollama request failed: %s", error)
            self._history.pop()
            return FALLBACK_ANSWER

        if not answer:
            self._history.pop()
            return FALLBACK_ANSWER

        self._history.append(Message("assistant", answer))
        self._trim()

        return answer

    def _trim(self) -> None:
        """Keep only the newest messages so the history stays bounded."""

        if len(self._history) > self.history_size:
            del self._history[: -self.history_size]

    def _payload(self) -> list[dict[str, str]]:
        """Build the message list sent to the model.

        Only the newest ``history_size`` messages are sent, so the context
        stays small and the local model stays fast.
        """

        recent = self._history[-self.history_size :]

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            *(message.as_dict() for message in recent),
        ]

    def _chat(self, messages: list[dict[str, str]]) -> str:
        """Send ``messages`` to Ollama and return the reply text."""

        import ollama  # imported lazily: JARVIS can start without Ollama

        response = ollama.chat(model=self.model, messages=messages)

        return str(response["message"]["content"]).strip()


brain = JarvisBrain()


def ask_ai(text: str) -> str:
    """Ask the shared brain instance (convenience function)."""

    return brain.ask(text)
