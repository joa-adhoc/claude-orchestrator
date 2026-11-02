#!/usr/bin/env bash
# Install for the current user: the skill into ~/.claude/skills and the agent into ~/.claude/agents.
# The orch-* tools stay in bin/. Safe to run again.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.claude/skills" "$HOME/.claude/agents"
chmod +x "$root"/bin/*

ln -sfn "$root" "$HOME/.claude/skills/claude-orchestrator"
ln -sfn "$root/agents/claude-orchestrator.md" "$HOME/.claude/agents/claude-orchestrator.md"

echo "installed from $root: in \`claude agents\`, dispatch \`@claude-orchestrator <request>\` and pin it with Ctrl+T"
