# DuoTalk 🎭

Multi‑agent voice conversations platform.

— Create rich, persona‑driven discussions (debate, roundtable, panel, interview, chat) with 1–10 agents. Audio YouTube summarization. Powered by LiveKit and Google Gemini.

## Install

```powershell
# create virtual env ,then
pip install duotalk
or
uv add duotalk
```

Environment (PowerShell):

```powershell
$env:GOOGLE_API_KEY = "<your_gemini_api_key>"

# Optional extras
$env:LIVEKIT_API_KEY = "<key>"
$env:LIVEKIT_API_SECRET = "<secret>"
```

## 1‑minute quick start

```powershell
# 3‑agent roundtable
duotalk roundtable -t "future of AI" -a 3

# 2‑agent debate
duotalk debate -t "pineapple on pizza"

# YouTube summary (short, with voice off)
duotalk summarize -u "https://youtu.be/VIDEO" -s short --no-voice
```

## CLI at a glance

| Command | Purpose | Agents |
|---|---|---|
| roundtable | Multi‑perspective discussion | 3–10 |
| debate | Opposing viewpoints | 2 |
| panel | Expert panel | 3–10 |
| interview | Interview format | 2 |
| chat | Casual or guided chat | 1–10 |
| summarize | YouTube video summary | 1 |

Tip: add -n <turns>, -p <personas comma‑list>, --voice/--no-voice.

## Minimal examples

```powershell
# Larger roundtable (6 agents)
duotalk roundtable -t "climate tech" -a 6 -n 16

# Expert panel with custom personas
duotalk panel -t "AI safety" -a 5 -p "researcher,engineer,ethicist,founder,policy"

# Interview with roles
duotalk interview -t "ML careers" --interviewer recruiter --interviewee engineer -n 12
```

## Personas

Browse available personas:

```powershell
duotalk personas
```

Examples: optimist, skeptic, pragmatist, theorist, analyst, educator, engineer, researcher, strategist, creative.

## Help

```powershell
duotalk --help
duotalk roundtable --help
duotalk summarize --help
```

## Links

- Docs/Issues: https://github.com/AbhyudayPatel/Duotalk-package
- License: MIT
