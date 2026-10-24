# anti-ai-copywriting

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![Version: 0.5.0](https://img.shields.io/badge/version-0.5.0-green.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**A rulebook that guides AI to write native-sounding natural language, free of obvious AI tone, in Chinese and English. Built for AI coding agents and LLM workflows.**

It removes translationese, AI clichés, pseudo-academic buzzwords, formulaic emotional parallelism, and defensive hedging. It covers four tasks: drafting, polishing, translation, and review. Polishing and translation obey **information conservation** (nothing added, nothing dropped, assertion strength unchanged). Drafting can offer an optional **warm, detail-driven tone** that never invents facts.

---

## 1. System Positioning & Paradigm Comparison

Typical AI text tools fall into two categories: **post-hoc detectors** that score a finished text, and **rewriting "humanizers"** that paraphrase it. `anti-ai-copywriting` takes a third route: **proactive writing rules plus a deterministic in-loop gate**.

> [!NOTE]
> The table compares tool categories in general terms. It is not a benchmark of any named product, and no named product was tested.

| Dimension | Post-hoc detectors (category) | Rewriting humanizers (category) | `anti-ai-copywriting` |
| :--- | :--- | :--- | :--- |
| **Intervention point** | After drafting; scores a finished text | After generation; paraphrases it | **Before and during writing** (`<auto_trigger>` rules) plus an **in-loop deterministic gate** |
| **Facts and terminology** | Not applicable (assessment only) | Synonym swaps can alter terms and claims | **Information conservation** for polishing and translation, with a `--source` check on numbers, codes, and acronyms |
| **Rhythm** | Usually opaque scoring | Often unspecified | **Stdlib-only** sentence-length variation (`CV_len`) and **MATTR** (window 50), documented and inspectable |
| **Word lists** | Usually undisclosed | Usually undisclosed | **Open JSON word lists** informed by the excess-vocabulary literature and Chinese light-verb grammar |
| **Tone choice** | None | None | Optional **warm human-touch mode** for original drafting; never fabricates detail |
| **Developer ecosystem** | Web dashboards or paid APIs | Web forms or subscriptions | **Zero-dependency CLI**, **MCP server**, **GitHub Action**, **pre-commit hook**, **DPO exporter** |

---

## 2. Real Dual-Model Benchmark: GLM-5.3 & mimo-v2.6-flash (Solo Model vs. Model + Skill + Tool Gate)

> [!NOTE]
> For the comprehensive benchmark report, mathematical derivations, in-depth linguistic diagnoses across all 8 subjects, and CLI reproduction commands, please consult: **[Full Benchmark & Evaluation Report (docs/BENCHMARK_REPORT.md)](docs/BENCHMARK_REPORT.md)**.

> [!IMPORTANT]
> **Data provenance.** This table is measured output of real end-to-end inference on GLM-5.3 (evaluation date 2026-10-24) under a dual-blind protocol: "Solo Model (native generation)" vs. "Model + anti-ai-copywriting skill + anti-ai-lint deterministic gate (with one in-loop remediation pass)". Raw generations and the summary table are persisted under `tests/fixtures_glm5/` and reproducible via `python3 scripts/run_glm5_benchmark.py`. All benchmark cases, regression tests, and DPO alignment datasets throughout the repository are strictly grounded in genuine empirical model outputs; all legacy synthetic or mock test fixtures have been completely purged.

The 8 subjects (6 drafting genres + 2 information-conservation workflows) score as follows:

| Scenario / Corpus | Genre Mode | Solo Penalty | Model+Skill+Tool | Score Delta | Violations Count | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Academic Abstract** (`academic`) | Academic | 4.0 pts | **0.0 pts** | **-100.0%** | 1 -> **0** | ✅ -> **✅** |
| **Business Memo** (`business`) | General | 2.5 pts | **2.5 pts** | Flat (residual style) | 1 -> **1** (invented metrics -> 【待补】placeholders) | ✅ -> **✅** |
| **English Academic Paper** (`en_academic`) | Academic | 3.0 pts | **3.0 pts** | Flat (Nature tropes double-zero) | 1 -> **1** | ✅ -> **✅** |
| **Research Grant Proposal** (`grant`) | Academic | 5.5 pts | **3.0 pts** | **-45.5%** | 2 -> **1** | ✅ -> **✅** |
| **PopSci Column** (`popsci`) | General | 0.0 pts | 3.0 pts | Counter-example (disclosed) | 0 -> 1 | ✅ -> **✅** |
| **Tech Review** (`social`) | General | 2.5 pts | **0.0 pts** | **-100.0%** | 1 -> **0** (fabricated experience -> material-request protocol) | ✅ -> **✅** |
| **Incident Polish** (`polish`, conservation) | General + `--source` | 34.5 pts | **0.0 pts** | **-100.0%** | 8 (5 fabricated facts) -> **0** | ❌ hard FAIL -> **✅ PASS** |
| **EN->ZH Translation** (`translate`, conservation) | General + `--source` | 16.0 pts | **3.5 pts** | **-78.1%** | 4 (2 fabricated anchors) -> **1** | ❌ hard FAIL -> **✅ PASS** |
| **Macro Average** (8 subjects) | - | **8.50 pts** | **1.88 pts** | **-77.9%** | **2.25 -> 0.62 (-72.2%)** | **75.0% -> 100% Pass** |

- **Fabricated fact anchors 7 -> 0**: the solo model self-computed a "35.7% reduction" in polishing and added a "UX" acronym in translation — both hard-blocked by `fidelity_added`. The skill + gate arm conserves every number, model code, and acronym at 100%; the conservation subset mean drops 25.25 -> 1.75 (-93.1%).
- **Gate pass rate 75.0% -> 100%**: the drafting margin is narrower (-34.3%) — real GLM-5.3's residual pathologies have migrated to bold abuse, em-dash stacking, and assistant-style meta chatter. One in-loop remediation pass clears semantic-class violations; style-class needs more rounds.
- **Counter-example disclosed**: in popsci the solo model natively scored 0 violations and beat the skill arm (3.0). The gate is a floor guarantee and conservation backstop, not a promise of winning every scenario.

### 2.1 Cross-Model Independent Replication: mimo-v2.6-flash (2026-10-24)

> [!IMPORTANT]
> **Data provenance.** The identical protocol was re-run on `mimo-v2.6-flash` through the OpenCode Go gateway (`https://opencode.ai/zen/go/v1/chat/completions`), time window 2026-10-24T11:28:04Z -> 11:33:58Z. All **24 real HTTP POSTs returned 200** (mean latency 14391 ms), consuming a measured 27976 tokens (prompt 14554 + completion 13422, incl. 7635 reasoning). The harness contains zero mocks — any non-200 / empty body / truncated / degenerate output raises and aborts. Raw artifacts persist under `tests/fixtures_mimo/`, reproducible via `python3 scripts/run_mimo_benchmark.py`.

| Scenario | Solo Model | Model+Skill+Tool | Delta |
| :--- | :--- | :--- | :--- |
| Academic abstract `academic` | 16.5 pts / 5 / ❌ FAIL | **4.0 pts / 1 / ✅** | **-75.8%, FAIL → PASS** |
| Business memo `business` | 2.5 pts / 1 | **0.0 pts / 0** | **-100.0%** |
| English paper `en_academic` | 2.5 pts / 1 | **0.0 pts / 0** | **-100.0%** |
| Grant proposal `grant` | 5.5 pts / 2 | **3.0 pts / 1** | -45.5% |
| PopSci column `popsci` | 3.0 pts / 1 | 3.0 pts / 1 | Flat (counter-example) |
| Gadget review `social` | 5.5 pts / 2 | **3.0 pts / 1** | -45.5% |
| Incident polish `polish` (conservation) | 5.0 pts / ❌ FAIL (fabricated "35.7%") | **0.0 pts / ✅ (14/9/3 conserved)** | **-100.0%, FAIL → PASS** |
| EN->ZH translation `translate` (conservation) | 3.5 pts / 1 | 3.5 pts / 1 | Flat (counter-example) |
| **Macro average** (8) | **5.50 pts / 1.75 / 75% pass** | **2.06 pts / 0.62 / 100% pass** | **penalty -62.5%, violations -64.3%** |

- **The self-computed reduction is a cross-model collective hallucination**: solo mimo independently computed "降幅达 35.7%" and wrote it into the incident report — the very same fabricated figure GLM-5.3 produced, while the source contains no percentage at all. `fidelity_added` hard-blocks it; the gated arm conserves every digit at 100%.
- **Pathology migration corroborated**: solo mimo tripped the blocked-word list exactly once; its penalties come from the formulaic "随着……的飞速发展" opener, light-verb crutches, em-dash stacking, and bold abuse — the same migration direction as GLM-5.3.
- Real preference pairs are exported in three alignment formats (HF DPO / ChatML / ShareGPT, 8 pairs each) to `data/mimo_dpo/`; methodology, representative diffs, and the full disclosure of one pseudo tool-call degenerate output are in [Report Section 6](docs/BENCHMARK_REPORT.md).

---

## 3. Key Capabilities & AI Engineering Architecture

- **Task routing, information conservation, and optional warm tone** (`skill/anti-ai-copywriting/SKILL.md`, Section 0):
  - The agent first classifies the task: drafting, polishing, translation, or review.
  - **Polishing and translation**: the source owns the facts. No added numbers, people, scenes, or emotion; no dropped facts; assertion strength preserved; register matched to the source. Warmth comes from native syntax, never from invention.
  - **Original drafting of experiential genres** (column, essay, social post, brand story, speech): if the user has not stated a tone and the agent can interact, it asks once, with short examples, whether to write **A. objective** or **B. warm human-touch**. Warm mode uses only details the user supplied and inserts `[TODO: ...]` placeholders instead of inventing any.
  - Academic, grant, technical, business, polishing, translation, and non-interactive runs never trigger the question and default to objective.
- **Information-conservation gate**: `anti-ai-lint out.md --source original.md` fails the run when a number, code (e.g. `H100`), or acronym appears in the output but not in the source, and penalizes numbers or codes that vanish.
- **Information-Theoretic Cadence & Rhythm (Burstiness & UID)**:
  - Measures sentence length variation via the Coefficient of Variation ($CV_{len} = \sigma / \mu$).
  - Automatically flags `rhythmic_monotony` (penalty 3.5) if $CV_{len} < 0.28$ across qualifying sentences ($\ge 6$), eliminating the uniform 20-word AI drone.
  - Implements Moving-Average Type-Token Ratio (MATTR) with a 50-token sliding window for unbiased lexical richness tracking.
- **Excess-vocabulary word list** (informed by Kobak et al., 2025, *Science Advances*):
  - That study tracked vocabulary shifts across 15M+ PubMed abstracts. The word list follows its style words. The tier penalties below are this project's hand-set heuristics, not statistics from the paper:
    - **Tier S (5.0)**: `delve`, `delve into`, `delving into`, `tapestry of`, `intricate tapestry`, `meticulously`, `testament to`.
    - **Tier A (3.5)**: `realm`, `realm of`, `intricate`, `pivotal role`, `pivotal`, `beacon of`, `commendable`, `foster`, `navigating complexities`, `unwavering`.
    - **Tier B (2.0)**: `comprehensive`, `robust`, `leverage`, `utilize`, `seamless integration`, `seamless`, `seamlessly`, `multifaceted`, `myriad`, `revolutionize`.
- **Chinese Light Verb Constructions (LVC / 文字义肢) Closed Set**:
  - Closed set of light verbs (`进行|开展|展开|作出|予以|给以|给予|加以|具有|得到|受到|作|做|致以`) paired with nominalized action targets (`分析|探讨|调研|考察|评估|测评|审校|整改|梳理|阐述|测查|优化|迭代|部署|排查|总结|研究|复盘`).
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

## 4. Installation & Deployment

### 4.1 Agent Skill & Rules Integration

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

### 4.2 Standalone Python Linter (`anti-ai-lint`)

Install locally or in your virtual environment:

```bash
pip install ./lint
```

Or run directly without installation:

```bash
python3 -m anti_ai_lint /path/to/document.md --max-score 8.0
```

---

### 4.3 Model Context Protocol (MCP) Server

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

### 4.4 GitHub Action & Pre-Commit Hook

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
    rev: v0.5.0
    hooks:
      - id: anti-ai-lint
        args: ["--format", "hook", "--genre", "general"]
```

---

## 5. Linter Usage & Output Modes

```bash
# General mode
anti-ai-lint paper.md

# Academic mode with hook format for pre-commit loops
anti-ai-lint paper.md --genre academic --format hook --max-score 8.0

# Controlled plain layer validation
anti-ai-lint guide.md --genre plain --format agent

# GitHub Actions format (produces workflow annotations)
anti-ai-lint docs/ --format github

# Polishing or translation: verify information conservation against the original
anti-ai-lint polished.md --source original.md --format hook
```

### 5.1 Polishing & Translation: Information-Conservation Check

`--source` compares the **fact anchors** of the checked text with the original: plain numbers (`1,200` equals `1200`), letter-led codes (`H100`, `CASP14`), and all-caps acronyms. Anchors that appear only in the output fail the gate regardless of `--max-score`. Numbers or codes missing from the output cost 3.0 points each.

Real results from `tests/workflow_cases/` (reproduce with the commands in the last column):

| Case | Source | Output | Result |
| :--- | :--- | :--- | :--- |
| Polish, faithful | `polish/source.md` | `polish/faithful.md` | ✅ PASS, score 0.0 |
| Polish, invented detail | `polish/source.md` | `polish/fabricated.md` (adds "3 weeks" and "36%") | ❌ FAIL, 2 × `fidelity_added`, score 10.0 |
| Translate EN→ZH, faithful | `translate/source.en.md` | `translate/faithful.zh.md` | ✅ PASS, score 0.0 |
| Translate EN→ZH, invented detail | `translate/source.en.md` | `translate/fabricated.zh.md` (adds "87%") | ❌ FAIL, 1 × `fidelity_added`, score 5.0 |

```bash
anti-ai-lint tests/workflow_cases/polish/fabricated.md --source tests/workflow_cases/polish/source.md --format hook
```

> [!WARNING]
> **What the check cannot see.** It only verifies numbers, codes, and acronyms. Invented adjectives, scenes, or feelings that contain none of these (for example "at midnight, in despair") pass undetected, and so does a changed meaning. Chinese numerals such as 三个通宵 are not tracked. A clean result means "no unsupported anchors found", not "faithful". Keep human review for anything that matters.

### Output Formats (`--format`)

- `text`: Human-readable summary with exact line/column locations, cadence metrics, and fix suggestions.
- `json`: Machine-readable structured AST and metrics report.
- `hook`: Compact single-line / multi-line summary designed for git pre-commit and Harness² in-loop hooks.
- `agent`: Specially formatted `<anti-ai-lint-feedback>` XML payload for LLM reflector loops.
- `github`: Native GitHub Actions Workflow Commands (`::warning` and `::error`).

---

## 6. Academic References & Citations

The design draws on the research and standards below. The detection papers (items 3–5) are background for the burstiness idea only: this tool implements no model-based detector. Items 9–12 underpin the information-conservation rules for polishing and translation.

1. **Kobak, D., González-Márquez, R., Horvát, E.-Á., & Lause, J. (2025)**. Delving into LLM-assisted writing in biomedical publications through excess vocabulary. *Science Advances, 11*(27), eadt3813. https://doi.org/10.1126/sciadv.adt3813 (arXiv:2406.07016).
2. **Meister, C., Pimentel, T., Haller, P., Jäger, L., Cotterell, R., & Levy, R. (2021)**. Revisiting the uniform information density hypothesis. In *Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (arXiv:2109.11635).
3. **Mitchell, E., Lee, Y., Khazatsky, A., Manning, C. D., & Finn, C. (2023)**. DetectGPT: Zero-shot machine-generated text detection using probability curvature. In *Proceedings of the 40th International Conference on Machine Learning (ICML)* (arXiv:2301.11305).
4. **Hans, A., Schwarzschild, A., Cherepanova, V., Kazemi, H., Saha, A., Goldblum, M., Geiping, J., & Goldstein, T. (2024)**. Spotting LLMs with Binoculars: Zero-shot detection of machine-generated text. In *Proceedings of the 41st International Conference on Machine Learning (ICML)* (arXiv:2401.12070).
5. **Dugan, L., Hwang, A., Trhlik, F., Ludan, J. M., Zhu, A., Xu, H., Ippolito, D., & Callison-Burch, C. (2024)**. RAID: A shared benchmark for robust evaluation of machine-generated text detectors. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL)* (arXiv:2405.07940).
6. **Zhu, D. X. (朱德熙). (1982)**. *语法讲义* [Lectures on grammar]. Commercial Press. (Chinese light verb constructions and nominalization.)
7. **ASD-STE100 Specification**. Aerospace, Security and Defence Industries Association of Europe (ASD). Simplified Technical English Specification.
8. **Xu, R., et al. (2026)**. Harness^2: Recursive agent harnessing for an open world. arXiv:2610.14224.
9. **ISO 17100:2015**. *Translation services — Requirements for translation services*. International Organization for Standardization.
10. **ISO 18587:2017**. *Translation services — Post-editing of machine translation output — Requirements*. International Organization for Standardization.
11. **GB/T 19363.1-2008**. 翻译服务 译文质量要求 第1部分：笔译 [Translation services — Specification for translation quality — Part 1: Translation]. Standardization Administration of China.
12. **Yan, F. (严复). (1898)**. 《天演论》译例言 [Translator's preface to *Evolution and Ethics*] (the "faithfulness, expressiveness, elegance" principle).

---

## 7. Uninstallation

Cleanly restore backups and remove marker blocks without touching other configurations:

```bash
# Uninstall a specific target
./uninstall.sh --target codex
./uninstall.sh --target cursor --dest /path/to/project

# Uninstall all registered targets
./uninstall.sh --all
```

---

## 8. Trademark & Non-Affiliation Notice

All product names, logos, brands, trademarks, and registered trademarks mentioned in this repository (including Anthropic, Claude, Claude Code, OpenAI, ChatGPT, Codex, DeepSeek, Google, Gemini, Antigravity, Cursor, Windsurf, Codeium, Cline, Aider, WorkBuddy, and others) are property of their respective owners. Their use in this documentation does not imply any affiliation with, endorsement by, or sponsorship by their respective holders. All integrations and adapter instructions are independent, community-developed open-source compatibility layers.

---

## 9. License

[MIT](LICENSE) © 2026 Liangliang Chen
