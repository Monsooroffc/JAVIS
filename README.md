# JARVIS

> A local, voice-controlled personal AI assistant for Windows — speech in, actions out, no cloud AI subscription required.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://github.com/Monsooroffc/JAVIS/actions/workflows/ci.yml/badge.svg)
![AI](https://img.shields.io/badge/AI-Ollama%20(local)-black)

JARVIS listens for the wake word **"jarvis"**, understands what you ask, drives
your computer (applications, browser, folders), remembers facts you tell it, and
answers questions with a language model running entirely on your own machine.

---

## Table of contents

- [Features](#features)
- [Quick start](#quick-start)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Voice commands](#voice-commands)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Area | What you get |
| ---- | ------------ |
| **Voice** | Wake word detection, continuous conversation, `pyttsx3` speech output |
| **Routing** | Deterministic offline intent router — instant replies, no model call for simple commands |
| **AI brain** | Local Ollama model (default `qwen2.5:1.5b`) with a rolling conversation history |
| **Memory** | Remembers facts you ask it to store, in a plain, human-readable JSON file |
| **Agent + tools** | Launches apps, opens websites, Google/YouTube searches, full Playwright browser control |
| **System** | Time, date and weekday answers |
| **Engineering** | Typed modules, one-way dependencies, central logging, atomic file writes, 60+ unit tests |

---

## Quick start

```powershell
git clone https://github.com/Monsooroffc/JAVIS.git
cd JAVIS
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull qwen2.5:1.5b

python jarvis.py            # full voice mode
python jarvis.py --text     # type commands (no microphone needed)
```

Example session:

```text
PS> python jarvis.py --text

============================================================
                       JARVIS  v7.0.0
============================================================
  AI brain  : qwen2.5:1.5b
  Memory    : memory.json
  Input     : keyboard
  Wake word : jarvis
  Speech    : on
============================================================

JARVIS: Hello bro. JARVIS v7.0.0 is online.
YOU: what time is it
JARVIS: It is 9:41 PM, bro.
YOU: open notepad
JARVIS: Opening Notepad, bro.
YOU: remember my wifi is Home
JARVIS: Got it bro. I saved that to my memory.
YOU: exit
JARVIS: Goodbye bro. JARVIS is going offline.
```

---

## Architecture

Each layer has exactly one job and only depends on the layer below it. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full diagram.

```text
microphone ──► voice.listen ──► brain.router ──► Intent + Route
                                                    │
                    agent.planner ──────────────────┤
                         │                          │
                    agent.agent ──► tools.*         │
                         │        (apps/browser/files)
                         ▼                          ▼
                    commands.*                 brain.ai ──► Ollama (local)
                                                    │
voice.speak ◄────────── jarvis.Jarvis ◄─────────────┘
                              │
                       memory.memory (JSON)
```

Design rules applied throughout:

1. **One direction of dependency** — nothing imports the entry point.
2. **No side effects on import** — the microphone, speech engine and browser are created lazily, so `--version`, the CLI and the test suite work on any machine.
3. **Nothing crashes the assistant** — every external call (Ollama, Playwright, audio, filesystem) is guarded; failures become a spoken sentence plus a log entry.
4. **Data over branches** — applications, websites and processes live in tables, not in long `if` chains.
5. **Pure functions where possible** — the router, `to_url` and the time/date helpers are pure, which is why they are cheap to test.

---

## Project structure

```text
JAVIS/
├── jarvis.py                  # entry point: CLI, wake word loop, reply handling
├── config.py                  # every setting, all env-overridable
├── requirements.txt
├── pyproject.toml             # metadata, dependencies, ruff config
├── LICENSE                    # MIT
├── .github/workflows/ci.yml   # tests + compile check on every push
├── brain/
│   ├── router.py              # Intent enum + Route dataclass + matching rules
│   └── ai.py                  # JarvisBrain: history + Ollama calls
├── agent/
│   ├── planner.py             # text -> Route
│   └── agent.py               # Intent -> tool call
├── tools/
│   ├── apps.py                # App/AppRegistry (Notepad, Calculator, Paint, Chrome)
│   ├── browser.py             # BrowserAgent on Playwright
│   ├── files.py               # reveal the project folder
│   └── manager.py             # ToolManager facade
├── commands/
│   ├── system.py              # time / date / day
│   └── computer.py            # websites, searches, closing programs
├── voice/
│   ├── listen.py              # Listener: microphone -> text
│   └── speak.py               # Speaker: text -> speech
├── memory/
│   └── memory.py              # MemoryStore: atomic JSON persistence
├── core/
│   ├── engine.py              # running / conversation state
│   └── logger.py              # logging setup
├── docs/ARCHITECTURE.md
├── legacy/                    # earlier single-file versions (reference only)
└── tests/                     # unittest suite (70+ tests)
```

---

## Installation

**Requirements:** Windows 10/11, Python 3.11+, a microphone and speakers,
[Ollama](https://ollama.com) for the local brain, and Google Chrome for the
browser tools.

```powershell
git clone https://github.com/Monsooroffc/JAVIS.git
cd JAVIS
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chrome      # skip if Chrome is already installed
ollama pull qwen2.5:1.5b
```

---

## Usage

### Command line options

```text
python jarvis.py                 # voice mode: wake word + continuous conversation
python jarvis.py --text          # type your commands instead of speaking
python jarvis.py --once "what time is it"   # answer one command and exit
python jarvis.py --no-voice      # print replies without speaking them
python jarvis.py --debug         # verbose logging
python jarvis.py --version       # print the version
python jarvis.py --help          # full option list
```

### Voice mode

1. JARVIS calibrates the microphone and says hello.
2. Say the wake word: **"jarvis"**.
3. Keep talking — conversation mode stays open.
4. Say **"goodbye"**, **"go to sleep"** or **"stop listening"** to end the
   conversation and go back to waiting for the wake word.

### Text mode

Useful without a microphone, for debugging, or over SSH — the router, agent,
tools, memory and AI brain all behave exactly as in voice mode.

### As an installed command (optional)

```powershell
pip install -e .
jarvis --text
```

---

## Voice commands

| Say this | What happens |
| -------- | ------------ |
| `jarvis` | Wakes the assistant ("Yes bro. I'm listening.") |
| `goodbye` / `go to sleep` | Ends the conversation, waits for the wake word again |
| `exit` | Shuts JARVIS down |
| `what time is it` | Spoken time |
| `what date is it` / `what day is it` | Spoken date / weekday |
| `open notepad` / `open calculator` / `open paint` / `open chrome` | Launches the application |
| `close chrome` / `close notepad` | Kills that process |
| `open youtube` / `open github` / `open chatgpt` | Opens the site in your browser |
| `open github.com` | Opens any domain you name |
| `search for python tutorials` | Google search |
| `play lofi beats` | YouTube search |
| `type hello world` | Types into the automated browser page |
| `press enter` | Presses a key |
| `click login` | Clicks matching text on the page |
| `find price` | Reports whether the text is on the page |
| `read page` | Reads the page title and text |
| `scroll down` | Scrolls the browser |
| `open jarvis folder` | Opens the project folder in Explorer |
| `remember my wifi is Home` | Stores a fact in `memory.json` |
| `what do you remember` | Lists everything stored |
| *anything else* | Answered by the local Ollama model |

Filler words (`please`, `can you`, `bro`, `hey jarvis`, …) are ignored, so
*"bro, could you please open notepad"* works exactly like `open notepad`.

---

## Configuration

Every setting lives in `config.py` and can be overridden by an environment
variable — no code changes needed:

```powershell
$env:JARVIS_MODEL = "llama3.2:3b"
$env:JARVIS_WAKE_WORD = "computer"
$env:JARVIS_USER_TITLE = "boss"
$env:JARVIS_LOG_LEVEL = "DEBUG"
$env:JARVIS_LOG_TO_FILE = "true"
python jarvis.py
```

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `JARVIS_MODEL` | `qwen2.5:1.5b` | Ollama model |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama server |
| `JARVIS_NAME` | `JARVIS` | Assistant name |
| `JARVIS_WAKE_WORD` | `jarvis` | Wake word |
| `JARVIS_USER_TITLE` | `bro` | How JARVIS addresses you |
| `JARVIS_LANGUAGE` | `en-US` | Recognition language |
| `JARVIS_LISTEN_TIMEOUT` | `5` | Seconds to wait for speech |
| `JARVIS_PHRASE_TIME_LIMIT` | `8` | Max seconds per phrase |
| `JARVIS_SPEECH_RATE` | `175` | Words per minute |
| `JARVIS_SPEECH_VOLUME` | `1.0` | Volume (0.0 – 1.0) |
| `JARVIS_MAX_HISTORY` | `10` | Messages kept in the AI context |
| `JARVIS_MEMORY_FILE` | `memory.json` | Memory file location |
| `JARVIS_BROWSER_CHANNEL` | `chrome` | Playwright browser channel |
| `JARVIS_BROWSER_HEADLESS` | `false` | Hide the browser window |
| `JARVIS_LOG_LEVEL` | `INFO` | `DEBUG` … `ERROR` |
| `JARVIS_LOG_TO_FILE` | `false` | Also write `logs/jarvis.log` |

---

## Testing

The suite uses the standard library `unittest` only — no extra packages — and
mocks everything external (Ollama, Playwright, subprocess, audio devices).

```powershell
python -m unittest discover -s tests -t . -v     # 96 tests
```

| Test file | Covers |
| --------- | ------ |
| `tests/test_router.py` | Text normalisation and every intent |
| `tests/test_brain.py` | Ollama wrapper, history trimming, error fallback |
| `tests/test_memory.py` | JSON store, duplicates, atomic writes, legacy formats |
| `tests/test_agent.py` | Planner + intent-to-tool dispatch |
| `tests/test_tools.py` | URL building, browser guards, app registry, folders |
| `tests/test_commands.py` | Time/date answers, websites, process closing |
| `tests/test_jarvis.py` | Assistant behaviour, text loop, CLI flags |

GitHub Actions runs the same suite on Windows with Python 3.13 for every push
and pull request (see `.github/workflows/ci.yml`).

---

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `Microphone error` at start-up | Install `pyaudio`, check Windows microphone permissions, or use `--text` |
| "I couldn't reach my local AI brain" | Start Ollama (`ollama serve`) and run `ollama pull qwen2.5:1.5b` |
| Browser actions do nothing | Install Google Chrome, then `playwright install chrome` |
| No sound from JARVIS | Check the Windows output device and volume, or pass `--no-voice` |
| Wake word never triggers | Lower `JARVIS_LISTEN_TIMEOUT`/raise the mic gain, or change `JARVIS_WAKE_WORD` |
| Voice recognition is slow | It uses the online Google Web Speech API; `--text` avoids it |

---

## Roadmap

- [x] Typed, tested package layout with CI
- [x] Text mode and single-command CLI
- [x] Local AI brain with bounded context
- [x] Atomic, format-tolerant memory store
- [ ] Wake word engine that runs fully offline (e.g. Porcupine/Vosk)
- [ ] Plugin interface for third-party tools
- [ ] Packaging as a Windows executable (`pyinstaller`)

---

## Contributing

1. Create a branch: `git checkout -b feature/my-idea`.
2. Make the change and add tests under `tests/`.
3. Run `python -m unittest discover -s tests -t . -v` until it is green.
4. Keep the module docstrings and type hints up to date, then open a pull request.

The design rules in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explain where
new code belongs.

---

## License

Released under the [MIT License](LICENSE).

Built by [Mansoor Aliyar](https://github.com/Monsooroffc).
Earlier prototypes are kept in [`legacy/`](legacy/README.md) for reference.