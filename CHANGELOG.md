# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-10-25

### Added
- **Macro Paragraph Cadence Variance Engine (`lint/anti_ai_lint/detector.py`)**:
  - Implemented macro paragraph length Coefficient of Variation ($CV_{para} = \sigma_{para} / \mu_{para}$) across long-form prose ($\ge 3$ eligible paragraphs, $\ge 300$ words/units).
  - Flags `paragraph_cadence_variance` (penalty 2.5) when paragraph length $CV_{para} < 0.15$, penalizing robotic, equal-length AI paragraph "brick walls" while exempting bullet lists, headers, code, and tables.
  - Exposed `para_cv` directly in `TextMetrics` dataclass and JSON reports for cadence analysis.
- **Syntactic Sentence-Starter Repetition Gate (`lint/anti_ai_lint/detector.py`)**:
  - Pure standard-library syntactic template extractor detecting repetitive consecutive sentence openings ($\ge 3$ consecutive prose sentences sharing identical templates).
  - Catches prepositional formulaic openers in Chinese (e.g. 「通过……」「针对……」「基于……」「为了……」) and structural patterns in English (e.g. `The [noun]`, `This [noun]`, `In order to`).
  - Correctly excludes Markdown lists, headers, and code blocks from starter penalty.
- **Unprompted Blind Stress Benchmark Suite (`scripts/run_frontier_v4_benchmark.py`)**:
  - Eliminated prompt leaking / negative prompting (zero hints on avoiding buzzwords, light verbs, or sentence patterns), effectively breaking the benchmark floor effect.
  - Benchmarked `deepseek-v4.1-flash` via OpenCode Go API across 3 unprompted enterprise briefs (kernel architecture, executive board memo, long-form KV-cache position paper).
  - Full audit telemetry: 8 genuine HTTP 200 calls, 34,768 tokens (78% reasoning tokens), live truncation handling and autonomous self-healing loops recorded in `tests/fixtures_frontier_v4/`.
- **Authoritative Human Gold-Standard Baseline Suite (`tests/fixtures_human_gold/`)**:
  - Curated 4 verbatim, publicly verifiable human masterworks:
    - USENIX ATC '14 Best Paper abstract (*In Search of an Understandable Consensus Algorithm*, Ongaro & Ousterhout).
    - Linux Kernel official scaling documentation (*Receive Packet Steering*, Tom Herbert).
    - Chinese veteran systems engineering treatise (*Online*, Dr. Wang Jian, CITIC Press 2016).
    - 1997 Amazon.com Letter to Shareholders (Jeff Bezos).
  - Automated regression suite verifies 100% PASS with 0.0 penalty score and zero false positives.
- **Unit Test Suite Expanded to 109 Tests**:
  - Added deterministic boundary tests for macro paragraph cadence, sentence starter repetition, and human gold-standard invariance. All 109 tests passing in 3.5s.

## [0.7.0] - 2026-10-25

### Added
- **Multi-Source Factual Synthesis Gate (`fidelity.py` & `cli.py`)**:
  - Upgraded `--source` CLI argument to accept multiple files (e.g. `--source arch.md perf.md cost.md`).
  - Implemented multi-document joint anchor pooling: tracks anchors and quantities across all source documents simultaneously.
  - Automatically identifies cross-document quantity equivalence and strictly prevents fabricated ungrounded data (`fidelity_added`) while exempting background detail omissions in summarization.
- **Code Listings and LaTeX Math Block Isolation (`fidelity.py`)**:
  - Implemented automatic isolation of fenced code blocks (```` ```...``` ````) and display equations (`$$...$$`, `\[...\]`).
  - Strips inline backticks and math dollar signs, cleanly exposing inline technical numerals (e.g. `` `850ns` ``) without allowing code internals (ports, hex memory addresses) to pollute prose factual anchors.
- **Inappropriate Colloquialism & Anti-Camouflage Gate (`detector.py`)**:
  - Added `inappropriate_colloquialism` detection (penalty 2.5) for formal academic and general writing: intercepts cheap conversational fillers (e.g., "说白了", "你猜怎么着", "坦率地讲", "咱就是说", "老实说") inserted by models attempting to bypass AI detection via pseudo-casual tone.
  - Added `staccato_overfragmentation` detection (penalty 2.5): flags 3 or more consecutive micro-sentences ($\le 3$ characters/words) attempting to artificially game sentence length variance.
- **Long-form English Cliché & Sentence-Head Patterns (`detector.py`)**:
  - Added `english_participial_fronting` detection (penalty 2.5): flags repetitive sentence-starting participial clauses (e.g. `Leveraging...`, `Having established...`, `Delving into...`).
  - Added `english_sentence_head_stacking` detection (penalty 2.5): flags repetitive fronted discourse adverbs (`Crucially,`, `Notably,`, `Strikingly,`, `Importantly,`).
- **DeepSeek v4.1-Flash Extreme Frontier Benchmark (`scripts/run_extreme_benchmark.py`)**:
  - Live empirical dual-blind A/B testing suite on `deepseek-v4.1-flash` via OpenCode Go gateway (`https://opencode.ai/zen/go/v1/chat/completions`).
  - 12 real HTTP calls, 45,156 tokens, 100% 200 OK (with live truncation guard handling).
  - Evaluated 4 cutting-edge frontier challenges: code/math interleave, anti-camouflage colloquialism, multi-source synthesis, and long English whitepaper.
  - Persisted live audit records to `tests/fixtures_extreme/`.
- **Test Suite Expanded to 106 Tests**:
  - Added unit tests for multi-source fidelity, code block isolation, colloquialism detection, staccato fragmentation, and English fronting. All 106 tests passing.

## [0.6.0] - 2026-10-24

### Added
- **Semantic Unit & Magnitude Normalization Engine (`lint/anti_ai_lint/fidelity.py`)**:
  - Implemented semantic equivalence recognition for physical time (`ms` ↔ `秒`, `min` ↔ `分钟`, `h` ↔ `小时`, `day` ↔ `天`), digital storage (`B` ↔ `KB` ↔ `MB` ↔ `GB` ↔ `TB`), and CJK financial orders of magnitude (`万` ↔ `亿`, `万元` ↔ `千万元` ↔ `亿元`).
  - Automatically pairs and matches quantities across source and output texts to eliminate false-positive blocks under `--source`.
  - Preserves strict anti-fabrication gates: ungrounded percentages (e.g., "降低幅度达 78.8%") or invented figures remain strictly blocked with `fidelity_added` hard failure.
- **Localized Paragraph Rhythmic Monotony Detection (`lint/anti_ai_lint/detector.py`)**:
  - Added `localized_rhythmic_monotony` quality gate (penalty 2.5) for long-form prose ($\ge 600$ characters or $\ge 400$ words).
  - Automatically scans each paragraph for monotonous AI drone: flags paragraphs where $\ge 5$ consecutive sentences exhibit a sentence-length Coefficient of Variation $CV_{len} < 0.20$.
  - Intelligently ignores bullet points, numbered lists, and KPI tables to eliminate false positives on enumeration blocks.
- **DeepSeek v4.1-Flash Advanced Stress Benchmark Suite (`scripts/run_advanced_benchmark.py`)**:
  - Introduced live dual-blind stress test suite with genuine HTTP calls to OpenCode Go endpoint (`https://opencode.ai/zen/go/v1/chat/completions`) using `deepseek-v4.1-flash`.
  - Covers 4 high-difficulty frontiers:
    1. `long_architecture`: 1500+ character cross-datacenter active-active architecture proposal (tests long-form style drift & paragraph cadence).
    2. `financial_unit_fidelity`: Financial core system database migration report under `--source` (tests unit/magnitude equivalence and anti-fabrication).
    3. `adversarial_cliche`: Strategic management draft with 10+ adversarial buzzwords (tests concrete verb restoration).
    4. `multiturn_remediation`: Complex multi-violation prompt (tests pre-conditioning and in-loop self-healing reflection).
  - Evaluated results: 10 live HTTP calls, 29,843 tokens (incl. 17,461 reasoning tokens), 100% HTTP 200, 100% Skill+Tool gate pass rate.
  - Persisted live audit records and generation outputs to `tests/fixtures_advanced/`.
- **Expanded Test Suite (100 Tests)**:
  - Added unit tests for unit/magnitude equivalence, percentage anti-fabrication, and localized paragraph cadence detection, achieving 100/100 tests passing.

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
- **Genuine End-to-End Empirical Benchmark on mimo-v2.6-flash (OpenCode Go Gateway)**:
  - Introduced `scripts/run_mimo_benchmark.py`: a dual-blind evaluation harness running against `mimo-v2.6-flash` via `https://opencode.ai/zen/go/v1/chat/completions`.
  - Zero-mock policy: live per-call network telemetry (HTTP 200 status, latency in ms, token usage including reasoning tokens, and server `response_id`), with any non-200, empty body, truncated, or degenerate output raising an exception and terminating the run.
  - Measured results (8 subjects, 24 live HTTP calls, all 200 OK, 27,976 tokens, 353.5 s): mean penalty 5.50 -> 2.06 (-62.5%), violations 1.75 -> 0.62 (-64.3%), gate pass rate 75.0% -> 100%; solo model in polishing hallucinated "35.7% reduction" and was hard-blocked by `fidelity_added`.
- **DPO Preference Alignment Dataset Export**:
  - Exported verified preference pairs in three formats (`data/mimo_dpo/mimo_dpo.jsonl`, `data/mimo_dpo/mimo_dpo_chatml.jsonl`, `data/mimo_dpo/mimo_dpo_sharegpt.jsonl`, 8 pairs each) generated directly from empirical outputs.
  - Enhanced `scripts/export_dpo_pairs.py` to auto-ingest `tests/fixtures_mimo/` with metadata integration.
- **Academic References & Translation Standards Harmonization**:
  - Cited Kobak et al. peer-reviewed publication: *Science Advances*, 11(27), eadt3813 (2025).
  - Integrated translation and post-editing standards (ISO 17100:2015, ISO 18587:2017, GB/T 19363.1-2008, Yan Fu 1898) across documentation and benchmark reports.

### Changed
- **Purged unverified demonstration artifacts and unified repository on verified empirical benchmark**:
  - Removed all unverified demonstration and mock artifacts (including `tests/fixtures_glm5/`, `scripts/run_glm5_benchmark.py`, and `data/glm5_dpo*`).
  - Completely rewritten `docs/BENCHMARK_REPORT.zh-CN.md` and `docs/BENCHMARK_REPORT.md` end to end around verified empirical `mimo-v2.6-flash` generations, audit logs, and scoreboards.
  - Updated `README.zh-CN.md` and `README.md` Section 2 tables to the genuine empirical benchmark measurements.
  - Unified CI workflows (`.github/workflows/ci.yml`), unit tests (`tests/test_linter.py`), DPO exporters, and DSPy optimizers to rely strictly on verified empirical model outputs (`tests/fixtures_mimo/`).

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
