# Engineering Team

A multi-agent system that takes high-level requirements for a software
project and produces a working backend, a Gradio frontend, and unit tests.

Built on the OpenAI Agents SDK and free OpenRouter models.

## What it does

Given a paragraph of natural-language requirements, four agents collaborate
to deliver a small working application:

1. **Engineering Lead** — turns the requirements into a detailed design
   (modules, classes, function signatures) and assigns work.
2. **Backend Engineer** — writes the backend Python code in a shared sandbox.
3. **Frontend Engineer** — writes a Gradio UI plus a small validation script.
4. **Test Engineer** — writes unit tests with `unittest`, runs them in the
   sandbox, and fixes any defects.

The four agents run sequentially. Each agent sees the design plus the
original requirements, and writes its files into the same sandbox directory.

## How it works

All file operations go through four function tools backed by Docker:

| Tool | What it does |
|---|---|
| `list_sandbox_files` | Lists files in the sandbox |
| `read_sandbox_file` | Reads a file's contents |
| `write_sandbox_file` | Writes/overwrites a file |
| `run_sandbox_python` | Runs a Python file inside `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` |

Before each run the sandbox is reset (`uv init --bare` + `uv add gradio`).
Every tool call is printed to the terminal so you can follow what each agent
is doing in real time.

## Prerequisites

- **Python 3.10 – 3.13**
- **Docker** running locally — used to execute generated code in an isolated
  container.
- **uv** on PATH — used to set up the sandbox project.
- An **OpenRouter API key** — create a free one at
  https://openrouter.ai/setting/keys.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -e .
```

Create a `.env` file in the project root (see `.env.example`):

```
OPENROUTER_API_KEY=sk-or-v1-...
DEFAULT_MODEL_NAME=nvidia/nemotron-3-ultra-550b-a55b:free
```

## Run

```bash
python -m engineering_team.main
```

The default requirements (a trading simulation account manager) are embedded
in `src/engineering_team/main.py`. Edit that string to build something else.

While the run is in progress the terminal shows:

- when the sandbox is initialized,
- which agent is currently working,
- every tool call (file written, file read, file executed, with sizes and
  exit codes),
- the final output of each agent.

Generated files land in `src/sandbox/` and the final outputs of each agent
are printed to the console.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPENROUTER_API_KEY` | (required) | OpenRouter API key |
| `DEFAULT_MODEL_NAME` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Model used by every agent |

To use a different free model (for example
`meta-llama/llama-3.3-70b-instruct:free`), change `DEFAULT_MODEL_NAME` in
`.env`.

## Notes

- The free model is slow. A full run typically takes 10–30 minutes.
- If you hit a 429, the daily quota for that free model is exhausted — wait
  or switch to another free model.
- Tracing is disabled because the provider is not OpenAI.
