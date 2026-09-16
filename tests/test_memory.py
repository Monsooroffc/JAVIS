"""Tests for the JSON memory store (``memory.memory``)."""

import json
import tempfile
import unittest
from pathlib import Path

from memory.memory import Memory, MemoryStore


class MemoryStoreTests(unittest.TestCase):
    """The store lives in a temporary folder so the real file is untouched."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "memory.json"
        self.store = MemoryStore(self.path)

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_file_is_empty(self):
        self.assertEqual(self.store.load(), [])
        self.assertEqual(self.store.count(), 0)

    def test_add_and_load(self):
        self.assertTrue(self.store.add("my wifi is Home"))

        memories = self.store.load()

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].text, "my wifi is Home")
        self.assertTrue(memories[0].created)

    def test_duplicates_are_rejected(self):
        self.store.add("my wifi is Home")

        self.assertFalse(self.store.add("MY WIFI IS HOME"))
        self.assertEqual(self.store.count(), 1)

    def test_blank_text_is_rejected(self):
        self.assertFalse(self.store.add("   "))
        self.assertFalse(self.store.add(""))

    def test_search(self):
        self.store.add("my wifi is Home")
        self.store.add("my birthday is in June")

        self.assertEqual(
            [memory.text for memory in self.store.search("wifi")],
            ["my wifi is Home"],
        )
        self.assertEqual(self.store.search(""), [])

    def test_clear(self):
        self.store.add("something")
        self.store.clear()

        self.assertEqual(self.store.load(), [])

    def test_legacy_plain_string_entries_are_supported(self):
        self.path.write_text(json.dumps(["old memory"]), encoding="utf-8")

        self.assertEqual(
            [memory.text for memory in self.store.load()],
            ["old memory"],
        )

    def test_broken_file_is_ignored(self):
        self.path.write_text("{ not json", encoding="utf-8")

        self.assertEqual(self.store.load(), [])

    def test_non_list_file_is_ignored(self):
        self.path.write_text(json.dumps({"text": "nope"}), encoding="utf-8")

        self.assertEqual(self.store.load(), [])

    def test_saved_file_is_readable_json(self):
        self.store.add("hello")

        data = json.loads(self.path.read_text(encoding="utf-8"))

        self.assertEqual(data[0]["text"], "hello")

    def test_from_entry_ignores_invalid_data(self):
        self.assertIsNone(Memory.from_entry(42))
        self.assertIsNone(Memory.from_entry({"text": "   "}))
        self.assertIsNone(Memory.from_entry(""))
        self.assertEqual(Memory.from_entry("plain").text, "plain")
        self.assertEqual(Memory.from_entry({"text": "x"}).created, "")


if __name__ == "__main__":
    unittest.main()