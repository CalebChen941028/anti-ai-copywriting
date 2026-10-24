# Windsurf Integration Guide (Anti-AI Copywriting & Natural Prose)

[English](windsurf.md) | [简体中文](windsurf.zh-CN.md)

This guide covers integrating `anti-ai-copywriting` with Codeium Windsurf via `.windsurfrules` and Model Context Protocol (MCP) tooling.

---

## 1. Quick Installation

Run the unified installer targeting your Windsurf workspace:

```bash
./install.sh --target windsurf --dest /path/to/your/project --lang en
```

This sets up:
1. Writing conventions in `/path/to/your/project/.windsurfrules`.
2. Skill instructions in `/path/to/your/project/.windsurf/skills/anti-ai-copywriting/SKILL.md`.

---

## 2. Windsurf MCP Server Configuration

Add the `anti-ai-copywriting` MCP server to Windsurf's MCP configuration (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "anti-ai-copywriting": {
      "command": "python3",
      "args": [
        "-m",
        "anti_ai_lint.mcp_server"
      ]
    }
  }
}
```

Windsurf's Cascade agent will automatically discover the tools `lint_prose`, `remediate_violation`, and `get_style_contract`.
