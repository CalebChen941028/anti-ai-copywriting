# anti-ai-copywriting

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![Version: 0.4.0](https://img.shields.io/badge/version-0.4.0-green.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**Bilingual Natural Prose & Academic Pro-Voice Engine for AI Coding Agents and LLM Workflows.**

Eliminates translationese, AI clichés, pseudo-academic buzzwords, formulaic emotional parallelism, and defensive hedging across both Chinese and English prose.

---

## 1. System Positioning & Paradigm Comparison

Most existing AI text tools operate as **post-hoc punitive detectors** or **destructive black-box humanizers**. In contrast, `anti-ai-copywriting` provides a **proactive, deterministic, and terminology-preserving** engine.

| Dimension | Reactive Detectors<br>*(Turnitin, GPTZero, Copyleaks)* | Black-Box Humanizers<br>*(Undetectable AI, HIX Bypass)* | `anti-ai-copywriting`<br>*(This Project)* |
| :--- | :--- | :--- | :--- |
| **Intervention Point** | Post-hoc assessment; flags submissions after drafting | Blind post-generation rewrite | **Proactive prior conditioning** (`<auto_trigger>`) + **In-loop deterministic gating** |
| **Terminology & Rigor** | N/A (assessment only) | Destroys domain terms and causal links via naive synonym swapping | **Preserves strict terminology discipline** (e.g. Mendelian randomization, ecological validity) |
| **Statistical Cadence** | Black-box proprietary perplexity/burstiness | Induces ungrammatical anomalies | **Pure stdlib Burstiness CV** ($CV_{len} \ge 0.28$) & **MATTR** (window 50) |
| **Lexical Empirical Basis** | Opaque heuristic models | Arbitrary substitution lists | **Nature 2024 PubMed excess vocabulary** & **朱德熙形式动词闭集 (LVC)** |
| **Developer Ecosystem** | Web dashboards / paid API quotas | Web forms & subscription paywalls | **Zero-dependency CLI**, **native MCP server**, **GitHub Action**, & **DPO exporter** |

---

## 2. Key Capabilities & AI Engineering Architecture

- **Information-Theoretic Cadence & Rhythm (Burstiness & UID)**:
  - Measures sentence length variation via the Coefficient of Variation ($CV_{len} = \sigma / \mu$).
  - Automatically flags `rhythmic_monotony` (penalty 3.5) if $CV_{len} < 0.28$ across qualifying sentences ($\ge 6$), eliminating the uniform 20-word AI drone.
  - Implements Moving-Average Type-Token Ratio (MATTR) with a 50-token sliding window for unbiased lexical richness tracking.
- **Kobak et al. 2024 Nature/Science Advances PubMed Excess Vocabulary**:
  - Calibrated against 14M+ scientific abstracts with tiered log-odds penalties:
    - **Tier S (5.0)**: `delve`, `delve into`, `delving into`, `tapestry of`, `intricate tapestry`, `meticulously`, `testament to`.
    - **Tier A (3.5)**: `realm`, `realm of`, `intricate`, `pivotal role`, `pivotal`, `beacon of`, `commendable`, `foster`, `navigating complexities`, `unwavering`.
    - **Tier B (2.0)**: `comprehensive`, `robust`, `leverage`, `utilize`, `seamless integration`, `seamless`, `seamlessly`, `multifaceted`, `myriad`, `revolutionize`.
- **Chinese Light Verb Constructions (LVC / 文字义肢) Closed Set**:
  - Closed set of light verbs (`进行|开展|展开|作出|予以|给以|加以|具有|得到|受到|作|做|致以`) paired with 16 nominalized action targets (`分析|探讨|调研|考察|评估|审校|整改|梳理|阐述|测查|优化|迭代|部署|排查|总结|研究`).
  - Provides actionable de-nominalization rewrite guidelines.
- **Model Context Protocol (MCP) Server**:
  - Zero-dependency JSON-RPC 2.0 stdio MCP server (`anti-ai-mcp` or `python3 -m anti_ai_lint.mcp_server`).
  - Native tools for Cursor, Claude Code, Windsurf, Zed, Cline: `lint_prose`, `remediate_violation`, and `get_style_contract`.
- **Modern AI Engineering Toolchain**:
  - Official GitHub Action (`action.yml`) with PR workflow annotations (`::warning` / `::error`).
  - Pre-commit configuration (`.pre-commit-hooks.yaml`).
  - Stanford DSPy prompt optimization runner script (`scripts/dspy_optimizer.py`).
  - DPO / SimPO preference dataset exporter (`scripts/export_dpo_pairs.py`) outputting HuggingFace TRL triplets, ChatML, and ShareGPT formats.
- **Multi-Platform Agent Support**:
  - Complete, first-class adapter support for **Codex**, **Claude Code**, **DeepSeek**, **OpenCode**, **WorkBuddy**, **Cursor**, **Windsurf**, **Cline**, **Aider**, **Antigravity**, **Harness²**, and **ZCode**.

---

## 3. Installation & Deployment

### 3.1 Agent Skill & Rules Integration

Install into your target platform using the unified installer with language selection (`--lang en|zh`):

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

For detailed guides, see [Agent Adapters & Integration Guides](docs/adapters/README.md).

---

### 3.2 Standalone Python Linter (`anti-ai-lint`)

Install locally or in your virtual environment:

```bash
pip install ./lint
```

Or run directly without installation:

```bash
python3 -m anti_ai_lint /path/to/document.md --max-score 8.0
```

---

### 3.3 Model Context Protocol (MCP) Server

To run the MCP server for Cursor, Windsurf, Claude Code, or Zed:

```bash
# Run stdio server directly:
python3 -m anti_ai_lint.mcp_server

# Or via installed console script:
anti-ai-mcp
```

Add to `.cursor/mcp.json` or Cline `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "anti-ai-copywriting": {
      "command": "python3",
      "args": ["-m", "anti_ai_lint.mcp_server"]
    }
  }
}
```

---

### 3.4 GitHub Action & Pre-Commit Hook

**GitHub Actions Workflow (`.github/workflows/prose-lint.yml`)**:

```yaml
name: Natural Prose Linter
on: [push, pull_request]

jobs:
  lint-prose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./action.yml
        with:
          paths: 'docs/'
          genre: 'academic'
          max-score: '10.0'
```

**Pre-commit Hook (`.pre-commit-config.yaml`)**:

```yaml
repos:
  - repo: https://github.com/CalebChen941028/anti-ai-copywriting
    rev: v0.4.0
    hooks:
      - id: anti-ai-lint
        args: ["--format", "hook", "--genre", "general"]
```

---

## 4. Linter Usage & Output Modes

```bash
# General mode
anti-ai-lint paper.md

# Academic mode with hook format for pre-commit loops
anti-ai-lint paper.md --genre academic --format hook --max-score 8.0

# Controlled plain layer validation
anti-ai-lint guide.md --genre plain --format agent

# GitHub Actions format (produces workflow annotations)
anti-ai-lint docs/ --format github
```

### Output Formats (`--format`)

- `text`: Human-readable summary with exact line/column locations, cadence metrics, and fix suggestions.
- `json`: Machine-readable structured AST and metrics report.
- `hook`: Compact single-line / multi-line summary designed for git pre-commit and Harness² in-loop hooks.
- `agent`: Specially formatted `<anti-ai-lint-feedback>` XML payload for LLM reflector loops.
- `github`: Native GitHub Actions Workflow Commands (`::warning` and `::error`).

---

## 5. Academic References & Citations

The methodologies and metrics implemented in `anti-ai-copywriting` are grounded in the following academic research:

1. **Kobak, D., González-Márquez, R., Horvát, E. Á., & Schulz, C. (2024)**. Monitoring the footprint of large language models in scientific writing. *Nature/Science Advances* (arXiv:2406.07016).
2. **Meister, C., Leszczynski, M., Aji, A. F., & Cotterell, R. (2021)**. Uniform information density and language generation. In *Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.
3. **Mitchell, E., Yoon, J., Miao, N., Finn, C., & Manning, C. D. (2023)**. DetectGPT: Zero-shot machine-generated text detection using probability curvature. In *International Conference on Learning Representations (ICLR 2023)*.
4. **Hans, A., Schwarzschild, A., Cherepanova, V., Bansal, H., Saha, S., Jain, A., ... & Goldblum, M. (2024)**. Spotting LLMs with Binoculars: Zero-shot detection of machine-generated text. In *International Conference on Learning Representations (ICLR 2024)*.
5. **Li, W., et al. (2024)**. RAID: A shared benchmark for robust evaluation of machine-generated text detectors. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL 2024)*.
6. **Zhu, D. X. (朱德熙). (1982)**. *Grammar Notes (语法讲义)*. Commercial Press. (Regarding Chinese Light Verb Constructions and Nominalization).
7. **ASD-STE100 Specification**. Aerospace, Security and Defence Industries Association of Europe (ASD). Simplified Technical English Specification.
8. **Google Research (2024)**. Harness²: Agentic Evaluation, Specification, and Guardrail Protocols.

---

## 6. Uninstallation

Cleanly restore backups and remove marker blocks without touching other configurations:

```bash
# Uninstall a specific target
./uninstall.sh --target codex
./uninstall.sh --target cursor --dest /path/to/project

# Uninstall all registered targets
./uninstall.sh --all
```

---

## 7. Trademark & Non-Affiliation Notice

All product names, logos, brands, trademarks, and registered trademarks mentioned in this repository (including Anthropic, Claude, Claude Code, OpenAI, ChatGPT, Codex, DeepSeek, Google, Gemini, Antigravity, Cursor, Windsurf, Codeium, Cline, Aider, WorkBuddy, and others) are property of their respective owners. Their use in this documentation does not imply any affiliation with, endorsement by, or sponsorship by their respective holders. All integrations and adapter instructions are independent, community-developed open-source compatibility layers.

---

## 8. License

[MIT](LICENSE) © 2026 Liangliang Chen
