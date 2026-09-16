"""Tests for the local AI brain wrapper (``brain.ai``)."""

import unittest

from brain.ai import FALLBACK_ANSWER, JarvisBrain
from config import SYSTEM_PROMPT


class FakeBrain(JarvisBrain):
    """A brain that never touches the network."""

    def __init__(self, reply: str = "Hello", error: Exception | None = None, **kwargs):
        super().__init__(**kwargs)
        self.reply = reply
        self.error = error
        self.calls: list[list[dict[str, str]]] = []

    def _chat(self, messages):
        self.calls.append(messages)

        if self.error is not None:
            raise self.error

        return self.reply


class JarvisBrainTests(unittest.TestCase):
    def test_ask_returns_the_answer(self):
        self.assertEqual(FakeBrain("Hello bro").ask("hi"), "Hello bro")

    def test_history_stores_both_sides_of_the_conversation(self):
        brain = FakeBrain()
        brain.ask("hi")

        self.assertEqual([message.role for message in brain.history], ["user", "assistant"])

    def test_system_prompt_is_always_sent_first(self):
        brain = FakeBrain()
        brain.ask("hi")

        self.assertEqual(
            brain.calls[0][0],
            {"role": "system", "content": SYSTEM_PROMPT},
        )

    def test_history_is_trimmed_to_the_configured_size(self):
        brain = FakeBrain(history_size=2)

        for text in ("one", "two", "three"):
            brain.ask(text)

        self.assertEqual(len(brain.history), 2)
        # At most the system prompt plus two remembered messages.
        self.assertLessEqual(len(brain.calls[-1]), 3)

    def test_errors_are_turned_into_the_fallback_answer(self):
        brain = FakeBrain(error=RuntimeError("ollama is not running"))

        self.assertEqual(brain.ask("hi"), FALLBACK_ANSWER)
        self.assertEqual(brain.history, ())

    def test_empty_reply_uses_the_fallback(self):
        self.assertEqual(FakeBrain(reply="").ask("hi"), FALLBACK_ANSWER)

    def test_blank_text_is_ignored(self):
        brain = FakeBrain()

        self.assertEqual(brain.ask("   "), "")
        self.assertEqual(brain.calls, [])

    def test_reset_clears_the_history(self):
        brain = FakeBrain()
        brain.ask("hi")
        brain.reset()

        self.assertEqual(brain.history, ())

    def test_default_model_comes_from_the_config(self):
        from config import MODEL

        self.assertEqual(JarvisBrain().model, MODEL)


if __name__ == "__main__":
    unittest.main()