# Cursor Integration Guide (Anti-AI Copywriting & Natural Prose)

[English](cursor.md) | [简体中文](cursor.zh-CN.md)

This guide explains how to integrate `anti-ai-copywriting` with Cursor using `.cursorrules`, skill directory structures, and the Model Context Protocol (MCP) server.

---

## 1. Quick Installation

Run the unified installer targeting your project directory:

```bash
./install.sh --target cursor --dest /path/to/your/project --lang en
```

This injects:
1. Anti-AI writing rules into `/path/to/your/project/.cursorrules`.
2. The core skill instructions into `/path/to/your/project/.cursor/skills/anti-ai-copywriting/SKILL.md`.

---

## 2. MCP Server Configuration in Cursor

Cursor natively supports Model Context Protocol (MCP) servers. To connect `anti-ai-lint` as a native MCP tool in Cursor:

Add to your project's `.cursor/mcp.json` (or Cursor Settings -> Features -> MCP):

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

Once configured, Cursor Composer and Agent mode can invoke:
- `lint_prose`: Run deterministic AST & cadence linting on active files or drafts.
- `remediate_violation`: Request actionable rewrite suggestions.
- `get_style_contract`: Query genre-specific style axioms (academic, plain, general).

---

## 3. Workflow & Verification

When drafting or editing prose in Cursor:
1. Cursor's system prompt loads the rules from `.cursorrules`.
2. When saving or reviewing documents, execute:
   ```bash
   anti-ai-lint /path/to/document.md --genre academic --max-score 10.0
   ```
3. If violations are reported, Cursor's agent will reflect on the feedback and produce clean, natural prose.
