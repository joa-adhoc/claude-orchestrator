#!/usr/bin/env bash
# Install for the current user: link the skill into ~/.claude/skills. The orch-* tools stay in bin/.
# Safe to run again.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.claude/skills"
chmod +x "$root"/bin/*
ln -sfn "$root" "$HOME/.claude/skills/claude-orchestrator"

echo "installed from $root: in \`claude agents\`, dispatch \`/claude-orchestrator <request>\` and pin it with Ctrl+T"
