# Legacy scripts

These files are the earlier, single-file versions of JARVIS. They are kept for
reference only - the maintained assistant lives in the project root
(`python jarvis.py`).

| File | What it is |
| ---- | ---------- |
| `main.py` | First prototype: speech recognition plus `pyttsx3` speech output, no AI. |
| `jarvis_ai.py` | Adds the local Ollama brain and simple computer control. |
| `jarvis_backup.py` | Larger backup version with its own memory file handling. |
| `local_brain.py` | Ten line script that checks whether Ollama answers. |
| `brain.py` | Experiment using the OpenAI API (needs `OPENAI_API_KEY`). |

They still run (`python legacy/jarvis_ai.py`), but they duplicate logic that is
now split into the `brain`, `agent`, `tools`, `voice`, `memory` and `commands`
packages, so new work should not go here.
