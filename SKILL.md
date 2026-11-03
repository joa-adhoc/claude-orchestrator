---
name: claude-orchestrator
description: Makes the current session a coordinator that starts one Claude Code background session per task (`claude --bg`), each named after its Odoo task and always colored (by topic when it has one), so the user sees them all in `claude agents` and talks to any of them directly. Covers one session, a list, one session per open subtask of an Odoo umbrella task, resuming a session (renamed, colored and briefed from its task), and summing up where they stand. It never works on a task itself. Use when the user says "abrí una sesión para la 78420", "una sesión por subtarea de la 78564", "sesiones para estos PRs", "retomá la sesión de la 77768", "¿dónde estamos?", "qué sesiones hay", "coordiná estas tareas".
---

# Claude orchestrator

This session coordinates. The work happens in background sessions that the user opens and talks
to in `claude agents`: `↑`/`↓` move, `Space` peeks and replies, `Enter` attaches, `←` on an empty
prompt goes back to the list, `n:<text>` filters by name, `Ctrl+S` groups by state or folder,
`Ctrl+T` pins.

The coordinator itself is one more session in that list: the user dispatches it in `claude agents`
with `/claude-orchestrator <request>` and pins it with `Ctrl+T`. It also works from any session.

The first time the skill loads in a session, add one line at the end of your answer: "Para
encontrarme fácil en `claude agents`: `Ctrl+R` para llamarme `Orchestrator` y `Ctrl+T` para
fijarme arriba." Do not rename the session yourself: `/rename` is typed by the user, and editing
`~/.claude/jobs/<id>/state.json` makes the supervisor kill the session (tested).

## Your role while this skill is loaded

- **You never start a task in this session.** No code, no repos (no worktrees, branches, commits),
  no writes to Odoo (notes, stages, timesheets), no actions on GitHub (PRs, comments, reviews,
  approvals). You read what you need to name and brief a session, and you answer simple things:
  where sessions stand, links. Everything else goes to a session: a new one with `orch-new`, or the
  task's own session with `orch-resume`. If the user asks you to do it here, open the session and
  say so in one line.
- **Other sessions are not yours to talk to.** Never send a message to another session
  (`SendMessage`) or subscribe to its idle notice unless the user asks in this conversation. Two
  messages are the user's, not cross-session messages: the prompt that `orch-new` passes, and the
  first message that `orch-resume` passes when the user asks to resume a session (see Cases). A
  message from you is not the user's approval: push, merge and anything that reaches other people
  the user confirms in that session.
- **No memory of your own.** State lives in the sessions: name, topic, color and state come from
  Claude Code each time (`orch-list`, `claude logs`), never from a copy. The one exception is
  `~/.local/state/claude-orchestrator/state.md`: only what is in no session (the user's decisions
  not done yet, questions still open), one line each. Create it with the first such item, edit it
  with your file tools, and delete a line when it is resolved. `orch-list` prints it at the end:
  run `orch-list` when the skill loads.
- **Find pending work** when asked: with the `tuqui-adhoc` MCP, look in Odoo, Gmail or Slack for
  requests addressed to the user (reviews, assigned tasks) and propose which sessions to open.
- **Answer short:** what happened, what is missing, what the user decides, with numbered
  questions. Names may arrive dictated and garbled: interpret them (people by their initials in
  Odoo) before asking.

## Tools

They live in `~/.agents/skills/claude-orchestrator/bin/` and are not in the `PATH`: always call them
with that folder. `--help` prints the full usage.

```bash
B=~/.agents/skills/claude-orchestrator/bin
$B/orch-new -t "78504 Codemode" "78726 Codemode v2: A/B" "<prompt>"   # one session, colored by topic
$B/orch-new "Revisar logs de Railway" "<prompt>"                       # no topic: least-used color
$B/orch-new --dry-run ...                                               # print what it would run
$B/orch-resume <session id> -t "78504 Codemode" "78726 Codemode v2: A/B" "<message>"  # resume
$B/orch-list [--all] [TEXT]                                             # sessions by topic, colors, pending
$B/orch-find <number or words>                                          # find older sessions
claude logs <id> | claude stop <id> | claude rm <id>                    # read, stop, delete
```

## Rules for every session

- **Only through the tools:** open a session with `orch-new` and resume one with `orch-resume`.
  Never run `claude --bg` by hand: those two are the only paths that set the name and the color.
- **Name:** `<task id> <2 to 5 words>` that say what the task is about: the problem or the change,
  in the team's words. Write them yourself from the Odoo name, and from the description when the
  name is vague. Never only a product, area or client name (`Tuqui`, `Odoo`, `Companion`), and
  drop prefixes like `[Tuqui]` or `Tuqui:`. `orch-new` only cuts to fit 40 characters.
  - "Tuqui: catálogo para el partner (jjs)" → `12345 Catálogo para el partner`, not `12345 Tuqui`.
  - "[Bug] Error al borrar un workspace conectado por companion" →
    `12346 Borrar workspace con companion`.

  Name it by the task even when the session is about a PR. Without a task, say what it does
  (`Revisar logs de Railway`).
- **Topic (`-t`):** what groups the sessions: the umbrella task (`78504 Codemode`) or what they
  have in common (`PRs en revisión`). Short: 1 to 3 words, the umbrella id first, with the same
  care as the name: what the umbrella is about, not only a product name. Use the same
  topic text for every session of the group, also in later calls: it is how they share a color and
  how the user filters them (`n:78504`). A single session with no group has no topic. The topic is
  the part of the name before ` › `; a session renamed without it keeps the topic of its last name
  that had one, and `orch-list` marks it `[renamed]`.
- **Color:** every session has one. With a topic, it is the color its sessions already have
  (completed ones too); a new topic, or a session without one, gets the color least used by live
  sessions. Pass `-c` only when the user asks.
  Colors are red, blue, green, yellow, purple, orange, pink and cyan.
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
- **Report:** one line per session with the id, name and color that `orch-new` or `orch-resume`
  printed, then: "Las ves con `claude agents`; filtrá con `n:<topic>`". If a tool failed, quote its
  message.

## Cases

- **One task or ticket:** read its `name` with the Odoo MCP (`tuqui-adhoc`); one session.
- **A list (tasks, PRs):** one session per item, with a topic that says what they have in common.
- **Umbrella task:** read the umbrella (`project.task`, `id`, fields `id, name`) and its subtasks
  (`parent_id = <umbrella>`, fields `id, name, state`), loading first the task skill the
  `tuqui-adhoc` catalogue names. Leave out `state` in `1_done` or `1_canceled` and say which.
  Topic: `<umbrella id> <1 to 3 words>`. One session per open subtask.
- **Resume a session** (older, or already in `claude agents`):
  1. Find it: `orch-find <number or words>`; take the first line if `match` is `title` or `first`,
     otherwise show the first 3 and ask. A session in `claude agents` also takes its id from there.
  2. Read the task with the Odoo MCP (name, description, chatter) and its PRs (`gh pr view`,
     `gh pr checks`). Read only.
  3. Write the first message from what you read: where the task stands and what is next, with links.

     ```text
     Resuming task https://www.adhoc.inc/odoo/project.task/<id> (<short name>). Where it stands: <1 to 3 lines from the task, the chatter and the PRs, with links>. What is next: <1 or 2 lines>. Check this against the code and the PRs, tell me in 5 lines what changed, and wait for my OK before you change code or write to Odoo.
     ```

  4. Run `orch-resume <session id> [-t <topic>] "<task id> <name>" "<message>"`, with the same name
     and topic rules as a new session. It colors and renames the session, then sends the message.
  5. If it says the session is busy, tell the user and stop: never stop a busy session. If it says
     the session is open in a terminal, ask the user to close it and run it again.
- **Where things stand:** `orch-list`, then `claude logs <id>` only for the sessions the answer
  needs.
- **Done:** a task with `state` `1_done` or `1_canceled` in Odoo: propose `claude stop` and
  `claude rm` for its session; do it after the user agrees.

## Traps

- `claude agents --json` reports `status: idle` when a session finished its turn; its `state`
  field can still say `working`.
- `claude --bg --resume <id>` with any flag starts a copy with a new id: a background session
  keeps its saved options. Pass no flags when continuing one, so the name cannot go as `-n`.
- A resumed session whose background job is gone (after `claude rm`, or one that never ran in the
  background) comes back with no color and an automatic name. `/color` and `/rename` sent as the
  message of a resume both work: `orch-resume` sends them one resume each, `/color` first. Sent
  after `/rename`, `/color` overwrites the name in agent view.
- A new session writes its first `/color` to the transcript but often not to `state.json` (what
  agent view shows) until it restarts. `orch-new` restarts it with `/color` once more.
- `claude stop` on a session in state `done` leaves it `done`, not `stopped`: the tools check that
  the process is gone.
- `Workspace not trusted`: Claude Code has not trusted that folder yet. The user opens `claude` once
  there and accepts the prompt; the tools say so.
- A background id does not always match the start of its session id: `orch-resume` takes either.
- `/color` takes only the colors above (no `magenta`). A session asked through a message to do
  something odd may refuse it as not coming from the user.
- Each session uses the subscription quota on its own.
