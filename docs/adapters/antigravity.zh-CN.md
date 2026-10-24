# Antigravity 适配与集成指南（自然语态与学术文案引擎）

[English](antigravity.md) | [简体中文](antigravity.zh-CN.md)

本指南说明如何在 Google DeepMind Antigravity 智能体编程环境中接入 `anti-ai-copywriting`。

---

## 1. 快速安装

针对 Antigravity 环境执行安装：

```bash
./install.sh --target antigravity --lang zh
```

安装程序将在 `~/.antigravity/`（或项目级目录）配置 `AGENTS.md` 规则并安装 `skills/anti-ai-copywriting/SKILL.md`。

---

## 2. 深度 Harness² 闭环与专职子智能体

Antigravity 原生支持 Harness² 多智能体协同协议：
- **c1/c6 自动触发器 (`<auto_trigger>`)**：在起草论文、文档、专栏时静默加载语态规范。
- **c5 专职润色子智能体 (`copywriting-editor`)**：可将初稿改写委托给 `sub_agents/copywriting-editor/AGENT.md`，执行高精度自检。
- **c8 环内质检门禁**：通过在写文件后执行 `anti-ai-lint <file> --format hook`，违规即时拦截并注入 `<anti-ai-lint-feedback>`。
- **MCP 原生服务**：运行 `anti-ai-mcp` 或 `python3 -m anti_ai_lint.mcp_server`，向智能体开放 `lint_prose`、`remediate_violation` 与 `get_style_contract` 工具。
