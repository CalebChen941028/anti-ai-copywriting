# Antigravity Integration Guide (Anti-AI Copywriting & Natural Prose)

[English](antigravity.md) | [简体中文](antigravity.zh-CN.md)

This guide covers integrating `anti-ai-copywriting` with Google DeepMind's Antigravity agentic coding framework.

---

## 1. Quick Installation

Install into your Antigravity environment:

```bash
./install.sh --target antigravity --lang en
```

This registers:
- `~/.antigravity/AGENTS.md` (or project-level `AGENTS.md`) with `<auto_trigger>` rules.
- `~/.antigravity/skills/anti-ai-copywriting/SKILL.md` skill instructions.

---

## 2. In-Loop Verification Hook & Subagent Roles

Antigravity operates with Google Research Harness² protocols:
- **c1 / c6 Autotriggers**: When writing markdown or documentation, Antigravity automatically activates the `anti-ai-copywriting` skill.
- **c5 Specialist Subagent**: Delegate text polishing to the `copywriting-editor` subagent located at `sub_agents/copywriting-editor/AGENT.md`.
- **c8 In-Loop Gate**: Run `anti-ai-lint <file> --format hook` after file write operations to detect any regression.
- **MCP Server Integration**: Start the stdio MCP server `anti-ai-mcp` or `python3 -m anti_ai_lint.mcp_server` to provide Antigravity with first-class `lint_prose` and `remediate_violation` tools.
