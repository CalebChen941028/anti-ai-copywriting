# ZCode 适配器指南

[English](zcode.md) | [简体中文](zcode.zh-CN.md)

## 概述

在 ZCode 环境中，`anti-ai-copywriting` 作为全局技能部署至 `~/.zcode/skills/anti-ai-copywriting/`，并将限定规则注入 `~/.zcode/AGENTS.md`。

---

## 1. 自动安装

使用统一安装脚本指定 `zcode` 目标：

```bash
# 全局用户级安装
./install.sh --target zcode --lang zh

# 指定工作区项目安装
./install.sh --target zcode --dest /path/to/project --lang zh
```

安装流程自动完成：
1. 安装技能规范 `SKILL.md` 到 `~/.zcode/skills/anti-ai-copywriting/SKILL.md`（或工作区）。
2. 在 `AGENTS.md` 中注入包含显式 `<auto_trigger>` 触发指令的限定标记块（`<!-- BEGIN anti-ai-copywriting v0.5.0 -->`）。
3. 在 `~/.local/share/anti-ai-copywriting/install-manifest.json` 中登记安装路径。

---

## 2. 质量门禁集成

在 CI 流水线或 Git Pre-commit 流程中执行 `anti-ai-lint`：

```bash
python3 -m anti_ai_lint docs/ --max-score 8.0 --format text
```

---

## 3. 安全卸载

安全清理并还原配置：

```bash
./uninstall.sh --target zcode
```

---

## 商标与非关联声明

ZCode 是一款智能体研发平台。`anti-ai-copywriting` 是独立的开源项目，与 ZCode 及其所属实体无任何官方关联、赞助或背书关系。
