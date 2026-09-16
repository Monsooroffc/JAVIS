# JARVIS

JARVIS is a local, voice-controlled personal AI assistant for Windows.

It listens for the wake word **"jarvis"**, understands natural commands,
controls the computer (apps, browser, files), remembers things you tell it,
and answers questions with a local LLM running through Ollama.

No cloud AI key is required for the main assistant - the brain runs on your
own machine (speech input uses the free Google Web Speech API).

---

## Features

| System        | What it does                                                          |
| ------------- | --------------------------------------------------------------------- |
| Voice         | Speech recognition (`speech_recognition`) + speech output (`pyttsx3`)  |
| Wake word     | Say `jarvis` to start, then keep talking in continuous conversation    |
| Router        | Rule-based intent routing (`brain/router.py`) for fast offline control |
| AI brain      | Local LLM via Ollama (`qwen2.5:1.5b`), keeps short chat history        |
| Memory        | Saves and recalls personal notes in `memory.json`                      |
| Agent + Tools | Opens apps, websites, Google/YouTube searches, Playwright browser control |
| System        | Tells time, date and day                                               |

---

## Project structure

```
JARVIS/
|-- jarvis.py              # MAIN ENTRY POINT (JARVIS v6.0)
|-- config.py              # Model, wake word, memory file, timeouts
|-- brain/
|   |-- ai.py              # Ollama chat (local AI brain)
|   `-- router.py          # Natural language -> intent router
|-- agent/
|   |-- agent.py           # Executes the plan using tools
|   `-- planner.py         # Turns routed commands into a plan
|-- tools/
|   |-- manager.py         # Single tool interface used by the agent
|   |-- apps.py            # Open Notepad / Calculator / Paint / Chrome
|   |-- browser.py         # Playwright browser (open, search, type, click, read, scroll)
|   `-- files.py           # Open the JARVIS folder
|-- commands/
|   |-- computer.py        # Legacy direct computer/website commands
|   `-- system.py          # Time / date / day answers
|-- voice/
|   |-- listen.py          # Microphone calibration + speech recognition
|   `-- speak.py           # Text to speech
|-- memory/
|   `-- memory.py          # Load / save / search memories
|-- core/
|   `-- engine.py          # Assistant state (running, conversation mode)
|-- main.py                # Prototype: voice only
|-- jarvis_ai.py           # Prototype: voice + local AI + computer control
|-- jarvis_backup.py       # Older backup version
|-- local_brain.py         # Quick Ollama test script
`-- brain.py               # OpenAI experiment script (optional, needs API key)
```

---

## Requirements

* Windows 10 / 11
* Python 3.10+ (developed on Python 3.13)
* A working microphone and speakers
* [Ollama](https://ollama.com) installed and running for the AI brain
* Google Chrome installed (the Playwright browser uses the `chrome` channel)

---

## Installation

```powershell
# 1. Get the code
git clone https://github.com/Monsooroffc/JAVIS.git
cd JAVIS

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install the Python packages
pip install -r requirements.txt
playwright install chrome    # only if Google Chrome is not installed yet

# 4. Pull the local AI model
ollama pull qwen2.5:1.5b
ollama serve                 # usually already running after install
```

---

## Usage

```powershell
.\venv\Scripts\Activate.ps1
python jarvis.py
```

Then:

1. JARVIS calibrates the microphone and says hello.
2. Say the wake word: **"jarvis"**.
3. Talk normally - conversation mode stays open.
4. Say **"goodbye"**, **"go to sleep"** or **"stop listening"** to end the
   conversation and go back to waiting for the wake word.

---

## Example commands

```
jarvis                      -> "Yes bro. I'm listening."
what time is it             -> It is 09:41 PM, bro.
what date is it             -> Today is 16 September 2026.
open notepad                -> Opening Notepad, bro.
open calculator             -> Opening Calculator, bro.
open chrome                 -> Opening Google Chrome, bro.
open youtube                -> Opens YouTube in the Playwright browser
open github                 -> Opens GitHub
search for python tutorials -> Google search
play lofi beats             -> YouTube search
type hello world            -> Types into the open browser page
press enter                 -> Presses a key
click login                 -> Clicks a matching element
read page                   -> Reads the current page text
scroll down                 -> Scrolls the browser page
open jarvis folder          -> Opens the JARVIS folder in Explorer
remember my wifi is Home    -> Saves it to memory.json
what do you remember        -> Lists everything saved
close chrome                -> Kills the Chrome process
exit                        -> Shuts JARVIS down
```

Anything the router does not recognise is sent to the local AI brain.

---

## Configuration

Edit `config.py`:

```python
MODEL = "qwen2.5:1.5b"   # any model you have pulled in Ollama
WAKE_WORD = "jarvis"     # change the wake word
LISTEN_TIMEOUT = 5       # seconds to wait for speech
PHRASE_TIME_LIMIT = 8    # max seconds per spoken phrase
```

`memory.json` is created automatically at runtime and is ignored by git,
so your personal memories are never pushed to GitHub.

---

## Troubleshooting

| Problem                        | Fix                                                              |
| ------------------------------ | ---------------------------------------------------------------- |
| `Microphone error` on start    | Install `pyaudio` and check Windows microphone permissions        |
| No answer from the AI brain    | Run `ollama serve` and confirm `ollama pull qwen2.5:1.5b` finished |
| Browser actions do nothing     | Install Google Chrome, then run `playwright install chrome`       |
| No voice output                | Check the Windows output device and volume                        |
| `brain.py` fails               | Optional OpenAI experiment - set `OPENAI_API_KEY` or skip it      |

---

## Notes

* `jarvis.py` is the current production entry point (v6.0).
* `main.py`, `jarvis_ai.py`, `jarvis_backup.py`, `local_brain.py` and
  `brain.py` are earlier prototypes / experiments kept for reference.
* `tools/files.py` and the `open jarvis folder` command point to the original
  absolute path of this project - update that path if you clone it elsewhere.
