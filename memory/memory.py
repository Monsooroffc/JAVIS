import json
import os
from datetime import datetime

from config import MEMORY_FILE


def load_memory():
    """Load saved memories."""

    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def save_memory(memory):
    """Save memories safely."""

    os.makedirs(
        os.path.dirname(MEMORY_FILE),
        exist_ok=True
    )

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            indent=4,
            ensure_ascii=False
        )


def remember(text):
    """Save a new memory."""

    text = text.strip()

    if not text:
        return False

    memories = load_memory()

    # Avoid duplicates
    for memory in memories:

        if isinstance(memory, dict):

            if memory.get("text", "").lower() == text.lower():
                return False

        elif isinstance(memory, str):

            if memory.lower() == text.lower():
                return False

    memories.append({
        "text": text,
        "created": datetime.now().isoformat(timespec="seconds")
    })

    save_memory(memories)

    return True


def get_memory():
    """Return all memories."""

    return load_memory()


def search_memory(query):
    """Search saved memories."""

    query = query.lower().strip()

    if not query:
        return []

    results = []

    for memory in load_memory():

        if isinstance(memory, dict):
            text = memory.get("text", "")
        else:
            text = str(memory)

        if query in text.lower():
            results.append(memory)

    return results


def clear_memory():
    """Delete all JARVIS memories."""

    save_memory([])


def memory_count():
    """Return number of memories."""

    return len(load_memory())