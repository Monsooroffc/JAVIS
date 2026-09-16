"""Tests for the intent router (``brain.router``)."""

import unittest

from brain.router import Intent, normalize, route_command


class NormalizeTests(unittest.TestCase):
    """The text normaliser must be forgiving but never destructive."""

    def test_strips_filler_words(self):
        self.assertEqual(
            normalize("Could you please open notepad bro"),
            "open notepad",
        )

    def test_keeps_words_that_merely_contain_a_filler_word(self):
        # "bro" used to be replaced inside words, turning "brother" into "ther".
        self.assertEqual(normalize("open brother notes"), "open brother notes")

    def test_lowercases_and_collapses_whitespace(self):
        self.assertEqual(normalize("   OPEN    Notepad  "), "open notepad")

    def test_handles_empty_input(self):
        self.assertEqual(normalize(""), "")
        self.assertEqual(normalize(None), "")


class RouteCommandTests(unittest.TestCase):
    """Every documented command must route to the expected intent."""

    def test_exit(self):
        self.assertIs(route_command("goodbye").intent, Intent.EXIT)

    def test_memory_question(self):
        self.assertIs(route_command("what do you remember").intent, Intent.MEMORY)

    def test_remember_extracts_the_text(self):
        route = route_command("remember my wifi is Home")

        self.assertIs(route.intent, Intent.REMEMBER)
        self.assertEqual(route.query, "my wifi is home")

    def test_bare_remember_asks_for_the_text(self):
        route = route_command("remember")

        self.assertIs(route.intent, Intent.REMEMBER)
        self.assertEqual(route.query, "")

    def test_open_app(self):
        route = route_command("open notepad")

        self.assertIs(route.intent, Intent.OPEN_APP)
        self.assertEqual(route.query, "notepad")

    def test_open_jarvis_folder_is_not_stolen_by_the_website_rule(self):
        self.assertIs(
            route_command("open jarvis folder").intent,
            Intent.OPEN_JARVIS_FOLDER,
        )

    def test_open_website(self):
        route = route_command("open github.com")

        self.assertIs(route.intent, Intent.OPEN_WEBSITE)
        self.assertEqual(route.query, "github.com")

    def test_open_website_drops_a_trailing_website_word(self):
        route = route_command("open website wikipedia.org")

        self.assertIs(route.intent, Intent.OPEN_WEBSITE)
        self.assertEqual(route.query, "wikipedia.org")

    def test_google_search(self):
        route = route_command("search for python tutorials")

        self.assertIs(route.intent, Intent.GOOGLE_SEARCH)
        self.assertEqual(route.query, "python tutorials")

    def test_youtube_search(self):
        route = route_command("play lofi beats")

        self.assertIs(route.intent, Intent.YOUTUBE_SEARCH)
        self.assertEqual(route.query, "lofi beats")

    def test_browser_type_press_click_and_find(self):
        cases = (
            ("type hello world", Intent.BROWSER_TYPE, "hello world"),
            ("press enter", Intent.BROWSER_PRESS, "enter"),
            ("click login", Intent.BROWSER_CLICK, "login"),
            ("find price", Intent.BROWSER_FIND, "price"),
        )

        for text, intent, query in cases:
            with self.subTest(text=text):
                route = route_command(text)

                self.assertIs(route.intent, intent)
                self.assertEqual(route.query, query)

    def test_scroll_and_read(self):
        self.assertIs(route_command("scroll down").intent, Intent.BROWSER_SCROLL)
        self.assertIs(route_command("read page").intent, Intent.BROWSER_READ)

    def test_system(self):
        self.assertIs(route_command("what time is it").intent, Intent.SYSTEM)

    def test_close_app(self):
        route = route_command("close chrome")

        self.assertIs(route.intent, Intent.CLOSE_APP)
        self.assertEqual(route.query, "chrome")

    def test_unknown_text_falls_back_to_the_ai(self):
        route = route_command("tell me a joke about python")

        self.assertIs(route.intent, Intent.AI)
        self.assertEqual(route.query, "tell me a joke about python")

    def test_intents_stay_comparable_with_plain_strings(self):
        # Older code compared route types with strings.
        self.assertEqual(route_command("time").intent, "system")

    def test_as_dict(self):
        self.assertEqual(
            route_command("time").as_dict(),
            {"type": "system", "command": "time", "query": None},
        )


if __name__ == "__main__":
    unittest.main()