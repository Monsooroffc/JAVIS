import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL = "qwen2.5:1.5b"
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")

WAKE_WORD = "jarvis"

LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 8