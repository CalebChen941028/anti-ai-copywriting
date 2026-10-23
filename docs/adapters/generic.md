# Codex CLI Adapter Guide

## Installation

```bash
./install.sh --target codex
```

Appends marked blocks to `~/.codex/AGENTS.md` and copies `SKILL.md` to `~/.codex/skills/anti-ai-copywriting/SKILL.md`.

---

# OpenCode Adapter Guide

## Installation

```bash
./install.sh --target opencode
```

Appends marked blocks to `~/.opencode/AGENTS.md` and copies `SKILL.md` to `~/.opencode/skills/anti-ai-copywriting/SKILL.md`.

---

# Generic Adapter Guide

## Usage

For Cursor, Cline, Windsurf, Aider, or custom agents:
```bash
./install.sh --target generic --dest /path/to/custom/rules/AGENTS.md
```
Or simply incorporate `rules/AGENTS.snippet.md` into your agent instructions.
