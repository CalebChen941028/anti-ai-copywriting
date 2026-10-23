# Codex Adapter Guide

## Overview

Codex CLI and autonomous code agents read instructions and guidelines from `AGENTS.md` in your repository root or home configuration directory (`~/.codex/AGENTS.md`).

## Installation

Run the unified installer specifying the `codex` target:

```bash
./install.sh --target codex
```

This will:
1. Copy `SKILL.md` to `~/.codex/skills/anti-ai-copywriting/SKILL.md`.
2. Inject bounded rules into `~/.codex/AGENTS.md`.

## Quality Gate Integration

In your CI or pre-commit workflow, you can add `anti-ai-lint` as an automated gate:

```bash
anti-ai-lint path/to/deliverable.md --max-score 8.0
```
