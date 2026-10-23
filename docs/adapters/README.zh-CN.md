# 智能体适配器与集成指南

[English](README.md) | [简体中文](README.zh-CN.md)

本目录提供针对各大主流 AI 编程智能体、自主大模型工作流及企业办公助手的平台适配指南与集成方案。

---

## 适配平台支持清单

| 平台 / 智能体 | 目标标识 | 默认技能安装路径 | 默认规则注入文件 | 环内验证支持方式 | 适配指南链接 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Codex** | `codex` | `~/.codex/skills/anti-ai-copywriting/` | `~/.codex/AGENTS.md` | Harness² c8 工具后置钩子（`.codex/hooks.json`） | [Codex 指南](codex.zh-CN.md) |
| **Claude Code** | `claude` | `~/.claude/skills/anti-ai-copywriting/` | `~/.claude/CLAUDE.md` | Git Pre-commit / 子智能体质检循环 | [Claude Code 指南](claude-code.zh-CN.md) |
| **DeepSeek** | `deepseek` | `~/.deepseek/skills/anti-ai-copywriting/` | `~/.deepseek/AGENTS.md` | CLI 反思循环与 API 系统提示词注入 | [DeepSeek 指南](deepseek.zh-CN.md) |
| **OpenCode** | `opencode` | `~/.opencode/skills/anti-ai-copywriting/` | `~/.opencode/AGENTS.md` | OpenCode 拦截插件（`plugin/anti-ai-copywriting.ts`） | [OpenCode 指南](opencode.zh-CN.md) |
| **WorkBuddy** | `workbuddy` | `~/.workbuddy/skills/anti-ai-copywriting/` | `~/.workbuddy/prompts/anti-ai-rules.md` | 自动化 Webhook / CI 质检门禁 | [WorkBuddy 指南](workbuddy.zh-CN.md) |
| **Cursor** | `cursor` | `.cursor/skills/anti-ai-copywriting/` | `.cursorrules` | MDC 规范定义与终端质检门禁 | [通用 / Cursor](generic.zh-CN.md#cursor) |
| **Windsurf** | `windsurf` | `.windsurf/skills/anti-ai-copywriting/` | `.windsurfrules` | Cascade 全局规则注入 | [通用 / Windsurf](generic.zh-CN.md#windsurf) |
| **Cline** | `cline` | `~/.cline/skills/anti-ai-copywriting/` | `.clinerules` | 任务初始提示词注入 | [通用 / Cline](generic.zh-CN.md#cline) |
| **Aider** | `aider` | `~/.aider/skills/anti-ai-copywriting/` | `CONVENTIONS.md` | Aider `--read` 约定文件参数 | [通用 / Aider](generic.zh-CN.md#aider) |
| **Antigravity** | `antigravity` | `~/.antigravity/skills/anti-ai-copywriting/` | `AGENTS.md` | 智能体系统规则与工具执行验证 | [通用 / Antigravity](generic.zh-CN.md#antigravity) |
| **通用 / 自定义** | `generic` | 通过 `--dest` 自定义路径 | 通过 `--dest` 自定义路径 | 纯 Python 零依赖命令行门禁（`anti-ai-lint`） | [通用适配指南](generic.zh-CN.md) |
| **ZCode** | `zcode` | `~/.zcode/skills/anti-ai-copywriting/` | `~/.zcode/AGENTS.md` | 全局技能引擎直接集成 | [ZCode 指南](zcode.zh-CN.md) |

---

## 快速安装

运行统一安装脚本并指定目标平台与语言版本（`zh` 或 `en`）：

```bash
# 安装到 Codex
./install.sh --target codex --lang zh

# 安装到 Claude Code
./install.sh --target claude --lang zh

# 安装到 DeepSeek
./install.sh --target deepseek --lang zh

# 安装到 OpenCode
./install.sh --target opencode --lang zh

# 安装到 WorkBuddy
./install.sh --target workbuddy --lang zh

# 安装到 Cursor 项目
./install.sh --target cursor --dest /path/to/repo --lang zh

# 安装到 Windsurf 项目
./install.sh --target windsurf --dest /path/to/repo --lang zh

# 安装到通用项目目录
./install.sh --target generic --dest /path/to/repo --lang zh
```

---

## 安全卸载

安全清理已部署的技能与限定规则块并还原备份：

```bash
# 卸载指定全局智能体配置
./uninstall.sh --target codex

# 卸载指定项目或工作区中的配置
./uninstall.sh --target cursor --dest /path/to/repo
./uninstall.sh --dest /path/to/repo

# 卸载所有已登记的目标
./uninstall.sh --all
```

---

## 商标与非关联声明

文档中提及的所有产品名称、商标、品牌与注册商标（包括 Anthropic、Claude、Claude Code、OpenAI、Codex、DeepSeek、Google、Cursor、Windsurf、Codeium、Cline、Aider、WorkBuddy 等）均归其各自所有者拥有。在本文档中引用这些名称仅为便于标识和说明兼容性。本项目为独立开源项目，与上述实体无任何官方关联、赞助或背书关系。
