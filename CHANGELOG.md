# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-10-24

### Added
- **Task Routing Architecture**:
  - Explicitly routes text generation into four distinct workflows: `Drafting` (起草), `Polishing` (润色), `Translation` (翻译), and `Review` (评审).
  - Documented protocol in `skill/anti-ai-copywriting/SKILL.md` (Section 0), `rules/AGENTS.snippet.*.md`, and `sub_agents/copywriting-editor/AGENT.md`.
- **Information Conservation Axioms (信息守恒四公理)**:
  - Formulated strict factual conservation laws for Polishing and Translation: zero added facts, zero dropped facts, unchanged assertion strength, and register matching.
  - Anchored naturalness and expressiveness in *syntactic decompression* (意合化、去欧化、名物化还原) instead of inventing emotional scenes or background trivia.
- **Deterministic Information-Conservation Gate (`fidelity.py` & `--source`)**:
  - Added pure standard library factual anchor extractor in `lint/anti_ai_lint/fidelity.py` tracking normalized numbers, letter-led codes (e.g. `H100`, `CASP14`), and uppercase acronyms with token count preservation.
  - Integrated hard-failure violation `fidelity_added` (+5.0 penalty, non-bypassable) and `fidelity_dropped` (+3.0 penalty) in `detector.py`.
  - Added `--source <path>` flag to CLI (`anti_ai_lint.cli`) with validation preventing directory or multi-target runs.
  - Integrated `source_text` and `source_path` inputs to MCP server tool `lint_prose`, with style contracts updated in `get_style_contract`.
- **Warm Human-Touch Protocol for Original Drafting (温感叙事交互协议)**:
  - Added interactive one-time prompt protocol for experiential/narrative drafting (columns, essays, social reviews, speeches, brand stories) presenting A/B options (`A. 客观克制` vs. `B. 温感叙事`) with concrete examples.
  - Enforced strict anti-hallucination constraint on warm mode: uses only user-provided physical details and sensory observations, inserting explicit `[待补充细节: ...]` / `[TODO: ...]` placeholders when details are absent.
  - Excluded academic papers, grant proposals, technical documentation, business memos, polishing, translation, and non-interactive scripts from prompting (defaulting to objective mode).
- **Comprehensive Workflow Test Fixtures & Unit Tests**:
  - Created real-world test cases in `tests/workflow_cases/` for polishing, translation, and warm drafting.
  - Added `tests/test_workflow.py` with 27 unit tests validating anchor extraction, CLI `--source` execution, MCP tool contracts, warm-tone criteria, and cross-file documentation synchronization.
- **Real GLM-5.3 End-to-End Benchmark (Solo Model vs. Model + Skill + Tool Gate)**:
  - Introduced `scripts/run_glm5_benchmark.py`: a dual-blind evaluation harness comparing bare GLM-5.3 native generation against GLM-5.3 + skill rule injection + `anti-ai-lint` in-loop deterministic gate (with one remediation pass), across 6 drafting scenarios and 2 information-conservation workflows (polish/translate under `--source`).
  - Persisted genuine model outputs and metrics under `tests/fixtures_glm5/` (per-scenario `solo_before.md` / `skill_tool_after.md` + `benchmark_results.json`); hardened the runner against empty response bodies, thinking-token budget exhaustion, and provider 429 rate limits.
  - Headline measured results (8 subjects): mean penalty 8.50 -> 1.88 (-77.9%), mean violations 2.25 -> 0.62 (-72.2%), gate pass rate 75.0% -> 100%, fabricated fact anchors 7 -> 0; conservation subset (polish/translate) penalty 25.25 -> 1.75 (-93.1%) with both solo runs hard-blocked by `fidelity_added`.
- **Academic References & Translation Standards Harmonization**:
  - Corrected Kobak et al. citation to peer-reviewed publication: *Science Advances*, 11(27), eadt3813 (2025).
  - Integrated translation and post-editing standards (ISO 17100:2015, ISO 18587:2017, GB/T 19363.1-2008, Yan Fu 1898) across documentation and benchmark reports.

### Changed
- **Replaced demonstration benchmark reports with real GLM-5.3 measurements**:
  - Rewrote `docs/BENCHMARK_REPORT.zh-CN.md` and `docs/BENCHMARK_REPORT.md` end to end: all scoreboards, the full 8-subject quantitative matrix, and all side-by-side case studies now quote verbatim GLM-5.3 generations from `tests/fixtures_glm5/`, including honest disclosures (residual style violations, one popsci counter-example where the solo model scored 0.0).
  - Updated `README.zh-CN.md` and `README.md` Section 2 tables and data-provenance notes to the same real measurements; the hand-written exemplars in `tests/fixtures/` remain for deterministic regression tests.

## [0.4.0] - 2026-10-24

### Added
- **Statistical Cadence & Information-Theoretic Metrics (UID Hypothesis & Burstiness)**:
  - Added pure Python standard library sentence length variation / Burstiness Coefficient of Variation ($CV_{len} = \sigma / \mu$).
  - Implemented automated `rhythmic_monotony` detection (penalty 3.5) triggered when $CV_{len} < 0.28$ across qualifying sentences ($\ge 6$).
  - Added Moving-Average Type-Token Ratio (MATTR) with window size 50 for sliding lexical richness tracking without sample-length bias.
- **Kobak et al. 2024 (Nature/Science Advances) Excess Vocabulary Integration**:
  - Calibrated PubMed excess vocabulary with tiered log-odds penalty weights:
    - Tier S (Penalty 5.0): `delve`, `delve into`, `delving into`, `tapestry of`, `intricate tapestry`, `meticulously`, `testament to`.
    - Tier A (Penalty 3.5): `realm`, `realm of`, `intricate`, `pivotal role`, `pivotal`, `beacon of`, `commendable`, `foster`, `navigating complexities`, `unwavering`.
    - Tier B (Penalty 2.0): `comprehensive`, `robust`, `leverage`, `utilize`, `seamless integration`, `seamless`, `seamlessly`, `multifaceted`, `myriad`, `revolutionize`.
- **Chinese Light Verb Constructions (LVC / 文字义肢) Closed Set Expansion**:
  - Expanded closed set of light verbs (`进行|开展|展开|作出|予以|给以|给予|加以|具有|得到|受到|作|做|致以`) paired with action targets (`分析|探讨|调研|考察|评估|测评|审校|整改|梳理|阐述|测查|优化|迭代|部署|排查|总结|研究|复盘`) with flexible bounded modifiers (`展开了全面的性能测评`, `安全排查`, `进一步分析`).
  - Added actionable de-nominalization rewrite guidelines and dynamic remediation suggestions.
- **Model Context Protocol (MCP) Server**:
  - Implemented zero-dependency JSON-RPC 2.0 stdio MCP server (`anti-ai-mcp` / `python3 -m anti_ai_lint.mcp_server` and `mcp_server/server.py`).
  - Hardened protocol parsing with batch array handling, non-dict validation, and error containment preventing server loop crashes.
  - Exposed 3 standard MCP tools: `lint_prose`, `remediate_violation`, and `get_style_contract`.
- **Modern AI Engineering Toolchain**:
  - Official GitHub Action (`action.yml`) supporting PR inline workflow annotations (`::warning` / `::error`).
  - Added `--format github` and `--format gh-action` to CLI.
  - Official pre-commit configuration (`.pre-commit-hooks.yaml`).
  - Added DSPy prompt optimization runner script (`scripts/dspy_optimizer.py`).
  - Added DPO / SimPO preference dataset exporter (`scripts/export_dpo_pairs.py`) supporting DPO, ChatML, and ShareGPT formats.
- **Multi-Platform Agent Guides**:
  - Added dedicated bilingual integration guides for **Cursor**, **Windsurf**, **Cline**, **Aider**, and **Antigravity**.

## [0.3.0] - 2026-10-24

### Added
- **Multi-Agent Adapters & Bilingual Documentation Matrix**:
  - Added explicit target support and comprehensive bilingual guides for **Codex**, **Claude Code**, **DeepSeek**, **OpenCode**, **WorkBuddy**, and common coding agents (**Cursor**, **Windsurf**, **Cline**, **Aider**, **Antigravity**, **ZCode**).
  - Provided bilingual index matrices in `docs/adapters/README.md` and `docs/adapters/README.zh-CN.md`.
  - Added bilingual documentation hubs in `docs/README.md` and `docs/README.zh-CN.md`.
- **Harness² Architectural Integrations (c1..c8)**:
  - **c8 In-Loop Verification Hook**: Added `hooks/hooks.json` and `.codex/hooks.json` for post-tool verification during agent write operations.
  - **c8 OpenCode Plugin**: Implemented `plugin/anti-ai-copywriting.ts` to intercept agent tool executions and feed prose lint warnings into the agent loop.
  - **c5 Dedicated Copy-Editing Subagent**: Created `sub_agents/copywriting-editor/AGENT.md` defining specialist role, contracts, and quality-gate workflow.
  - **c6/c1 Explicit Autotrigger Directives**: Added `<auto_trigger>` contract blocks to `rules/AGENTS.snippet.md`, `rules/AGENTS.snippet.zh.md`, and `rules/AGENTS.snippet.en.md`.
- **Linter Engine & CLI Capabilities**:
  - Added `--genre {general,academic,plain}` supporting strict academic hedging checks and controlled plain layer constraints (Chinese $\le 30$ chars, English $\le 25$ words, zero vague quantifiers).
  - Added `--format hook` for compact CI/pre-commit feedback and `--format agent` for structured LLM reflection.
  - Added normalized scoring (`normalized_score` per 1,000 text units) and `--max-normalized-score` filtering.
  - Added actionable remediation suggestions to every violation across all categories.
- **Installer & Uninstaller Upgrades**:
  - Expanded installer targets in `install.sh` to include `deepseek`, `cursor`, `windsurf`, `cline`, `aider`, `antigravity`, `generic`, `workbuddy`, `opencode`, `codex`, `claude`, and `zcode`.
  - Implemented multi-target manifest tracking in `install-manifest.json` preserving distinct records across targets.
  - Added functional `--lang zh|en` support deploying language-tailored snippets.
  - Enhanced `uninstall.sh` supporting `--target <name>`, `--dest <path>`, `--all`, and safe disambiguation prompts preventing unintended bulk project deletion.
  - Added integration test suite `tests/test_installer.py` covering selective project removal, paths with spaces, and multi-target isolation.
- **Open Source Compliance & Attribution**:
  - Added SPDX license headers and copyright statements across bash, Python, and TypeScript modules.
  - Standardized author format in `pyproject.toml` and verified entrypoint licensing.
  - Included formal Trademark & Non-Affiliation disclaimers covering Anthropic, OpenAI, DeepSeek, Google, Anysphere (Cursor), Codeium (Windsurf), Cline, Aider, and WorkBuddy.
  - Added formal citations and copyright statements for ASD-STE100 and Google Research Harness².

### Fixed
- **Code Block State Machine**: Fixed bug in `detector.py` where lines inside multi-line fenced code blocks (` ``` ` / ` ~~~ `) and inline code (`` `...` ``) were falsely flagged as prose violations.
- **Uninstaller Project Targeting**: Fixed issue where `uninstall.sh` lacked `--dest` support and indiscriminately deleted all matching targets across multiple project paths.
- **Bilingual Sentence Splitting**: Replaced naive regex split with robust tokenization that protects decimal numbers (e.g. `28.6%`) and abbreviations (e.g. `e.g.`, `i.e.`, `et al.`).
- **Word Counting**: Implemented true bilingual token counting combining CJK characters and Latin words.
- **Template Phrase Matching**: Fixed unescaped ellipsis matching in Chinese phrase patterns (e.g. `随着...的飞速发展` converted to dynamic regex pattern).
- **Wordlist Synchronization**: Synchronized root `wordlists/` with package `lint/anti_ai_lint/wordlists/` and in-code defaults.

## [0.2.0] - 2026-10-23

### Added
- Integrated full `natural-voice` skill rules (Academic Voice, Controlled Plain Layer, Academic Presentation Standards, and full self-inspection checklist).
- Standalone zero-dependency Python linter `anti-ai-lint` with CLI supporting `--max-score`, `--format json|text`, and wordlist customization.
- Six fixture scenarios under `tests/fixtures/` with regression tests comparing before and after rewrites.
- Multi-agent adapter documentation for ZCode, Claude Code, Codex, OpenCode, Generic, and WorkBuddy.
- Bounded marker blocks for safe installation into shared rule files (`AGENTS.md`, `CLAUDE.md`).
- GitHub Actions CI workflow for Python 3.8-3.14.

### Changed
- Refined "不是……而是……" rule from blanket prohibition to targeting pseudo-contrasts without real empirical opposition (A3).
- Rewrote all English rule sections into idiomatic English (A4).
- Expanded bilingual forbidden buzzword lists with additional tropes and hedges (A2).
