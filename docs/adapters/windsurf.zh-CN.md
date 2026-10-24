# Windsurf 适配与集成指南（自然语态与学术文案引擎）

[English](windsurf.md) | [简体中文](windsurf.zh-CN.md)

本指南说明如何在 Codeium Windsurf 环境中配置 `anti-ai-copywriting`，利用 `.windsurfrules` 与 MCP 服务赋能 Cascade 智能体。

---

## 1. 快速安装

针对项目仓库执行安装：

```bash
./install.sh --target windsurf --dest /path/to/your/project --lang zh
```

安装程序将在项目根目录下配置 `.windsurfrules` 并将技能文件写入 `.windsurf/skills/anti-ai-copywriting/SKILL.md`。

---

## 2. Windsurf MCP 工具配置

在 Windsurf MCP 配置文件（`~/.codeium/windsurf/mcp_config.json`）中添加服务：

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

Cascade 智能体可在编辑过程中自动触发 `lint_prose` 质量门禁与 `remediate_violation` 词汇修复建议。
