# Claude Code Adapter Guide

[English](claude-code.md) | [简体中文](claude-code.zh-CN.md)

## Overview

Claude Code CLI reads project-level instructions from `CLAUDE.md` in your repository root, or global preferences from `~/.claude/CLAUDE.md`. Custom agent skills reside under `~/.claude/skills/`.

---

## 1. Automated Installation

Run the unified installer specifying the `claude` target:

```bash
# Global user installation
./install.sh --target claude --lang en

# Repository-local installation
./install.sh --target claude --dest /path/to/project --lang en
```

This command:
1. Installs `SKILL.md` into `~/.claude/skills/anti-ai-copywriting/SKILL.md` (or your project directory).
2. Injects bounded rule markers (`<!-- BEGIN anti-ai-copywriting v0.3.0 -->`) into `CLAUDE.md` with explicit `<auto_trigger>` directives.
3. Records all installed files in `~/.local/share/anti-ai-copywriting/install-manifest.json` for rollback.

---

## 2. In-Loop Subagent Delegation (Harness² c5 Paradigm)

When handling comprehensive prose revisions or academic drafting, Claude Code can delegate the editing task to the dedicated copywriting subagent defined in `sub_agents/copywriting-editor/AGENT.md`:

```markdown
Run the copywriting-editor subagent to review and polish docs/architecture.md:
- Apply strict academic tone
- Remove all passive nominalizations and AI tropes
- Verify with anti-ai-lint --max-score 5.0
```

---

## 3. Pre-Commit Hook & CI Quality Gate

### Git Pre-Commit Hook

Add a pre-commit check to prevent merging machine-sounding prose:

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit
git diff --cached --name-only --diff-filter=ACM | grep -E '\.(md|markdown|txt)$' | while read -r file; do
  if [ -f "$file" ]; then
    python3 -m anti_ai_lint "$file" --genre general --format hook --max-score 8.0 || exit 1
  fi
done
```

### GitHub Actions Workflow

In `.github/workflows/ci.yml`:

```yaml
- name: Lint Copywriting & Prose Quality
  run: |
    python3 -m anti_ai_lint docs/ README.md --max-score 8.0 --format text
```

---

## 4. Uninstallation

To restore original configurations and cleanly remove injected blocks:

```bash
./uninstall.sh --target claude
```

---

## Trademark & Non-Affiliation Disclaimer

Claude and Claude Code are trademarks of Anthropic PBC. `anti-ai-copywriting` is an independent open-source project and is not affiliated with, endorsed by, or sponsored by Anthropic PBC.
