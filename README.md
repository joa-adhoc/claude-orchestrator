# orchestrator

A coordinator session for Claude Code that starts one background session per task
(`claude --bg`), named after the Odoo task and colored by topic. The user sees them all in
`claude agents` and talks to any of them directly there. No terminal tabs, no window focus, no
simulated keys: it uses only Claude Code's background sessions and agent view.

```
orchestrator/
├── SKILL.md              rules and cases for the coordinator
├── agents/orchestrator.md  the coordinator agent
├── bin/
│   ├── orchestrator      starts the coordinator in this terminal (the only one in PATH)
│   ├── orch-new          one background session: name, topic color, first prompt
│   ├── orch-list         sessions grouped by topic
│   └── orch-find         find older sessions by task number or words
└── install.sh
```

## Install

```bash
~/.agents/skills/orchestrator/install.sh
```

## Use

```bash
orchestrator        # the coordinator, here
claude agents       # all sessions, in another terminal or tab
```

A session is named `<topic> › <task id> <name>`. Sessions of one topic share a color, set with
`/color` as their first message; `orch-new` then stops and resumes the session with the task
prompt, so the prompt arrives as the user's message. Topic colors are kept in
`~/.local/state/orchestrator/topics.json`.

Requires Claude Code with background sessions and agent view (2.1.139 or later), `python3`.
