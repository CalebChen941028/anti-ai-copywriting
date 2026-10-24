# ZCode Adapter Guide

[English](zcode.md) | [简体中文](zcode.zh-CN.md)

## Overview

In ZCode environments, `anti-ai-copywriting` operates as a global skill installed in `~/.zcode/skills/anti-ai-copywriting/` and injects bounded rules into `~/.zcode/AGENTS.md`.

---

## 1. Automated Installation

Run the unified installer specifying the `zcode` target:

```bash
# Global user installation
./install.sh --target zcode --lang en

# Workspace installation
./install.sh --target zcode --dest /path/to/project --lang en
```

This will:
1. Install `SKILL.md` to `~/.zcode/skills/anti-ai-copywriting/SKILL.md` (or workspace).
2. Inject bounded marker blocks (`<!-- BEGIN anti-ai-copywriting v0.6.0 -->`) into `AGENTS.md` with explicit `<auto_trigger>` directives.
3. Record installed files in `~/.local/share/anti-ai-copywriting/install-manifest.json` for clean rollback.

---

## 2. In-Loop Quality Gate

Run `anti-ai-lint` as part of your CI pipeline or pre-commit workflow:

```bash
python3 -m anti_ai_lint docs/ --max-score 8.0 --format text
```

---

## 3. Uninstallation

To cleanly remove all installed components:

```bash
./uninstall.sh --target zcode
```

---

## Trademark & Non-Affiliation Disclaimer

ZCode is an agent development platform. `anti-ai-copywriting` is an independent open-source project and is not affiliated with, endorsed by, or sponsored by ZCode or its parent entities.
