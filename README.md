# anti-ai-copywriting

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**Bilingual Natural Prose & Academic Pro-Voice Engine for AI Coding Agents and LLMs.**

Eliminates translationese, AI clichés, pseudo-academic buzzwords, formulaic emotional parallelism, and defensive hedging across both Chinese and English prose.

---

## Key Features

- **Cross-Platform Compatibility**: Full, first-class adapter support for Codex, Claude Code, DeepSeek, OpenCode, WorkBuddy, and common agents (Cursor, Windsurf, Cline, Aider, Antigravity, Harness², ZCode).
- **Genre-Specific Tone Shaping (`--genre general|academic|plain`)**:
  - `academic`: Strict de-hedging, given-new flow, APA/JARS compliant statistics, and zero table formulas.
  - `plain`: Controlled plain layer inspired by simplified technical English (Chinese $\le 30$ chars/sentence, English $\le 25$ words/sentence, zero vague quantifiers).
  - `general`: Comprehensive cross-genre prose polishing.
- **De-AI Lexicon & Formulaic Templates**: Eliminates buzzwords (`delve into`, `tapestry of`, `testament to`, `realm`, `navigating complexities`, `赋能`, `抓手`, `闭环`, `底层逻辑`, `颗粒度`) and templates (`随着...飞速发展`, `不仅是...更是...`).
- **Actionable Remediation**: Every detected violation provides a concrete replacement suggestion.
- **Harness² Architectural Integrations (c1..c8)**:
  - **c8 In-Loop Verification Hook**: `hooks/hooks.json` and `.codex/hooks.json` automatically lint drafted prose immediately after file write tool calls.
  - **c8 OpenCode Plugin**: `plugin/anti-ai-copywriting.ts` intercepts tool execution to feed structured feedback back into the agent turn.
  - **c5 Dedicated Copy-Editing Subagent**: `sub_agents/copywriting-editor/AGENT.md` provides a specialist role for autonomous de-AI editing.
  - **c6/c1 Autotrigger Contracts**: Explicit `<auto_trigger>` directives in rules snippets ensure agents proactively load the skill.
- **Deterministic Zero-Dependency Linter (`anti-ai-lint`)**: Command-line tool supporting text, JSON, hook, and agent formats, plus normalized density scoring per 1,000 units.

---

## Installation & Deployment

### 1. Agent Skill & Rules Integration

Install into your target environment using the unified installer with multi-target tracking and language selection (`--lang en|zh`):

```bash
# Codex:
./install.sh --target codex --lang en

# Claude Code CLI:
./install.sh --target claude --lang en

# DeepSeek (CLI / API agents):
./install.sh --target deepseek --lang en

# OpenCode:
./install.sh --target opencode --lang en

# WorkBuddy:
./install.sh --target workbuddy --lang zh

# Cursor (project repository):
./install.sh --target cursor --dest /path/to/project --lang en

# Windsurf (project repository):
./install.sh --target windsurf --dest /path/to/project --lang en

# Cline / Aider / Antigravity:
./install.sh --target cline --dest /path/to/project --lang en
./install.sh --target aider --dest /path/to/project --lang en
./install.sh --target antigravity --lang en

# ZCode:
./install.sh --target zcode --lang zh

# Generic workspace destination:
./install.sh --target generic --dest /path/to/project --lang en
```

For detailed guides and architecture walkthroughs, see [Agent Adapters & Integration Guides](docs/adapters/README.md).

---

### 2. Standalone Python Linter (`anti-ai-lint`)

Install locally or in your virtual environment:

```bash
pip install ./lint
```

Or run directly without installation:

```bash
python3 -m anti_ai_lint /path/to/document.md --max-score 8.0
```

---

## Linter Usage & Modes

```bash
# Check single file with default settings
anti-ai-lint paper.md

# Academic mode with hook format for pre-commit / tool loops
anti-ai-lint paper.md --genre academic --format hook --max-score 8.0

# Controlled plain layer validation
anti-ai-lint guide.md --genre plain --format agent

# Normalized score constraint (penalty per 1,000 words/units)
anti-ai-lint docs/ --max-normalized-score 25.0 --format json
```

### Output Formats (`--format`)

- `text`: Human-readable summary with exact line/column locations and fix suggestions.
- `json`: Machine-readable structured AST and metrics report.
- `hook`: Compact single-line / multi-line summary designed for git pre-commit and Harness² in-loop hooks.
- `agent`: Specially formatted `<anti-ai-lint-feedback>` XML/markdown payload for LLM reflector loops.

---

## Uninstallation

Cleanly restore backups and remove marker blocks without touching other user configurations:

```bash
# Uninstall a specific target (global or project-specific)
./uninstall.sh --target codex
./uninstall.sh --target cursor --dest /path/to/project
./uninstall.sh --dest /path/to/project

# Uninstall all registered targets
./uninstall.sh --all
```

---

## Regression Test Suite

Run the full test suite (covering 6 genres, code blocks, sentence splitting, genre modes, normalized scores, formats, and multi-target installer integration):

```bash
python3 -m unittest discover -s tests
```

---

## Credits & Acknowledgments

- **ASD-STE100**: The Controlled Plain Layer draws general conceptual inspiration from ASD-STE100 simplified technical documentation principles. ASD holds copyright over the specification (ASD-STE100); all rules and detection patterns in this repository were authored independently.
- **Google Research Harness²**: Integration patterns draw on Google Research Harness² agent harness architectures (c1 specification contracts, c5 subagents, c6 autotriggers, and c8 in-loop hooks).

---

## Trademark & Non-Affiliation Notice

All product names, logos, brands, trademarks, and registered trademarks mentioned in this repository (including Anthropic, Claude, Claude Code, OpenAI, Codex, DeepSeek, Google, Cursor, Windsurf, Codeium, Cline, Aider, WorkBuddy, and others) are property of their respective owners. Their use does not imply any affiliation with, endorsement by, or sponsorship by their respective holders. All integrations and adapter instructions are independent, community-developed open-source compatibility layers.

---

## License

[MIT](LICENSE) © 2026 Liangliang Chen
