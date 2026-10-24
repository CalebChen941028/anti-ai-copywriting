# Aider Integration Guide (Anti-AI Copywriting & Natural Prose)

[English](aider.md) | [简体中文](aider.zh-CN.md)

This guide covers integrating `anti-ai-copywriting` with Aider pair-programming CLI using conventions files.

---

## 1. Quick Installation

Install for Aider:

```bash
./install.sh --target aider --dest /path/to/your/project --lang en
```

This injects anti-ai rules into `/path/to/your/project/CONVENTIONS.md` (or `~/.aider.conventions.md`) and installs `skills/anti-ai-copywriting/SKILL.md`.

---

## 2. Using with Aider

Pass conventions explicitly or let Aider load `CONVENTIONS.md` automatically:

```bash
aider --read CONVENTIONS.md
```

Run `anti-ai-lint` on drafted documents before committing.
