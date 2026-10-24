# anti-ai-copywriting 文档导航

[English](README.md) | [简体中文](README.zh-CN.md)

欢迎查阅 **anti-ai-copywriting**（中英双语自然语态与学术专业文案引擎）官方文档。

---

## 核心文档目录

- **[实测效果对比与基准评测报告](BENCHMARK_REPORT.zh-CN.md)** ([English](BENCHMARK_REPORT.md))：基于智谱 GLM-5.3 大模型真实端到端推理测定，涵盖 8 大中英双语核心科目（学术、商业、英文顶会、基金申报、科普、社媒评测，以及遵循信息守恒的技术润色与英译中）在「单一模型」vs.「模型+技能工具」双盲对照下的量化指标对比、语言学机理诊断与落地实证数据。
- **[智能体适配器支持总览与安装](adapters/README.zh-CN.md)** ([English](adapters/README.md))：针对主流平台的专用集成指南：
  - [Codex 适配指南](adapters/codex.zh-CN.md) ([English](adapters/codex.md))
  - [Claude Code 适配指南](adapters/claude-code.zh-CN.md) ([English](adapters/claude-code.md))
  - [DeepSeek 适配指南](adapters/deepseek.zh-CN.md) ([English](adapters/deepseek.md))
  - [OpenCode 适配指南](adapters/opencode.zh-CN.md) ([English](adapters/opencode.md))
  - [WorkBuddy 适配指南](adapters/workbuddy.zh-CN.md) ([English](adapters/workbuddy.md))
  - [通用与常见智能体（Cursor、Windsurf、Cline、Aider、Antigravity）适配指南](adapters/generic.zh-CN.md) ([English](adapters/generic.md))
  - [ZCode 适配指南](adapters/zcode.zh-CN.md) ([English](adapters/zcode.md))

---

## 智能体架构范式（Harness² c1..c8）

本项目深度融入 Google Research Harness² 智能体系统设计模式：
- **c1 契约规范**：在 `rules/` 中提供严格受控的文案质量规范边界契约。
- **c5 专属子智能体**：在 `sub_agents/copywriting-editor/AGENT.md` 中实现独立的审校与改写专家角色。
- **c6 主动触发机制**：在规则片段中内置 `<auto_trigger>` 指令促使智能体主动加载技能。
- **c8 环内执行门禁**：通过 `hooks/hooks.json`、`.codex/hooks.json` 与 `plugin/anti-ai-copywriting.ts` 实现工具调用后的实时自动质检。

---

## 商标与非关联声明

文档中提及的所有产品名称、商标、品牌与注册商标均归其各自所有者拥有。在本文档中引用这些名称仅为便于标识和说明兼容性。本项目为独立开源项目，与上述实体无任何官方关联、赞助或背书关系。
