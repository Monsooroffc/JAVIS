# JARVIS architecture

JARVIS is a small pipeline. Each layer has one job, knows only about the layer
directly below it, and can be tested on its own.

```
        speech / keyboard
                |
                v
        +---------------+
        |  voice.listen |  microphone -> text
        +---------------+
                |
                v
        +---------------+      +-----------------+
        |  brain.router | ---> |  Intent + Route |
        +---------------+      +-----------------+
                |
                v
        +---------------+      +-------------------+
        | agent.planner | ---> | agent.agent       |  executes tool actions
        +---------------+      +-------------------+
                |                       |
                |                       v
                |               +----------------+
                |               |  tools.*       |  apps / browser / files
                |
                v
        +---------------+      +-----------------+
        |  brain.ai     | ---> |  Ollama (local) |
        +---------------+      +-----------------+
                |
                v
        +---------------+      +-----------------+
        |  voice.speak  |      |  memory.memory  |
        +---------------+      +-----------------+
                |
                v
             speakers
```

## Layers

| Layer | Module | Responsibility |
| ----- | ------ | -------------- |
| Entry point | `jarvis.py` | CLI, wake word loop, wiring, spoken replies |
| Config | `config.py` | Every tunable value, each overridable by an environment variable |
| Core | `core/logger.py`, `core/engine.py`, `core/phrases.py` | Logging, rotating filler lines, run/stop state |
| Routing | `brain/router.py` | Text -> `Intent` + `Route` (deterministic, offline) |
| Brain | `brain/ai.py` | `JarvisBrain`: chat history + Ollama calls, never raises |
| Planning | `agent/planner.py` | Wraps the router for the agent |
| Agent | `agent/agent.py` | Maps an intent onto a tool call |
| Tools | `tools/*` | Applications, Playwright browser, folders |
| Commands | `commands/*` | Direct handlers (time/date, websites, closing apps) |
| Voice | `voice/*` | `Listener` (speech to text), `Speaker` (text to speech) |
| Memory | `memory/memory.py` | `MemoryStore`: JSON persistence, atomic writes |

## Design rules

1. **One direction of dependency.** `jarvis.py` may import anything; the lower
   layers never import the entry point.
2. **No side effects on import.** Heavy or device specific objects (microphone,
   `pyttsx3` engine, Playwright) are created lazily, so the CLI, the tests and
   `--version` all work on a machine without a microphone or a browser.
3. **Nothing crashes the assistant.** Every external call (Ollama, Playwright,
   audio, filesystem) is wrapped; failures become a spoken sentence plus a log
   entry.
4. **Data over branches.** Applications, websites and process names live in
   dictionaries/tuples, not in long `if` chains.
5. **Pure functions where possible.** `commands/system.py` accepts a
   `datetime`, `tools/browser.to_url` is pure, the router is pure - which makes
   them trivial to unit test.
6. **Talk while working.** Before a slow action (a language model call, opening
   a page, a search, reading a page) `Jarvis.acknowledge` speaks one line from
   `core/phrases.py`, so the assistant never goes silent after you stop talking.
   The list of slow intents and the lines themselves live in `config.py`.

## Adding a new command

1. Add the value to `Intent` in `brain/router.py`.
2. Add the matching rule inside `route_command`.
3. Either add a handler in `agent/agent.py` (if it needs a tool), or handle the
   intent in `Jarvis._execute` in `jarvis.py`.
4. Add a test to `tests/test_router.py` (and to `tests/test_agent.py` when the
   agent is involved).

## Configuration reference

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `JARVIS_MODEL` | `qwen2.5:1.5b` | Ollama model used by the brain |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama server address |
| `JARVIS_WAKE_WORD` | `jarvis` | Word that starts a conversation |
| `JARVIS_NAME` | `JARVIS` | Assistant name used in replies |
| `JARVIS_USER_TITLE` | `bro` | How JARVIS addresses you |
| `JARVIS_LANGUAGE` | `en-US` | Speech recognition language |
| `JARVIS_LISTEN_TIMEOUT` | `5` | Seconds to wait for speech |
| `JARVIS_PHRASE_TIME_LIMIT` | `8` | Maximum seconds per phrase |
| `JARVIS_SPEECH_RATE` | `175` | Words per minute |
| `JARVIS_MAX_HISTORY` | `10` | Messages kept in the AI context |
| `JARVIS_THINKING` | `true` | Speak a filler line before slow actions |
| `JARVIS_THINKING_PHRASES` | `One moment, {title}.\|Let me think, {title}.` | Pipe separated filler lines (`{title}` = `JARVIS_USER_TITLE`) |
| `JARVIS_MEMORY_FILE` | `memory.json` | Where memories are stored |
| `JARVIS_BROWSER_CHANNEL` | `chrome` | Playwright browser channel |
| `JARVIS_BROWSER_HEADLESS` | `false` | Run the browser without a window |
| `JARVIS_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `JARVIS_LOG_TO_FILE` | `false` | Also write `logs/jarvis.log` |

## Testing strategy

* `unittest` only - no extra dependencies, runs with `python -m unittest`.
* Anything external is mocked: subprocess, `webbrowser`, Playwright, Ollama,
  the speaker and the microphone.
* The memory tests write to a temporary directory, never to `memory.json`.