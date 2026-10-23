# Claude Code Adapter Guide

## Overview

For Claude Code CLI, `anti-ai-copywriting` installs into `~/.claude/` or workspace `CLAUDE.md`.

## Automatic Installation

```bash
./install.sh --target claude --lang en
```

This injects marked blocks into `~/.claude/CLAUDE.md` and copies `SKILL.md` into `~/.claude/skills/anti-ai-copywriting/SKILL.md`.

## Quality Gate in CI

In your GitHub Actions workflow:
```yaml
- name: Lint Copywriting
  run: python3 -m anti_ai_lint docs/ --max-score 8.0
```
