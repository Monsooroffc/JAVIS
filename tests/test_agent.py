"""Tests for the planner and the agent (``agent``)."""

import unittest
from unittest import mock

from agent.agent import JarvisAgent
from agent.planner import Planner
from brain.router import Intent, Route
from tools.manager import ToolManager


class PlannerTests(unittest.TestCase):
    def test_plan_returns_a_route(self):
        route = Planner().plan("open notepad")

        self.assertIsInstance(route, Route)
        self.assertIs(route.intent, Intent.OPEN_APP)
        self.assertEqual(route.query, "notepad")


class AgentTests(unittest.TestCase):
    """The agent is tested against a mock tool layer: nothing is launched."""

    def setUp(self):
        self.tools = mock.Mock(spec=ToolManager)
        self.agent = JarvisAgent(tool_manager=self.tools)

    def test_handles_only_its_own_intents(self):
        self.assertTrue(
            self.agent.handles(Route(Intent.OPEN_APP, "open notepad", "notepad"))
        )
        self.assertFalse(self.agent.handles(Route(Intent.AI, "hi", "hi")))
        self.assertFalse(self.agent.handles(Route(Intent.SYSTEM, "time")))

    def test_open_app_passes_the_query(self):
        self.tools.open_app.return_value = "Opening Notepad."

        self.assertEqual(self.agent.process("open notepad"), "Opening Notepad.")
        self.tools.open_app.assert_called_once_with("notepad")

    def test_open_website_passes_the_query(self):
        self.agent.process("open github.com")

        self.tools.open_website.assert_called_once_with("github.com")

    def test_youtube_search_passes_the_query(self):
        self.agent.process("play lofi beats")

        self.tools.youtube_search.assert_called_once_with("lofi beats")

    def test_scroll_needs_no_query(self):
        self.agent.process("scroll down")

        self.tools.scroll.assert_called_once_with()

    def test_read_page(self):
        self.agent.process("read page")

        self.tools.read_page.assert_called_once_with()

    def test_ai_route_is_not_handled(self):
        self.assertIsNone(self.agent.process("tell me a joke"))

    def test_intents_property_lists_the_supported_actions(self):
        self.assertIn(Intent.YOUTUBE_SEARCH, self.agent.intents)
        self.assertNotIn(Intent.AI, self.agent.intents)


if __name__ == "__main__":
    unittest.main()