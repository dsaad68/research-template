#!/usr/bin/env bash
# Symlink .apm/ primitives into .claude/ so Claude Code discovers them natively.
# Workaround for APM <=0.8.11, which does not yet deploy local `.apm/` content
# to `.claude/` during `apm install --target claude`. See microsoft/apm#94.
#
# Run from the repo root: `apm run sync-claude` (or `bash scripts/sync-claude.sh`).
# Safe to re-run — existing symlinks are refreshed in place.

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p .claude/skills .claude/agents

# Skills: .apm/skills/<name>/  ->  .claude/skills/<name>
for dir in .apm/skills/*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  ln -sfn "../../$dir" ".claude/skills/$name"
  echo "skill:  .claude/skills/$name -> $dir"
done

# Agents: .apm/agents/<name>.agent.md  ->  .claude/agents/<name>.md
for file in .apm/agents/*.agent.md; do
  [ -f "$file" ] || continue
  name=$(basename "$file" .agent.md)
  ln -sfn "../../$file" ".claude/agents/$name.md"
  echo "agent:  .claude/agents/$name.md -> $file"
done

echo "[+] Sync complete."
