# anti-ai-copywriting

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**Bilingual Natural Prose & Academic Pro-Voice Engine for AI Coding Agents and LLMs.**

Eliminates translationese, AI clichés, pseudo-academic buzzwords, formulaic emotional parallelism, and defensive hedging across both Chinese and English prose.

---

## Key Features

- **Genre-Specific Tone Shaping**: Anchors tone for academic papers, grant proposals, tech columns, social media copy, and business memos.
- **De-AI Lexicon & Tropes**: Eliminates buzzwords (*delve into*, *tapestry of*, *testament to*, *realm*, *navigating complexities*, 赋能, 抓手, 闭环, 底层逻辑, 颗粒度).
- **Controlled Plain Layer**: Hard constraints inspired by simplified technical English for code annotations and non-specialist briefings.
- **Academic Presentation Standards**: Structured tables, figure legends, and APA/JARS compliant statistical notation.
- **Deterministic Zero-Dependency Linter (`anti-ai-lint`)**: Command-line tool with zero third-party dependencies, callable directly in CI or agent verification gates (`verifyCommand`).

---

## Installation

### 1. Agent Skill & Rules Integration

Install into your preferred environment using the unified installer:

```bash
# For ZCode:
./install.sh --target zcode --lang zh

# For Claude Code CLI:
./install.sh --target claude --lang en

# For Codex CLI / OpenCode:
./install.sh --target codex
./install.sh --target opencode

# For Generic agents (Cursor, Windsurf, WorkBuddy, Cline):
./install.sh --target generic --dest /path/to/project
```

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

## Linter Usage

```bash
# Check single file
anti-ai-lint paper.md

# Check directory with custom threshold and JSON output
anti-ai-lint docs/ --max-score 6.0 --format json

# Pipe from standard input
cat draft.txt | anti-ai-lint --max-score 5.0
```

When violations exceed `--max-score`, `anti-ai-lint` exits with non-zero code `1`, making it ideal for CI workflows or agent verification gates (`verifyCommand`).

---

## Regression Test Suite

Run the built-in test suite covering 6 genres (Academic, Grant Proposal, Science Column, Social Media, Business Memo, and English Academic):

```bash
python3 -m unittest discover -s tests
```

---

## Credits & Acknowledgments

- The Controlled Plain Layer draws general conceptual inspiration from ASD-STE100 simplified technical documentation principles (ASD holds copyright over the specification; all rules in this repository were authored independently).

---

## Disclaimer

This project is an independent open-source contribution and is not affiliated with, sponsored by, or endorsed by Google LLC or Anthropic. All brand names belong to their respective holders.

---

## License

[MIT](LICENSE) © 2026 Liangliang Chen
