# OpenCode Adapter Guide

## Overview

OpenCode agents look for skills in `~/.opencode/skills/` and global instructions in `~/.opencode/AGENTS.md`.

## Installation

Run the unified installer with the `opencode` target:

```bash
./install.sh --target opencode
```

This will:
1. Deploy `SKILL.md` to `~/.opencode/skills/anti-ai-copywriting/SKILL.md`.
2. Idempotently insert bounded rule markers (`<!-- BEGIN anti-ai-copywriting -->`) into `~/.opencode/AGENTS.md`.

## Verification

Run OpenCode and request text generation or polishing. The agent will silently adhere to natural prose rules and eliminate AI tropes.
