"""Tests for the rotating spoken phrases (``core.phrases``)."""

import unittest

from core.phrases import PhraseSpinner


class PhraseSpinnerTests(unittest.TestCase):
    def test_rotates_in_order_and_wraps_around(self):
        spinner = PhraseSpinner(["a", "b"])

        self.assertEqual(
            [spinner.next(), spinner.next(), spinner.next()],
            ["a", "b", "a"],
        )

    def test_reset_starts_from_the_first_phrase_again(self):
        spinner = PhraseSpinner(["a", "b"])
        spinner.next()
        spinner.reset()

        self.assertEqual(spinner.next(), "a")

    def test_title_placeholder_is_filled_in(self):
        spinner = PhraseSpinner(["Hello {title}."], title="boss")

        self.assertEqual(spinner.next(), "Hello boss.")

    def test_broken_placeholder_is_returned_unchanged(self):
        spinner = PhraseSpinner(["Hi {unknown}"])

        self.assertEqual(spinner.next(), "Hi {unknown}")

    def test_no_phrases_returns_an_empty_string(self):
        spinner = PhraseSpinner([])

        self.assertEqual(spinner.next(), "")
        self.assertEqual(len(spinner), 0)

    def test_blank_phrases_are_dropped(self):
        spinner = PhraseSpinner(["  ", "", "hi"])

        self.assertEqual(spinner.phrases, ("hi",))
        self.assertEqual(len(spinner), 1)

    def test_phrases_property_lists_the_raw_templates(self):
        spinner = PhraseSpinner(["Hi {title}."])

        self.assertEqual(spinner.phrases, ("Hi {title}.",))
        self.assertEqual(spinner.rendered, ("Hi .",))

    def test_rendered_phrases_have_the_title_filled_in(self):
        spinner = PhraseSpinner(["One moment, {title}."], title="boss")

        self.assertEqual(spinner.rendered, ("One moment, boss.",))


if __name__ == "__main__":
    unittest.main()