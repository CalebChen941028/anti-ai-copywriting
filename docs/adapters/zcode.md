# ZCode Adapter Guide

## Overview

In ZCode, `anti-ai-copywriting` operates as a global skill in `~/.zcode/skills/anti-ai-copywriting` and injects rules into `~/.zcode/AGENTS.md`.

## Automatic Installation

Run the unified installer:
```bash
./install.sh --target zcode --lang zh
```

This will:
1. Install `SKILL.md` to `~/.zcode/skills/anti-ai-copywriting/SKILL.md`.
2. Inject bounded marker blocks (`<!-- BEGIN anti-ai-copywriting v0.2.0 -->`) into `~/.zcode/AGENTS.md`.
3. Record installed files in `~/.local/share/anti-ai-copywriting/install-manifest.json` for clean rollback.

## Uninstallation

```bash
./uninstall.sh
```
