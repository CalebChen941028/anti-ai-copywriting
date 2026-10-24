# anti-ai-copywriting Documentation

[English](README.md) | [简体中文](README.zh-CN.md)

Welcome to the documentation for **anti-ai-copywriting**, the bilingual natural prose and academic pro-voice engine for AI coding agents and LLMs.

---

## Documentation Structure

- **[Empirical Benchmark & Evaluation Report](BENCHMARK_REPORT.md)** ([中文](BENCHMARK_REPORT.zh-CN.md)): Comprehensive before-and-after empirical case studies and quantitative metrics across 6 core bilingual scenarios (Academic, Business, English Academic, Grant, PopSci, Social Reviews).
- **[Agent Adapters & Integration Matrix](adapters/README.md)** ([中文](adapters/README.zh-CN.md)): Platform-specific setup guides for:
  - [Codex Adapter](adapters/codex.md) ([中文](adapters/codex.zh-CN.md))
  - [Claude Code Adapter](adapters/claude-code.md) ([中文](adapters/claude-code.zh-CN.md))
  - [DeepSeek Adapter](adapters/deepseek.md) ([中文](adapters/deepseek.zh-CN.md))
  - [OpenCode Adapter](adapters/opencode.md) ([中文](adapters/opencode.zh-CN.md))
  - [WorkBuddy Adapter](adapters/workbuddy.md) ([中文](adapters/workbuddy.zh-CN.md))
  - [Generic & Common Agents (Cursor, Windsurf, Cline, Aider, Antigravity)](adapters/generic.md) ([中文](adapters/generic.zh-CN.md))
  - [ZCode Adapter](adapters/zcode.md) ([中文](adapters/zcode.zh-CN.md))

---

## Architectural Patterns (Harness² c1..c8)

The project incorporates agent integration patterns from Google Research Harness² architectures:
- **c1 Specification Contracts**: Formal boundary contracts for prose quality in `rules/`.
- **c5 Specialist Subagent**: Dedicated copy-editing subagent defined in `sub_agents/copywriting-editor/AGENT.md`.
- **c6 Autotriggers**: `<auto_trigger>` directives in rules snippets to proactively prompt skills loading.
- **c8 In-Loop Verification Hooks**: Automated prose linting hooks in `hooks/hooks.json`, `.codex/hooks.json`, and `plugin/anti-ai-copywriting.ts`.

---

## Trademark & Non-Affiliation Notice

All product names, logos, brands, trademarks, and registered trademarks mentioned throughout this documentation are property of their respective owners. Their reference does not imply any affiliation with, endorsement by, or sponsorship by their respective holders.
