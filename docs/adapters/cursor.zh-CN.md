# Cursor 适配与集成指南（自然语态与学术文案引擎）

[English](cursor.md) | [简体中文](cursor.zh-CN.md)

本指南说明如何在 Cursor IDE 中接入 `anti-ai-copywriting`，结合 `.cursorrules`、技能目录以及 MCP (Model Context Protocol) 协议实现全自动自然语态守护。

---

## 1. 快速安装

针对目标项目仓库执行统一安装脚本：

```bash
./install.sh --target cursor --dest /path/to/your/project --lang zh
```

安装程序将自动完成：
1. 向项目根目录 `.cursorrules` 注入自然语态守护规则块。
2. 将核心规范部署至 `.cursor/skills/anti-ai-copywriting/SKILL.md`。

---

## 2. 在 Cursor 中配置 MCP 原生工具服务

Cursor 原生支持 Model Context Protocol (MCP)。通过配置 MCP Server，Cursor Composer 与智能体可在对话中直接调用门禁质检：

在项目根目录 `.cursor/mcp.json`（或全局 Cursor 设置 -> Features -> MCP）中添加：

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

配置后，Cursor 可自动调用以下工具：
- `lint_prose`：接收选中文本或文件路径，返回 AST 掩码与节奏分析报告。
- `remediate_violation`：针对特定套话提供可替换的具体动词与重写方案。
- `get_style_contract`：获取指定场景（academic/general/plain）的语态公理。

---

## 3. 质检与工作流闭环

在终端或任务循环中运行确定性质检门禁：

```bash
anti-ai-lint docs/paper.md --genre academic --max-score 10.0
```
