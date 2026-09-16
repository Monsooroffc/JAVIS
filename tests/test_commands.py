"""Tests for the direct command handlers (``commands``)."""

import unittest
from datetime import datetime
from unittest import mock

from commands import computer, system
from config import USER_TITLE


class SystemCommandTests(unittest.TestCase):
    def test_time_answer_uses_a_12_hour_clock(self):
        moment = datetime(2026, 9, 16, 9, 5)

        self.assertEqual(system.time_answer(moment), f"It is 9:05 AM, {USER_TITLE}.")

    def test_date_answer(self):
        self.assertEqual(
            system.date_answer(datetime(2026, 9, 16)),
            "Today is 16 September 2026.",
        )

    def test_day_answer(self):
        self.assertEqual(
            system.day_answer(datetime(2026, 9, 16)),
            "Today is Wednesday.",
        )

    def test_keywords_are_recognised(self):
        for text in (
            "what time is it",
            "time",
            "what date is it",
            "date",
            "what day is it",
        ):
            with self.subTest(text=text):
                self.assertIsNotNone(system.system_command(text))

    def test_other_text_is_ignored(self):
        self.assertIsNone(system.system_command("open notepad"))
        self.assertIsNone(system.system_command(""))
        self.assertIsNone(system.system_command(None))


class ComputerCommandTests(unittest.TestCase):
    def test_empty_text_returns_none(self):
        self.assertIsNone(computer.execute_command(""))
        self.assertIsNone(computer.execute_command(None))

    def test_unrelated_text_returns_none(self):
        self.assertIsNone(computer.execute_command("nothing to see here"))

    def test_open_app_is_delegated_to_the_registry(self):
        with mock.patch.object(
            computer.registry, "open", return_value="Opening Paint."
        ) as patched:
            self.assertEqual(computer.execute_command("open paint"), "Opening Paint.")
            patched.assert_called_once_with("paint")

    def test_open_website_uses_the_browser(self):
        with mock.patch.object(computer.webbrowser, "open") as patched:
            answer = computer.execute_command("open youtube")

            patched.assert_called_once_with("https://www.youtube.com")
            self.assertIn("YouTube", answer)

    def test_search_builds_a_google_url(self):
        with mock.patch.object(computer.webbrowser, "open") as patched:
            computer.execute_command("search for python")

            url = patched.call_args.args[0]

            self.assertTrue(url.startswith("https://www.google.com/search?q="))
            self.assertIn("python", url)

    def test_play_builds_a_youtube_url(self):
        with mock.patch.object(computer.webbrowser, "open") as patched:
            computer.execute_command("play lofi beats")

            self.assertIn("youtube.com/results", patched.call_args.args[0])

    def test_close_kills_the_matching_process(self):
        with mock.patch.object(computer.subprocess, "run") as patched:
            answer = computer.execute_command("close google chrome")

            self.assertEqual(
                patched.call_args.args[0],
                ["taskkill", "/IM", "chrome.exe", "/F"],
            )
            self.assertIn("Google Chrome", answer)

    def test_close_unknown_program_returns_none(self):
        self.assertIsNone(computer.execute_command("close photoshop"))

    def test_jarvis_folder_command(self):
        with mock.patch.object(
            computer, "open_jarvis_folder", return_value="Opening the JARVIS folder."
        ):
            self.assertEqual(
                computer.execute_command("open jarvis folder"),
                "Opening the JARVIS folder.",
            )


if __name__ == "__main__":
    unittest.main()