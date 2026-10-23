# Agent Adapters & Integration Guides

[English](README.md) | [简体中文](README.zh-CN.md)

This directory provides platform-specific integration guides and adapters for deploying `anti-ai-copywriting` across AI coding agents, autonomous LLM loops, and enterprise workspace assistants.

---

## Supported Environments Matrix

| Platform / Agent | Target Identifier | Default Skill Path | Default Rule File | In-Loop Verification Support | Guide Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Codex** | `codex` | `~/.codex/skills/anti-ai-copywriting/` | `~/.codex/AGENTS.md` | Harness² c8 Post-Tool Hooks (`.codex/hooks.json`) | [Codex Guide](codex.md) |
| **Claude Code** | `claude` | `~/.claude/skills/anti-ai-copywriting/` | `~/.claude/CLAUDE.md` | Pre-commit / Subagent quality gate | [Claude Code Guide](claude-code.md) |
| **DeepSeek** | `deepseek` | `~/.deepseek/skills/anti-ai-copywriting/` | `~/.deepseek/AGENTS.md` | CLI reflection loop & API system prompt | [DeepSeek Guide](deepseek.md) |
| **OpenCode** | `opencode` | `~/.opencode/skills/anti-ai-copywriting/` | `~/.opencode/AGENTS.md` | OpenCode Plugin (`plugin/anti-ai-copywriting.ts`) | [OpenCode Guide](opencode.md) |
| **WorkBuddy** | `workbuddy` | `~/.workbuddy/skills/anti-ai-copywriting/` | `~/.workbuddy/prompts/anti-ai-rules.md` | Webhook / CI quality gate | [WorkBuddy Guide](workbuddy.md) |
| **Cursor** | `cursor` | `.cursor/skills/anti-ai-copywriting/` | `.cursorrules` | MDC rule definition & terminal lint gate | [Generic / Cursor](generic.md#cursor) |
| **Windsurf** | `windsurf` | `.windsurf/skills/anti-ai-copywriting/` | `.windsurfrules` | Cascade global rule injection | [Generic / Windsurf](generic.md#windsurf) |
| **Cline** | `cline` | `~/.cline/skills/anti-ai-copywriting/` | `.clinerules` | Task initialization prompt injection | [Generic / Cline](generic.md#cline) |
| **Aider** | `aider` | `~/.aider/skills/anti-ai-copywriting/` | `CONVENTIONS.md` | Aider `--read` conventions parameter | [Generic / Aider](generic.md#aider) |
| **Antigravity** | `antigravity` | `~/.antigravity/skills/anti-ai-copywriting/` | `AGENTS.md` | Agent system prompt & tool verification | [Generic / Antigravity](generic.md#antigravity) |
| **Generic / Custom** | `generic` | Custom path via `--dest` | Custom path via `--dest` | Deterministic CLI gate (`anti-ai-lint`) | [Generic Guide](generic.md) |
| **ZCode** | `zcode` | `~/.zcode/skills/anti-ai-copywriting/` | `~/.zcode/AGENTS.md` | Global skills engine integration | [ZCode Guide](zcode.md) |

---

## Quick Installation

Run the unified installer and specify your target platform and preferred language (`zh` or `en`):

```bash
# Install for Codex
./install.sh --target codex --lang en

# Install for Claude Code
./install.sh --target claude --lang en

# Install for DeepSeek
./install.sh --target deepseek --lang en

# Install for OpenCode
./install.sh --target opencode --lang en

# Install for WorkBuddy
./install.sh --target workbuddy --lang zh

# Install for Cursor into a repository
./install.sh --target cursor --dest /path/to/repo --lang en

# Install for Windsurf into a repository
./install.sh --target windsurf --dest /path/to/repo --lang en

# Install for generic workspace
./install.sh --target generic --dest /path/to/repo --lang en
```

---

## Trademark & Non-Affiliation Notice

All product names, logos, brands, trademarks, and registered trademarks (including Anthropic, Claude, Claude Code, OpenAI, Codex, DeepSeek, Google, Cursor, Windsurf, Codeium, Cline, Aider, WorkBuddy, and others) are the property of their respective owners. Their use in this documentation is solely for identification and compatibility purposes. anti-ai-copywriting is an independent open-source project and is not affiliated with, endorsed by, or sponsored by any of these entities.
