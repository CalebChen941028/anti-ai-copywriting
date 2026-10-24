# Cline 适配与集成指南（自然语态与学术文案引擎）

[English](cline.md) | [简体中文](cline.zh-CN.md)

本指南说明如何在 Cline（原 Claude Dev）智能体中集成 `anti-ai-copywriting`。

---

## 1. 快速安装

针对项目执行：

```bash
./install.sh --target cline --dest /path/to/your/project --lang zh
```

安装程序将在项目目录中配置 `.clinerules` 与 `skills/anti-ai-copywriting/SKILL.md`。

---

## 2. Cline MCP 工具配置

在 Cline MCP 设置文件 `cline_mcp_settings.json` 中添加：

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
