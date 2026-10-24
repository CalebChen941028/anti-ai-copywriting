# anti-ai-copywriting

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![Version: 0.8.0](https://img.shields.io/badge/version-0.8.0-green.svg)](CHANGELOG.md)
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

## 2. Real Empirical Benchmark: mimo-v2.6-flash (Solo Model vs. Model + Skill + Tool Gate)

> [!NOTE]
> For the comprehensive benchmark report, mathematical derivations, in-depth linguistic diagnoses across all 8 subjects, and CLI reproduction commands, please consult: **[Full Benchmark & Evaluation Report (docs/BENCHMARK_REPORT.md)](docs/BENCHMARK_REPORT.md)**.

> [!IMPORTANT]
> **Data Provenance & Audit Guarantee.** All evaluation data in this table is measured output of genuine end-to-end inference on **`mimo-v2.6-flash`** via the OpenCode Go gateway (`https://opencode.ai/zen/go/v1/chat/completions`, time window: 2026-10-24T11:28:04Z → 11:33:58Z). All **24 live HTTP POSTs returned 200 OK** (mean latency 14,391 ms), consuming a measured **27,976 tokens** (prompt 14,554 + completion 13,422, incl. 7,635 reasoning tokens). Every single generation is tracked with a unique server-issued `response_id`. All raw texts and immutable audit records persist under `tests/fixtures_mimo/`, reproducible via `python3 scripts/run_mimo_benchmark.py`. All unverified demonstration or synthetic mock fixtures have been completely purged from the repository.

The 8 subjects (6 drafting genres + 2 information-conservation workflows) evaluate as follows:

| Scenario / Corpus | Genre Mode | Solo Penalty | Model+Skill+Tool | Score Delta | Violations Count | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Academic Abstract** (`academic`) | Academic | 16.5 pts | **4.0 pts** | **-75.8%** | 5 -> **1** | ❌ FAIL -> **✅ PASS** |
| **Business Memo** (`business`) | General | 2.5 pts | **0.0 pts** | **-100.0%** | 1 -> **0** | ✅ -> **✅** |
| **English Academic Paper** (`en_academic`) | Academic | 2.5 pts | **0.0 pts** | **-100.0%** | 1 -> **0** | ✅ -> **✅** |
| **Research Grant Proposal** (`grant`) | Academic | 5.5 pts | **3.0 pts** | **-45.5%** | 2 -> **1** | ✅ -> **✅** |
| **PopSci Column** (`popsci`) | General | 3.0 pts | 3.0 pts | Flat (counter-example) | 1 -> 1 | ✅ -> **✅** |
| **Tech Review** (`social`) | General | 5.5 pts | **3.0 pts** | **-45.5%** | 2 -> **1** | ✅ -> **✅** |
| **Incident Polish** (`polish`, conservation) | General + `--source` | 5.0 pts | **0.0 pts** | **-100.0%** | 1 (fabricated "35.7%") -> **0** | ❌ Hard FAIL -> **✅ PASS** |
| **EN->ZH Translation** (`translate`, conservation) | General + `--source` | 3.5 pts | 3.5 pts | Flat (counter-example) | 1 -> 1 | ✅ -> **✅** |
| **Macro Average** (8 subjects) | - | **5.50 pts** | **2.06 pts** | **-62.5%** | **1.75 -> 0.62 (-64.3%)** | **75.0% -> 100% Pass** |

- **Strict Information Conservation**: The solo model in polishing autonomously computed and hallucinated "降幅达 35.7%" (a figure absent from the source), triggering an immediate hard block by `fidelity_added`. The skill + gate arm achieves 100% numerical and factual conservation.
- **De-cliché and Cadence Restoration**: In the academic abstract, the solo model defaulted to the formulaic opening ("随着……的飞速发展"), light-verb nominalizations, and monotonous sentence cadence ($CV_{len} = 0.25$). The skill gate restructured the opening to lead with empirical findings and varied sentence rhythms, reducing penalty from 16.5 to 4.0 pts.
- **Empirical Honesty**: In popsci and technical translation, scores were flat, transparently disclosing that modern reasoning models already possess baseline competence on straightforward prompts and illustrating that the gate functions as a deterministic safety floor rather than claiming synthetic 100% wins.
- **DPO Preference Pairs**: Preference pairs across all 8 subjects are exported in HF DPO, ChatML, and ShareGPT formats under `data/mimo_dpo/`.

### 2.2 Advanced Stress Benchmark: deepseek-v4.1-flash (Long-Form, Unit Normalization, Adversarial Buzzwords)

> [!NOTE]
> To probe engine robustness across long-form drift, multi-magnitude units, and adversarial corporate buzzwords, an advanced stress test harness evaluates **`deepseek-v4.1-flash`**. Full audit records persist in [tests/fixtures_advanced/BENCHMARK_REPORT.md](tests/fixtures_advanced/BENCHMARK_REPORT.md).

> [!IMPORTANT]
> **Data Provenance & Audit Guarantee.** All evaluation data below represents genuine end-to-end inference on **`deepseek-v4.1-flash`** via the OpenCode Go gateway (`https://opencode.ai/zen/go/v1/chat/completions`, session: `session-deepseek-advanced-benchmark-2026`). All **10 live HTTP POSTs returned 200 OK** (mean latency 19,009 ms), consuming **29,843 tokens** (prompt 7,569 + completion 22,274, incl. 17,461 reasoning tokens). Every generation has a verifiable server-issued `response_id`. All raw texts and immutable audit records persist under `tests/fixtures_advanced/`, reproducible via `python3 scripts/run_advanced_benchmark.py`.

| Advanced Scenario | Key Challenges & Focus | Solo Penalty | Model+Skill+Tool | Gate Verdict | Closed-Loop Mechanism |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Active-Active Architecture** (`long_architecture`) | 1500+ word long-form style drift, paragraph cadence, hedging | 4.0 pts / 1 viol | **0.0 pts / 0 viol** | ❌ Block -> **✅ PASS** | Prior rule injection; 1,503 words with healthy cadence ($CV \ge 0.55$) |
| **Financial Migration Report** (`financial_unit_fidelity`) | Semantic physical & financial unit normalization under `--source` | 7.5 pts / 2 viols | **5.0 pts / 2 viols** | ❌ Block -> **✅ PASS** | In-loop reflection triggered (57.5 -> 5.0 pts); equivalent units passed, zero hallucinations |
| **Adversarial Buzzwords** (`adversarial_cliche`) | Cleaning 10+ stacked corporate clichés (empower, synergy, closed-loop) | 2.5 pts / 1 viol | **2.5 pts / 1 viol** | ✅ PASS -> **✅ PASS** | All buzzwords eliminated into concrete actions; minimal formatting bolding |
| **Provocative Academic Abstract** (`multiturn_remediation`) | High-risk prompt tempting grandiose narrative and empty praise | 11.0 pts / 3 viols | **0.0 pts / 0 viols** | ❌ Block -> **✅ PASS** | Prior conditioning intercepted buzzwords, passing cleanly on Turn 1 |

### 2.3 Extreme Frontier Benchmark: deepseek-v4.1-flash (Code/Math Interleaving, Anti-Camouflage, Multi-Source Synthesis & Long English)

> [!NOTE]
> Probing the four furthest frontiers: code listings and LaTeX math equations, adversarial pseudo-casual camouflage, multi-document synthesis, and long-form English whitepapers. Full audit records persist in [tests/fixtures_extreme/BENCHMARK_REPORT.md](tests/fixtures_extreme/BENCHMARK_REPORT.md).

> [!IMPORTANT]
> **Data Provenance & Audit Guarantee.** All evaluation data below represents genuine end-to-end inference on **`deepseek-v4.1-flash`** via the OpenCode Go gateway (`https://opencode.ai/zen/go/v1/chat/completions`, session: `session-deepseek-extreme-benchmark-2026`). All **12 live HTTP POSTs (including 1 length-truncation guard retry) returned 200 OK** (mean latency 28,095 ms), consuming **45,156 tokens** (prompt 12,129 + completion 33,027, incl. 26,112 reasoning tokens). Every generation has a verifiable server-issued `response_id`. All raw texts and immutable audit records persist under `tests/fixtures_extreme/`, reproducible via `python3 scripts/run_extreme_benchmark.py`.

| Extreme Frontier Scenario | Key Challenges & Focus | Solo Penalty | Model+Skill+Tool | Gate Verdict | Empirical Observations & Mechanism |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Code & Math Interleaving** (`code_math_interleave`) | DPDK kernel bypass whitepaper; verifying code blocks, port numbers, and LaTeX math isolation | 42.0 pts / 9 viols | **12.5 pts / 3 viols** | ❌ Block -> **✅ Significant Convergence** | Code block contents (`port_id`, `32`) zero false positives; dropped from 65.0 to 12.5 pts, identifying unit nuances |
| **Anti-Camouflage Colloquialism** (`anti_camouflage_colloquial`) | Adversarial conversational prompt tempting informal chat tone in executive paper | 2.5 pts / 1 viol | **3.5 pts / 1 viol** | ✅ PASS -> **✅ PASS** | Solo fell into register trap, flagged for 「说白了」; Skill arm restored executive gravitas |
| **Multi-Source Factual Synthesis** (`multi_source_synthesis`) | Fusing 3 separate documents (arch, perf, cost); joint anchor pool prevents attribution errors | 37.5 pts / 8 viols | **0.0 pts / 0 viols** | ❌ Block -> **✅ Perfect PASS** | Solo over-repeated cross-doc figures (7 viols); Skill achieved 0.0 pts in loop; 3 unit conversions passed |
| **Long-Form English Whitepaper** (`long_english_whitepaper`) | 600-900 word paper; verifying fronted participial clauses & transitional adverb stacking | 0.0 pts / 0 viols | **3.0 pts / 1 viol** | ✅ PASS -> **✅ PASS** | Both arms showed healthy cadence ($CV \ge 0.40$); Skill arm had minor dash remnant (3.0 pts), transparently disclosed |

---

## 3. Key Capabilities & AI Engineering Architecture

- **Task routing, information conservation, and optional warm tone** (`skill/anti-ai-copywriting/SKILL.md`, Section 0):
  - The agent first classifies the task: drafting, polishing, translation, or review.
  - **Polishing and translation**: the source owns the facts. No added numbers, people, scenes, or emotion; no dropped facts; assertion strength preserved; register matched to the source. Warmth comes from native syntax, never from invention.
  - **Original drafting of experiential genres** (column, essay, social post, brand story, speech): if the user has not stated a tone and the agent can interact, it asks once, with short examples, whether to write **A. objective** or **B. warm human-touch**. Warm mode uses only details the user supplied and inserts `[TODO: ...]` placeholders instead of inventing any.
  - Academic, grant, technical, business, polishing, translation, and non-interactive runs never trigger the question and default to objective.
- **Information-Conservation Gate, Multi-Source Synthesis & Code/Math Isolation**:
  - `anti-ai-lint out.md --source original.md [source2.md ...]` performs two-way anchor verification against one or more source texts.
  - **Multi-Source Factual Synthesis Pool**: pools anchors and quantities across multiple background files, strictly preventing hallucinated additions (`fidelity_added`) while exempting summary omissions.
  - **Code Listings and LaTeX Math Block Isolation**: automatically isolates fenced code blocks and display equations from anchor extraction, preventing ports, memory offsets, and formula symbols from leaking into prose checks; strips wrapping backticks and dollars so inline technical values (e.g. `` `850ns` ``) remain strictly conserved.
  - **Semantic Unit Normalization**: recognizes semantic physical and magnitude equivalence across time (`ms ↔ s ↔ min ↔ h ↔ day`), storage (`B ↔ KB ↔ MB ↔ GB ↔ TB`), and CJK financial orders (`万 ↔ 亿`, `万元 ↔ 千万元 ↔ 亿元`).
- **Information-Theoretic Cadence, Anti-Camouflage & Long English Patterns**:
  - Measures global sentence length variation via the Coefficient of Variation ($CV_{len} = \sigma / \mu$). Flags `rhythmic_monotony` (penalty 3.5) if global $CV_{len} < 0.28$ across qualifying sentences ($\ge 6$).
  - **Localized Paragraph Rhythmic Monotony** (`localized_rhythmic_monotony`): in long-form prose ($\ge 600$ characters), flags natural paragraphs where $\ge 5$ consecutive sentences exhibit a localized $CV_{len} < 0.20$.
  - **Anti-Camouflage & Colloquialism Interception**: `inappropriate_colloquialism` catches conversational crutches ("说白了", "你猜怎么着", "坦率地讲") in formal writing; `staccato_overfragmentation` flags $\ge 3$ consecutive micro-sentences ($\le 3$ words/chars) used to game variance.
  - **Long-form English Cliché Patterns**: detects repetitive sentence-initial participial clauses (`english_participial_fronting`) and repetitive fronted discourse adverbs (`english_sentence_head_stacking`, e.g. `Crucially,`, `Notably,`).
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
    rev: v0.8.0
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
