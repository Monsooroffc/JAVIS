"""Long term memory backed by a small JSON file.

The store tolerates the older on-disk formats (a bare list of strings or a
list of ``{"text": ..., "created": ...}`` objects) and writes atomically, so a
crash can never leave a broken ``memory.json`` behind.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator

from config import MEMORY_FILE
from core.logger import get_logger

__all__ = [
    "Memory",
    "MemoryStore",
    "clear_memory",
    "get_memory",
    "load_memory",
    "memory_count",
    "remember",
    "save_memory",
    "search_memory",
    "store",
]

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class Memory:
    """A single remembered fact."""

    text: str
    created: str = ""

    def as_dict(self) -> dict[str, str]:
        """Return the on-disk representation of this memory."""

        return {"text": self.text, "created": self.created}

    @classmethod
    def from_entry(cls, entry: object) -> Memory | None:
        """Build a memory from raw JSON data, or ``None`` when invalid."""

        if isinstance(entry, Memory):
            return entry if entry.text else None

        if isinstance(entry, dict):
            text = str(entry.get("text", "")).strip()
            created = str(entry.get("created", "") or "")

        elif isinstance(entry, str):
            text, created = entry.strip(), ""

        else:
            return None

        if not text:
            return None

        return cls(text=text, created=created)


Entry = Memory | str | dict


class MemoryStore:
    """Reads and writes the JSON memory file."""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path) if path is not None else Path(MEMORY_FILE)

    # =========================
    # READING
    # =========================

    def load(self) -> list[Memory]:
        """Load every memory, returning an empty list when unreadable."""

        if not self.path.exists():
            return []

        try:
            with self.path.open("r", encoding="utf-8") as file:
                raw = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            log.error("Could not read %s: %s", self.path.name, error)
            return []

        if not isinstance(raw, list):
            log.error("%s does not contain a list of memories.", self.path.name)
            return []

        memories = [Memory.from_entry(entry) for entry in raw]

        return [memory for memory in memories if memory is not None]

    def search(self, query: str) -> list[Memory]:
        """Return every memory containing ``query`` (case insensitive)."""

        needle = (query or "").strip().lower()

        if not needle:
            return []

        return [memory for memory in self.load() if needle in memory.text.lower()]

    def count(self) -> int:
        """Return how many memories are stored."""

        return len(self.load())

    # =========================
    # WRITING
    # =========================

    def save(self, memories: Iterable[Entry]) -> None:
        """Replace the file contents with ``memories``, atomically."""

        cleaned = [memory.as_dict() for memory in _coerce(memories)]

        self.path.parent.mkdir(parents=True, exist_ok=True)

        handle, temp_name = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=".memory-", suffix=".tmp"
        )

        try:
            with os.fdopen(handle, "w", encoding="utf-8") as file:
                json.dump(cleaned, file, indent=4, ensure_ascii=False)
                file.write("\n")

            os.replace(temp_name, self.path)

        except OSError as error:
            log.error("Could not save memories: %s", error)
            _remove(temp_name)

    def add(self, text: str) -> bool:
        """Remember ``text``.

        Returns:
            ``True`` when the fact was stored, ``False`` when it was empty or
            already known.
        """

        sentence = (text or "").strip()

        if not sentence:
            return False

        memories = self.load()

        if any(memory.text.lower() == sentence.lower() for memory in memories):
            log.debug("Memory already stored: %s", sentence)
            return False

        memories.append(
            Memory(
                text=sentence,
                created=datetime.now().isoformat(timespec="seconds"),
            )
        )

        self.save(memories)
        log.info("Stored a new memory: %s", sentence)

        return True

    def clear(self) -> None:
        """Delete every memory."""

        self.save([])


def _coerce(memories: Iterable[Entry]) -> Iterator[Memory]:
    """Yield only the valid memories found in ``memories``."""

    for entry in memories:
        memory = Memory.from_entry(entry)

        if memory is not None:
            yield memory


def _remove(path: str) -> None:
    """Delete ``path``, ignoring errors."""

    try:
        os.remove(path)

    except OSError:  # pragma: no cover - best effort cleanup
        pass


store = MemoryStore()


# =========================
# MODULE LEVEL HELPERS
# =========================


def load_memory() -> list[Memory]:
    """Load every memory stored in the default file."""

    return store.load()


def save_memory(memories: Iterable[Entry]) -> None:
    """Overwrite the default memory file."""

    store.save(memories)


def remember(text: str) -> bool:
    """Store ``text`` in the default memory file."""

    return store.add(text)


def get_memory() -> list[Memory]:
    """Return every memory stored in the default file."""

    return store.load()


def search_memory(query: str) -> list[Memory]:
    """Search the default memory file."""

    return store.search(query)


def clear_memory() -> None:
    """Delete every memory from the default file."""

    store.clear()


def memory_count() -> int:
    """Return how many memories the default file holds."""

    return store.count()