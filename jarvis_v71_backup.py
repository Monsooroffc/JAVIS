#!/usr/bin/env python
"""JARVIS - a local, voice controlled personal AI assistant.

Usage::

    python jarvis.py                      # wake word + continuous conversation
    python jarvis.py --text               # type your commands instead
    python jarvis.py --once "what time is it"
    python jarvis.py --debug
"""

from __future__ import annotations

import argparse
import sys

from agent.agent import JarvisAgent
from brain.ai import JarvisBrain
from brain.router import Intent, Route, route_command
from commands.computer import execute_command
from commands.system import system_command
from config import (
    ASSISTANT_NAME,
    MODEL,
    SLEEP_PHRASES,
    THINKING_ENABLED,
    THINKING_INTENTS,
    THINKING_PHRASES,
    USER_TITLE,
    VERSION,
    WAKE_WORD,
)
from core.engine import JarvisEngine
from core.logger import configure_logging, get_logger
from core.phrases import PhraseSpinner
from memory.memory import MemoryStore, store as default_memory_store
from voice.listen import Listener
from voice.speak import Speaker

__all__ = ["Jarvis", "build_parser", "main"]

log = get_logger(__name__)


class Jarvis:
    """The assistant.

    A sentence comes in, :mod:`brain.router` decides what it means, the agent
    or the local model performs it, and the answer is spoken back.
    """

    def __init__(
        self,
        *,
        voice: bool = True,
        text_input: bool = False,
        brain: JarvisBrain | None = None,
        agent: JarvisAgent | None = None,
        memory: MemoryStore | None = None,
        speaker: Speaker | None = None,
        listener: Listener | None = None,
        thinking: bool = THINKING_ENABLED,
    ) -> None:
        self.engine = JarvisEngine()
        self.brain = brain or JarvisBrain()
        self.agent = agent or JarvisAgent()
        self.memory = memory or default_memory_store
        self.speaker = speaker or Speaker(enabled=voice)
        self.listener = listener or Listener()
        self.text_input = text_input
        self.thinking_enabled = thinking
        self.phrases = PhraseSpinner(THINKING_PHRASES, title=USER_TITLE)

    # =========================
    # INPUT / OUTPUT
    # =========================

    def say(self, text: str) -> None:
        """Print a reply and read it out loud."""

        message = str(text or "").strip()

        if not message:
            return

        print(f"{ASSISTANT_NAME}: {message}")
        self.speaker.say(message)

    def prompt(self) -> str:
        """Read one typed command (used by text mode)."""

        try:
            return input("YOU: ").strip().lower()

        except (EOFError, KeyboardInterrupt):
            print()

            return "exit"

    # =========================
    # COMMAND HANDLING
    # =========================

    def handle(self, text: str) -> bool:
        """Handle a single command.

        Returns:
            ``False`` when JARVIS should shut down, ``True`` to keep going.
        """

        route = route_command(text)
        log.info("Route: %s", route.intent.value)

        if route.intent is Intent.EXIT:
            self.say(f"Goodbye {USER_TITLE}. {ASSISTANT_NAME} is going offline.")

            return False

        if route.intent is Intent.MEMORY:
            self._show_memory()

            return True

        if route.intent is Intent.REMEMBER:
            self._remember(route.query or "")

            return True

        answer = self._execute(route)
        self.say(answer or f"I couldn't do that, {USER_TITLE}.")

        return True

    def acknowledge(self, route: Route) -> str | None:
        """Say a short line *before* an action that takes a moment.

        This is what keeps JARVIS talking instead of going silent while it
        thinks or opens something. Instant commands (time, date, launching an
        app) are never delayed: only the intents in
        :data:`config.THINKING_INTENTS` get a filler line.

        Returns:
            The line that was spoken, or ``None`` when nothing was said.
        """

        if not self.thinking_enabled:
            return None

        if route.intent.value not in THINKING_INTENTS:
            return None

        line = self.phrases.next()

        if not line:
            return None

        log.debug("Thinking filler: %s", line)
        self.say(line)

        return line

    def _execute(self, route: Route) -> str | None:
        """Perform ``route`` and return the reply, or ``None`` on failure."""

        if route.intent is Intent.SYSTEM:
            return system_command(route.command)

        if route.intent is Intent.CLOSE_APP:
            return execute_command(route.command)

        # Keep talking to the user while the slow work happens.
        self.acknowledge(route)

        if self.agent.handles(route):
            return self.agent.process(route.command)

        # Everything the router does not recognise is a question for the AI.
        return self.brain.ask(route.query or route.command)

    def _remember(self, text: str) -> None:
        """Store a new memory and confirm it."""

        if not text:
            self.say(f"What should I remember, {USER_TITLE}?")

            return

        if self.memory.add(text):
            self.say(f"Got it {USER_TITLE}. I saved that to my memory.")

        else:
            self.say("I already remember that.")

    def _show_memory(self) -> None:
        """Read out how many memories exist and print the list."""

        memories = self.memory.load()

        if not memories:
            self.say(f"My memory is currently empty, {USER_TITLE}.")

            return

        self.say(f"I have {len(memories)} memories saved, {USER_TITLE}.")

        print("-" * 60)

        for index, memory in enumerate(memories, start=1):
            print(f"{index:>2}. {memory.text}")

            if memory.created:
                print(f"    saved: {memory.created}")

        print("-" * 60)

    # =========================
    # RUNTIME
    # =========================

    def print_banner(self) -> None:
        """Print the start up banner."""

        print()
        print("=" * 60)
        print(f"{ASSISTANT_NAME}  v{VERSION}".center(60))
        print("=" * 60)

        for label, value in (
            ("AI brain", MODEL),
            ("Memory", self.memory.path.name),
            ("Input", "keyboard" if self.text_input else "microphone"),
            ("Wake word", WAKE_WORD),
            ("Speech", "on" if self.speaker.enabled else "off"),
        ):
            print(f"  {label:<10}: {value}")

        print("=" * 60)
        print()

    def run(self) -> int:
        """Run the assistant until the user says goodbye.

        Returns:
            The process exit code (``0`` on a clean shutdown).
        """

        self.print_banner()

        if not self.text_input and not self.listener.calibrate():
            print("Microphone unavailable. Run with --text to type commands.")

            return 1

        self.say(f"Hello {USER_TITLE}. {ASSISTANT_NAME} v{VERSION} is online.")

        while self.engine.should_continue():
            if self.text_input:
                self._text_round()
            else:
                self._voice_round()

        self.speaker.stop()

        return 0

    def _text_round(self) -> None:
        """Read one typed command and handle it."""

        command = self.prompt()

        if not command:
            return

        if not self.handle(command):
            self.engine.shutdown()

    def _voice_round(self) -> None:
        """Wait for the wake word, then keep the conversation open."""

        print(f"\nWaiting for the wake word ('{WAKE_WORD}')...")

        heard = self.listener.listen()

        if not heard:
            return

        if WAKE_WORD.lower() not in heard.lower():
            log.debug("Ignored (no wake word): %s", heard)

            return

        self.say(f"Yes {USER_TITLE}. I'm listening.")
        self.engine.start_conversation()

        while self.engine.conversation_mode and self.engine.should_continue():
            print("\nListening...")

            command = self.listener.listen()

            if not command:
                self.say(f"I didn't hear you, {USER_TITLE}.")
                continue

            if any(phrase in command for phrase in SLEEP_PHRASES):
                self.say(f"Okay {USER_TITLE}. I'll wait for you.")
                self.engine.stop_conversation()

                return

            if not self.handle(command):
                self.engine.shutdown()

                return


def run_once(command: str, voice: bool = True) -> int:
    """Handle a single command and exit (used by ``--once``)."""

    assistant = Jarvis(voice=voice, text_input=True)

    try:
        assistant.handle(command)

    finally:
        assistant.speaker.stop()

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""

    parser = argparse.ArgumentParser(
        prog="jarvis",
        description=f"{ASSISTANT_NAME} - a local, voice controlled assistant.",
    )
    parser.add_argument(
        "-t",
        "--text",
        action="store_true",
        help="type commands instead of speaking them",
    )
    parser.add_argument(
        "-o",
        "--once",
        metavar="COMMAND",
        help="handle a single command and exit",
    )
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="print the replies without speaking them",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{ASSISTANT_NAME} {VERSION}",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Command line entry point.

    Returns:
        The process exit code.
    """

    args = build_parser().parse_args(argv)
    configure_logging("DEBUG" if args.debug else None)

    voice = not args.no_voice

    if args.once:
        return run_once(args.once, voice=voice)

    assistant = Jarvis(voice=voice, text_input=args.text)

    try:
        return assistant.run()

    except KeyboardInterrupt:
        print()
        assistant.say(f"Goodbye {USER_TITLE}.")
        assistant.speaker.stop()

        return 0


if __name__ == "__main__":
    sys.exit(main())