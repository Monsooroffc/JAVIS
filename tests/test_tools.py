"""Tests for the tool layer (``tools``).

Nothing is really launched: subprocess, Playwright and Explorer are mocked.
"""

import unittest
from pathlib import Path
from unittest import mock

from tools import apps, files
from tools.apps import App, AppRegistry
from tools.browser import BrowserAgent, to_url


class UrlTests(unittest.TestCase):
    def test_a_full_url_is_kept(self):
        self.assertEqual(to_url("https://example.com"), "https://example.com")

    def test_a_domain_gets_https(self):
        self.assertEqual(to_url("github.com"), "https://github.com")

    def test_a_name_becomes_a_search(self):
        self.assertIn("google.com/search", to_url("open ai"))

    def test_empty_input_still_produces_a_url(self):
        self.assertIn("google.com/search", to_url(""))


class BrowserAgentTests(unittest.TestCase):
    def test_reports_when_it_is_not_running(self):
        agent = BrowserAgent()

        self.assertFalse(agent.running)
        self.assertEqual(agent.read(), "The browser is not running.")
        self.assertEqual(agent.scroll(), "The browser is not running.")
        self.assertEqual(agent.type_text("hi"), "The browser is not running.")
        self.assertEqual(agent.press("enter"), "The browser is not running.")
        self.assertEqual(agent.click_text("login"), "The browser is not running.")
        self.assertEqual(agent.find_text("price"), "The browser is not running.")

    def test_open_without_a_name_asks_for_one(self):
        self.assertIn("website name", BrowserAgent().open("   "))

    def test_search_without_a_query_asks_for_one(self):
        self.assertIn("search for", BrowserAgent().search(""))

    def test_stop_is_safe_before_start(self):
        BrowserAgent().stop()

    def test_context_manager_enters_and_exits(self):
        agent = BrowserAgent()

        with mock.patch.object(agent, "start", return_value=False):
            with agent as started:
                self.assertIs(started, agent)


class AppRegistryTests(unittest.TestCase):
    def test_find_is_case_insensitive_and_accepts_aliases(self):
        registry = AppRegistry()

        self.assertEqual(registry.find("CALC").name, "Calculator")
        self.assertEqual(registry.find("Google Chrome").name, "Google Chrome")
        self.assertIsNone(registry.find("photoshop"))

    def test_open_reports_a_missing_application(self):
        registry = AppRegistry()
        ghost = App("Ghost", ("ghost",), "ghost.exe")

        with mock.patch.object(registry, "find", return_value=ghost):
            self.assertIn("couldn't find", registry.open("ghost"))

    def test_open_launches_the_executable(self):
        registry = AppRegistry()
        ghost = App("Ghost", ("ghost",), "ghost.exe")

        with (
            mock.patch.object(registry, "find", return_value=ghost),
            mock.patch.object(App, "executable", return_value="ghost.exe"),
            mock.patch.object(apps.subprocess, "Popen") as popen,
        ):
            answer = registry.open("ghost")

            popen.assert_called_once_with(["ghost.exe"], close_fds=True)
            self.assertIn("Ghost", answer)

    def test_unknown_name_returns_none(self):
        self.assertIsNone(AppRegistry().open("photoshop"))


class FilesToolTests(unittest.TestCase):
    def test_project_folder_is_derived_from_the_config(self):
        self.assertTrue(files.JARVIS_FOLDER.exists())
        self.assertEqual(files.JARVIS_FOLDER, Path(files.BASE_DIR))

    def test_missing_folder_is_reported(self):
        self.assertIn("couldn't find", files.open_folder("no-such-folder-here"))

    def test_open_folder_uses_explorer(self):
        with mock.patch.object(files.subprocess, "Popen") as popen:
            answer = files.open_folder(files.JARVIS_FOLDER)

            popen.assert_called_once_with(
                ["explorer.exe", str(files.JARVIS_FOLDER)]
            )
            self.assertIn("JARVIS folder", answer)


if __name__ == "__main__":
    unittest.main()