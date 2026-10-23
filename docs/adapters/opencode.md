# OpenCode Adapter Guide

[English](opencode.md) | [简体中文](opencode.zh-CN.md)

## Overview

OpenCode agents look for skills in `~/.opencode/skills/` and global instructions in `~/.opencode/AGENTS.md` (or workspace `AGENTS.md`).

---

## 1. Installation

Run the unified installer with the `opencode` target:

```bash
# Global user installation
./install.sh --target opencode --lang en

# Workspace installation
./install.sh --target opencode --dest /path/to/project --lang en
```

This will:
1. Deploy `SKILL.md` to `~/.opencode/skills/anti-ai-copywriting/SKILL.md` (or workspace).
2. Idempotently insert bounded rule markers (`<!-- BEGIN anti-ai-copywriting -->`) into `AGENTS.md` with explicit `<auto_trigger>` directives.
3. Record target in `~/.local/share/anti-ai-copywriting/install-manifest.json`.

---

## 2. OpenCode Verification Plugin (Harness² c8)

To enforce zero-tolerance AI clichés during agent execution, load `plugin/anti-ai-copywriting.ts` in your OpenCode configuration:

```typescript
import antiAiPlugin from "./plugin/anti-ai-copywriting";

export default {
  plugins: [antiAiPlugin],
};
```

The plugin intercepts `postToolExecution` events for all `.md`, `.markdown`, and `.txt` file writes, executing `anti-ai-lint --format agent` and automatically feeding structured revision requests back into the agent turn if AI buzzwords are found.

---

## 3. Uninstallation

```bash
./uninstall.sh --target opencode
```

---

## Trademark & Non-Affiliation Disclaimer

OpenCode is an open-source AI agent runtime. `anti-ai-copywriting` is an independent project and is not affiliated with or sponsored by upstream OpenCode maintainers.
