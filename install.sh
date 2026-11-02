#!/usr/bin/env bash
# Install for the current user: the skill into ~/.claude/skills, the agent into ~/.claude/agents and
# the `orchestrator` command into ~/.local/bin. The orch-* tools stay in bin/. Safe to run again.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/bin" "$HOME/.claude/skills" "$HOME/.claude/agents"
chmod +x "$root"/bin/*

ln -sfn "$root" "$HOME/.claude/skills/orchestrator"
ln -sfn "$root/agents/orchestrator.md" "$HOME/.claude/agents/orchestrator.md"
ln -sfn "$root/bin/orchestrator" "$HOME/.local/bin/orchestrator"

case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "warning: ~/.local/bin is not in PATH" ;; esac
echo "installed from $root: run \`orchestrator\` to start the coordinator here"
