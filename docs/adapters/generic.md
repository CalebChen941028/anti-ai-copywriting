# Generic & Common Agent Adapters Guide

[English](generic.md) | [简体中文](generic.zh-CN.md)

## Overview

This guide provides instructions for deploying `anti-ai-copywriting` across common coding assistants and autonomous agent frameworks, including **Cursor**, **Windsurf**, **Cline**, **Aider**, **Antigravity**, and custom LLM agent harnesses.

---

## 1. Supported Platforms & File Locations

| Tool / Framework | Target Flag | Generated Rules File | Local Skill Directory |
| :--- | :--- | :--- | :--- |
| **Cursor** | `--target cursor` | `.cursorrules` (or `.cursor/rules/*.mdc`) | `.cursor/skills/anti-ai-copywriting/` |
| **Windsurf** | `--target windsurf` | `.windsurfrules` | `.windsurf/skills/anti-ai-copywriting/` |
| **Cline** | `--target cline` | `.clinerules` | `~/.cline/skills/anti-ai-copywriting/` |
| **Aider** | `--target aider` | `CONVENTIONS.md` / `~/.aider.conventions.md` | `~/.aider/skills/anti-ai-copywriting/` |
| **Antigravity** | `--target antigravity`| `AGENTS.md` | `~/.antigravity/skills/anti-ai-copywriting/` |
| **Custom Agent** | `--target generic` | User-defined via `--dest` | User-defined via `--dest` |

---

## 2. Platform Installation Guides

### Cursor

#### Option A: Project `.cursorrules`
Install bounded rules into your repository root:
```bash
./install.sh --target cursor --dest /path/to/project --lang en
```
Cursor automatically includes `.cursorrules` in every agent turn.

#### Option B: Cursor MDC Rules
Place a markdown rule file at `.cursor/rules/anti-ai-copywriting.mdc`:
```bash
./install.sh --target cursor --dest /path/to/project/.cursor/rules/anti-ai.mdc --lang en
```

---

### Windsurf

Windsurf (Cascade) reads global and repository-level rules from `.windsurfrules`:
```bash
./install.sh --target windsurf --dest /path/to/project --lang en
```
Cascade will automatically follow the anti-AI phrasing and de-hedging guidelines during file edits and documentation generation.

---

### Cline

Install into your project or home directory:
```bash
# Project root
./install.sh --target cline --dest /path/to/project --lang en

# Global user directory
./install.sh --target cline --lang en
```
Cline reads `.clinerules` upon starting any workspace task.

---

### Aider

Aider supports loading external conventions files during interactive sessions:
```bash
# Install convention file into repository
./install.sh --target aider --dest /path/to/project --lang en

# Launch Aider referencing the conventions
aider --read CONVENTIONS.md
```

Alternatively, configure your `.aider.conf.yml`:
```yaml
read:
  - CONVENTIONS.md
```

---

### Antigravity

Antigravity multi-agent systems read global skill and agent contracts from `AGENTS.md`:
```bash
./install.sh --target antigravity --lang en
```

---

### Custom Agent / LLM Pipelines

For bespoke agent orchestrators (LangChain, LlamaIndex, AutoGen, CrewAI):
1. Install rules to a designated location:
   ```bash
   ./install.sh --target generic --dest /path/to/prompts --lang en
   ```
2. Read `AGENTS.snippet.en.md` (or `AGENTS.snippet.zh.md`) and inject it into your system prompt.

---

## 3. Automated Verification in CI / Git Pre-Commit

Regardless of which agent framework you use, enforce clean prose in your continuous integration pipeline:

```bash
# Verify entire documentation tree
python3 -m anti_ai_lint docs/ --max-score 8.0 --format text

# Check academic paper with normalized score cap
python3 -m anti_ai_lint paper.md --genre academic --max-normalized-score 20.0
```

---

## 4. Uninstallation

```bash
# Uninstall specific target
./uninstall.sh --target cursor
./uninstall.sh --target windsurf
./uninstall.sh --target cline
./uninstall.sh --target aider
./uninstall.sh --target antigravity
./uninstall.sh --target generic
```

---

## Trademark & Non-Affiliation Disclaimer

Cursor is a product of Anysphere, Inc. Windsurf is a product of Codeium. Cline and Aider are open-source projects. All trademarks, registered trademarks, and logos belong to their respective owners. `anti-ai-copywriting` is an independent open-source project and is not affiliated with, endorsed by, or sponsored by any of these entities.
