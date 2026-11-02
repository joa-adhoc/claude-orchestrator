---
name: orchestrator
description: Makes the current session a coordinator that starts one Claude Code background session per task (`claude --bg`), each named after its Odoo task and colored by topic, so the user sees them all in `claude agents` and talks to any of them directly. Covers one session, a list, one session per open subtask of an Odoo umbrella task, moving an existing session to the background, and summing up where they stand. Use when the user says "abrí una sesión para la 78420", "una sesión por subtarea de la 78564", "sesiones para estos PRs", "retomá la sesión de la 77768", "¿dónde estamos?", "qué sesiones hay", "coordiná estas tareas".
---

# Orchestrator

This session coordinates. The work happens in background sessions that the user opens and talks
to in `claude agents`: `↑`/`↓` move, `Space` peeks and replies, `Enter` attaches, `←` on an empty
prompt goes back to the list, `n:<text>` filters by name, `Ctrl+S` groups by state or folder,
`Ctrl+T` pins.

The coordinator itself is one more session in that list: the user dispatches it in `claude agents`
with `@orchestrator <request>` and pins it with `Ctrl+T`. If this session is not the
`orchestrator` agent, say that once and go on here if the user prefers.

## Tools

They live in `~/.agents/skills/orchestrator/bin/` and are not in the `PATH`: always call them
with that folder. `--help` prints the full usage.

```bash
B=~/.agents/skills/orchestrator/bin
$B/orch-new -t "78504 Codemode" "78726 Codemode v2: A/B" "<prompt>"   # one session, colored by topic
$B/orch-new "Revisar logs de Railway" "<prompt>"                       # no topic: no color
$B/orch-new --dry-run ...                                               # print what it would run
$B/orch-list [--all] [TEXT]                                             # sessions grouped by topic
$B/orch-find <number or words>                                          # find older sessions
claude logs <id> | claude stop <id> | claude rm <id>                    # read, stop, delete
```

## Rules for every session

- **Name:** `<task id> <Odoo name>` whenever there is a task; pass the full Odoo name, `orch-new`
  shortens it. Name it by the task even when the session is about a PR. Without a task, say what
  it does (`Revisar logs de Railway`).
- **Topic (`-t`):** what groups the sessions: the umbrella task (`78504 Codemode`) or what they
  have in common (`PRs en revisión`). Short: 1 to 3 words, the umbrella id first. Use the same
  topic text for every session of the group, also in later calls: it is how they share a color and
  how the user filters them (`n:78504`). A single session with no group has no topic.
- **Color:** comes from the topic; pass `-c` only when the user asks. Colors are red, blue, green,
  yellow, purple, orange, pink and cyan.
- **Folder (`-d`):** the repo the request names; otherwise this session's folder.
- **Prompt:** what the user asked for. For a task with no instruction:

  ```text
  Task https://www.adhoc.inc/odoo/project.task/<id> (<short name>). Read the task, its chatter, the related PRs and what other sessions already solved. Answer in 5 lines: where it stands, what is missing and what I have to decide. Do not change code or write to Odoo until I ask, and do not message other sessions.
  ```

  For a helpdesk ticket, use `helpdesk.ticket` in the link.
- **One at a time:** run `orch-new` once per session, one after the other, never in parallel: each
  start loads Claude and its MCP servers, and several at once can stall the machine.
- **Quota:** with more than 6 sessions, show the list and ask first. With fewer, show one line per
  session and open.
- **Messages:** never message another session or subscribe to its idle notice unless the user asks
  in this conversation. The prompt that `orch-new` passes is the user's first message, not a
  cross-session message.
- **Report:** one line per session with the id, name and color that `orch-new` printed, then:
  "Las ves con `claude agents`; filtrá con `n:<topic>`". If `orch-new` failed, quote its message.

## Cases

- **One task or ticket:** read its `name` with the Odoo MCP (`tuqui-adhoc`); one session.
- **A list (tasks, PRs):** one session per item, with a topic that says what they have in common.
- **Umbrella task:** read the umbrella (`project.task`, `id`, fields `id, name`) and its subtasks
  (`parent_id = <umbrella>`, fields `id, name, state`), loading first the task skill the
  `tuqui-adhoc` catalogue names. Leave out `state` in `1_done` or `1_canceled` and say which.
  Topic: `<umbrella id> <1 to 3 words>`. One session per open subtask.
- **Resume an older session:** `orch-find <number or words>`; take the first line if `match` is
  `title` or `first`, otherwise show the first 3 and ask. If its tab or terminal is still open,
  ask the user to close it first. Then `claude --bg --resume <session id>` from its `cwd` moves it
  to the background; it keeps its old name. A session already in `claude agents` needs nothing:
  the user opens it there.
- **Where things stand:** `orch-list`, then `claude logs <id>` only for the sessions the answer
  needs.
- **Done:** a task with `state` `1_done` or `1_canceled` in Odoo: propose `claude stop` and
  `claude rm` for its session; do it after the user agrees.

## Traps

- `claude agents --json` reports `status: idle` when a session finished its turn; its `state`
  field can still say `working`.
- `claude --bg --resume <id>` with any flag starts a copy with a new id: a background session
  keeps its saved options. Pass no flags when continuing one.
- `/color` takes only the colors above (no `magenta`). A session asked through a message to do
  something odd may refuse it as not coming from the user.
- Each session uses the subscription quota on its own.
