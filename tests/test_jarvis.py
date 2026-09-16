"""Tests for the assistant itself (``jarvis.Jarvis``).

The assistant is built with a silent speaker, a fake brain and a mock tool
layer, so no microphone, sound card or network connection is needed.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent.agent import JarvisAgent
from brain.ai import JarvisBrain
from config import THINKING_PHRASES, USER_TITLE
from jarvis import Jarvis, build_parser
from memory.memory import MemoryStore
from tools.manager import ToolManager

# The fillers JARVIS should say, with the user title already substituted.
EXPECTED_FILLERS = [
    phrase.format(title=USER_TITLE) for phrase in THINKING_PHRASES
]


class SilentSpeaker:
    """Collects the sentences that would have been spoken."""

    enabled = False

    def __init__(self):
        self.spoken: list[str] = []

    def say(self, text):
        self.spoken.append(str(text))

    def stop(self):
        pass


class EchoBrain(JarvisBrain):
    """A brain that answers instantly without touching Ollama."""

    def __init__(self, reply: str = "AI answer"):
        super().__init__()
        self.reply = reply
        self.asked: list[str] = []

    def ask(self, text):
        self.asked.append(text)

        return self.reply


class JarvisTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self.speaker = SilentSpeaker()
        self.brain = EchoBrain()
        self.memory = MemoryStore(Path(self._tmp.name) / "memory.json")

        self.jarvis = Jarvis(
            voice=False,
            text_input=True,
            brain=self.brain,
            agent=JarvisAgent(tool_manager=mock.Mock(spec=ToolManager)),
            memory=self.memory,
            speaker=self.speaker,
        )

    # =========================
    # COMMANDS
    # =========================

    def test_exit_stops_the_assistant(self):
        self.assertFalse(self.jarvis.handle("goodbye"))

    def test_system_command_does_not_reach_the_ai(self):
        self.assertTrue(self.jarvis.handle("what time is it"))

        self.assertEqual(self.brain.asked, [])
        self.assertTrue(any("It is" in line for line in self.speaker.spoken))

    def test_remember_stores_the_fact(self):
        self.jarvis.handle("remember my wifi is Home")

        # The router lowercases the sentence, so the stored text is lowercase.
        self.assertEqual(
            [memory.text for memory in self.memory.load()],
            ["my wifi is home"],
        )

    def test_remembering_the_same_fact_twice_is_reported(self):
        self.jarvis.handle("remember my wifi is Home")
        self.jarvis.handle("remember my wifi is Home")

        self.assertTrue(
            any("already remember" in line for line in self.speaker.spoken)
        )

    def test_remember_without_text_asks_for_it(self):
        self.jarvis.handle("remember")

        self.assertTrue(
            any("What should I remember" in line for line in self.speaker.spoken)
        )

    def test_memory_list_reports_the_count(self):
        self.jarvis.handle("remember coffee at 9")
        self.jarvis.handle("what do you remember")

        self.assertTrue(
            any("1 memories saved" in line for line in self.speaker.spoken)
        )

    def test_empty_memory_is_reported(self):
        self.jarvis.handle("what do you remember")

        self.assertTrue(
            any("empty" in line for line in self.speaker.spoken)
        )

    def test_agent_actions_are_delegated_to_the_tools(self):
        self.jarvis.agent.tools.open_app.return_value = "Opening Notepad."

        self.jarvis.handle("open notepad")

        self.jarvis.agent.tools.open_app.assert_called_once_with("notepad")
        self.assertEqual(self.brain.asked, [])

    def test_unknown_text_goes_to_the_ai(self):
        self.jarvis.handle("tell me a joke")

        self.assertEqual(self.brain.asked, ["tell me a joke"])
        self.assertTrue(any("AI answer" in line for line in self.speaker.spoken))

    # =========================
    # KEEPING JARVIS TALKING
    # =========================

    def test_slow_actions_speak_a_thinking_line_before_the_answer(self):
        self.jarvis.handle("tell me a joke")

        self.assertEqual(
            self.speaker.spoken,
            [EXPECTED_FILLERS[0], "AI answer"],
        )

    def test_thinking_lines_rotate(self):
        self.jarvis.handle("tell me a joke")
        self.jarvis.handle("tell me another joke")

        self.assertEqual(self.speaker.spoken[0], EXPECTED_FILLERS[0])
        self.assertEqual(
            self.speaker.spoken[2],
            EXPECTED_FILLERS[1 % len(EXPECTED_FILLERS)],
        )

    def test_web_actions_also_get_a_thinking_line(self):
        self.jarvis.agent.tools.open_website.return_value = "Opened github.com."

        self.jarvis.handle("open github.com")

        self.assertEqual(self.speaker.spoken[0], EXPECTED_FILLERS[0])
        self.assertIn("Opened github.com.", self.speaker.spoken)

    def test_instant_commands_are_not_delayed(self):
        self.jarvis.handle("what time is it")

        self.assertEqual(len(self.speaker.spoken), 1)
        self.assertTrue(self.speaker.spoken[0].startswith("It is"))

    def test_thinking_can_be_disabled(self):
        speaker = SilentSpeaker()

        jarvis = Jarvis(
            voice=False,
            text_input=True,
            brain=self.brain,
            agent=JarvisAgent(tool_manager=mock.Mock(spec=ToolManager)),
            memory=self.memory,
            speaker=speaker,
            thinking=False,
        )

        jarvis.handle("tell me a joke")

        self.assertEqual(speaker.spoken, ["AI answer"])

    def test_fillers_respect_the_configured_user_title(self):
        self.assertEqual(list(self.jarvis.phrases.rendered), EXPECTED_FILLERS)

    # =========================
    # INPUT / LOOP
    # =========================

    def test_prompt_reads_and_normalises_typed_input(self):
        with mock.patch("builtins.input", return_value="  Hello  "):
            self.assertEqual(self.jarvis.prompt(), "hello")

    def test_prompt_treats_interrupts_as_exit(self):
        with mock.patch("builtins.input", side_effect=KeyboardInterrupt):
            self.assertEqual(self.jarvis.prompt(), "exit")

    def test_text_mode_run_stops_on_exit(self):
        with (
            mock.patch.object(self.jarvis, "print_banner"),
            mock.patch.object(
                self.jarvis,
                "prompt",
                side_effect=["what time is it", "exit"],
            ),
        ):
            self.assertEqual(self.jarvis.run(), 0)

        self.assertFalse(self.jarvis.engine.running)

    def test_banner_is_printable(self):
        with mock.patch("builtins.print") as printed:
            self.jarvis.print_banner()

        self.assertTrue(printed.called)


class CliTests(unittest.TestCase):
    def test_text_flag(self):
        args = build_parser().parse_args(["--text"])

        self.assertTrue(args.text)
        self.assertFalse(args.no_voice)

    def test_once_flag(self):
        args = build_parser().parse_args(["--once", "what time is it"])

        self.assertEqual(args.once, "what time is it")

    def test_defaults(self):
        args = build_parser().parse_args([])

        self.assertFalse(args.text)
        self.assertFalse(args.debug)
        self.assertIsNone(args.once)


if __name__ == "__main__":
    unittest.main()