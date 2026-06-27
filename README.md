<div align="center">
  <img src="assets/logo.svg" width="128" alt="northh — personal thinking workspace">
  <h1 align="center">northh</h1>
  <p align="center">
    <strong>a personal thinking workspace</strong>
    <br>
    capture ideas · organize projects · explore domains · reflect daily
  </p>
  <p>
    <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.13%2B-262626?style=flat-square&logo=python&logoColor=f59e0b&labelColor=0d0d0d&color=262626" alt="Python 3.13+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-262626?style=flat-square&labelColor=0d0d0d&color=262626" alt="License MIT"></a>
    <a href="https://docs.astral.sh/uv/"><img src="https://img.shields.io/badge/uv-262626?style=flat-square&logo=uv&logoColor=f59e0b&labelColor=0d0d0d&color=262626" alt="uv"></a>
    <a href="https://textual.textualize.io"><img src="https://img.shields.io/badge/Textual-262626?style=flat-square&logo=textual&logoColor=f59e0b&labelColor=0d0d0d&color=262626" alt="Textual"></a>
    <a href="https://github.com/Dark-Knight499/northh"><img src="https://img.shields.io/badge/3★_on_GitHub-262626?style=flat-square&logo=github&logoColor=f59e0b&labelColor=0d0d0d&color=262626" alt="3★ on GitHub"></a>
  </p>
</div>

> the cost of losing an idea is higher than the cost of storing an unorganized one.

---

<img src=".github/demo.gif" width="100%" alt="northh demo — home, capture, ideas, projects, domains, journal, help">

---

## why

you have ideas all the time. in conversations, while reading, at 3am. you tell yourself you'll remember. you won't.

by the time you've picked the right folder, created the right file, figured out the right category — the thought is gone. northh flips it: **capture first, organize later.**

**ideas** are raw captures. a thought, an observation, a question — no structure, no ceremony. just a timestamp and a markdown file.

**projects** are structured explorations. when an idea gains momentum, it gets its own directory, its own entries. titles become filenames. things take shape over time.

**domains** are long-term learning spaces. machine learning, systems, mathematics — areas you return to across months and years, building understanding without a finish line.

**journal** is personal reflection. daily entries append to a date-stamped file, creating a timeline you can look back on. not notes for something — just you talking to your future self.

the boundary between them is intentionally fuzzy. an idea can become a project. a project can reveal a domain. you don't need to get it right upfront — you just need to get it down.

everything is markdown in `~/.northh/`. no database. no lock-in. your editor, your tools, your data.

---

## quick start

```bash
uv tool install northh
northh
```

or with pip:

```bash
pip install northh
northh
```

first run creates `~/.northh/` and opens the TUI. that's it.

> **Windows (PowerShell):** same commands. just make sure python 3.13+ is on your path.

---

## once you're in

| key | action |
|-----|--------|
| `Space` | capture whatever's on your mind |
| `I` | browse ideas |
| `P` | browse projects |
| `D` | browse domains |
| `J` | browse journal |
| `T` | today's journal entry |
| `N` | new entry (inside a browser) |
| `/` | filter entries |
| `Enter` / `O` | open in your editor |
| `Esc` | go back |
| `?` | help |
| `Q` | quit |

### CLI quick capture

```bash
northh idea "a startup idea about X"
northh project my-project "some initial thoughts"
northh domain machine-learning "notes on transformers"
northh journal "today I learned..."
```

### voice capture

```bash
northh idea --voice
northh idea --voice --lang hi   # hindi
```

speech-to-text powered by Whisper (runs locally, no cloud dependency).

---

## structure

### your data (`~/.northh/`)

```
~/.northh/
├── ideas/        # timestamped.md — raw capture
├── projects/     # project-name/entry.md — structured work
├── domains/      # domain-name/entry.md — learning
└── journal/      # YYYY-MM-DD.md — daily reflection
```

### the code

```
northh/
├── src/
│   ├── functions/    # core logic, listing, editor, stt, sketch
│   └── ui/
│       ├── app.py    # textual app shell + key bindings
│       └── screens/  # home, browser, capture, new entry, help
├── docs/
│   └── philosophy.md # design vision
├── tests/            # pytest suite (189 tests)
└── main.py           # entry point
```

---

## features

| | |
|---|---|
| **dual interface** | full TUI + CLI, same capabilities from both |
| **zero database** | plain markdown files you own — `~/.northh/`, no lock-in |
| **capture first** | one keystroke to capture, organize later |
| **voice notes** | local speech-to-text via Whisper, hindi support |
| **sketches** | excalidraw-based visual thinking, context-aware storage |
| **filtering** | live text filter across any browser |
| **editor integration** | open any entry in `$EDITOR` with one key |
| **markdown native** | every entry is a `.md` file — use any editor, any tool |

---

## development

```bash
git clone git@github.com:Dark-Knight499/northh.git
cd northh
uv sync
uv run python main.py     # launch TUI
uv run pytest              # run 189 tests
```

---

<div align="center">
  <a href="https://github.com/Dark-Knight499/northh"><strong>⭐ star on GitHub</strong></a>
  <br><br>
  <sub>MIT — go build something.</sub>
</div>
