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
│   ├── orch-resume       resume a session: name, color, first message
│   ├── orch-list         sessions by topic with their colors, then pending items
│   ├── orch-find         find older sessions by task number or words
│   └── orchlib.py        shared by the orch-* tools
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
not kept anywhere else: a topic's color is the one Claude Code saved for its sessions, so a topic
with no sessions left frees its color. The only file of the skill is
`~/.local/state/claude-orchestrator/state.md`, for what is in no session yet; `orch-list` prints it.

To resume a session, `orch-resume` does the same in steps, each one a stop and a resume:
`/color <color>`, `/rename <name>`, then a first message the coordinator writes from the task.
It does not stop a session that is busy.

Requires Claude Code with background sessions and agent view (2.1.139 or later), `python3`.
