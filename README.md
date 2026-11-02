# claude-orchestrator

A coordinator session for Claude Code that starts one background session per task
(`claude --bg`), named after the Odoo task and always colored: by topic, or the least-used color
for a lone session. The user sees them all in `claude agents` and talks to any of them directly
there. No terminal tabs, no window focus, no simulated keys: it uses only Claude Code's background
sessions and agent view.

```
claude-orchestrator/
├── SKILL.md              rules and cases for the coordinator
├── bin/
│   ├── orch-new          one background session: name, topic color, first prompt
│   ├── orch-list         sessions grouped by topic
│   └── orch-find         find older sessions by task number or words
└── install.sh
```

## Install

```bash
~/.agents/skills/claude-orchestrator/install.sh
```

## Use

Open `claude agents` and dispatch the coordinator like any session, starting with the skill:

```
/claude-orchestrator una sesión por subtarea abierta de la 78647
```

Pin it with `Ctrl+T` so it stays on top, and rename it with `Ctrl+R`. The sessions it opens show
up in the same list.

A session is named `<topic> › <task id> <name>`. Every session has a color, and sessions of one
topic share it. It is set with `/color` as the first message; `orch-new` then stops and resumes
the session with the task prompt, so the prompt arrives as the user's message. Topic colors are
kept in
`~/.local/state/claude-orchestrator/topics.json`.

Requires Claude Code with background sessions and agent view (2.1.139 or later), `python3`.
