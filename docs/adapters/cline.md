# Cline Integration Guide (Anti-AI Copywriting & Natural Prose)

[English](cline.md) | [简体中文](cline.zh-CN.md)

This guide covers integrating `anti-ai-copywriting` with Cline (formerly Claude Dev) using `.clinerules` and the MCP server.

---

## 1. Quick Installation

Install for a specific project:

```bash
./install.sh --target cline --dest /path/to/your/project --lang en
```

This injects:
1. Anti-AI writing rules into `.clinerules`.
2. Skill instructions into `skills/anti-ai-copywriting/SKILL.md`.

---

## 2. Cline MCP Settings

Add to Cline MCP settings (`cline_mcp_settings.json`):

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

Cline can then run `lint_prose` and `remediate_violation` during task execution.
