# Codex 适配器指南

[English](codex.md) | [简体中文](codex.zh-CN.md)

## 概述

Codex CLI 及自主编程智能体优先读取代码仓库根目录的 `AGENTS.md`，或用户主配置目录中的 `~/.codex/AGENTS.md`。

---

## 1. 自动安装

使用统一安装脚本指定 `codex` 目标：

```bash
# 全局用户级安装
./install.sh --target codex --lang zh

# 指定工作区项目安装
./install.sh --target codex --dest /path/to/project --lang zh
```

安装流程自动完成：
1. 复制技能规范 `SKILL.md` 到 `~/.codex/skills/anti-ai-copywriting/SKILL.md`（或项目目录）。
2. 在 `AGENTS.md` 中注入包含显式 `<auto_trigger>` 触发标记的限定规则块。
3. 在 `~/.local/share/anti-ai-copywriting/install-manifest.json` 中登记安装路径。

---

## 2. 环内执行钩子（Harness² c8 范式）

Codex 原生支持智能体环内执行钩子。可将本项目的 `.codex/hooks.json` 配置引入项目中：

```json
{
  "$schema": "https://raw.githubusercontent.com/google-research/harness2/main/schemas/hooks.json",
  "version": "1.0.0",
  "hooks": [
    {
      "id": "anti-ai-prose-verifier",
      "event": "post_tool_execution",
      "tools": ["write_to_file", "replace_file_content", "apply_diff"],
      "file_patterns": ["*.md", "*.txt", "*.markdown"],
      "command": "python3 -m anti_ai_lint.cli \"${file_path}\" --format hook --max-score 10.0",
      "on_failure": "block_and_feedback",
      "feedback_format": "agent"
    }
  ]
}
```

每当智能体调用写文件工具修改 markdown 文档后，钩子即时运行 `anti-ai-lint`。若发现套话或防御性免责措辞，会自动反馈至智能体上下文促成重写。

---

## 3. 质量门禁集成

在 CI 流水线或 Git 预提交中添加检查门禁：

```bash
anti-ai-lint path/to/deliverable.md --genre academic --format hook --max-score 8.0
```

---

## 4. 安全卸载

```bash
./uninstall.sh --target codex
```

---

## 商标与非关联声明

Codex 与 OpenAI 是 OpenAI, Inc. 的商标。`anti-ai-copywriting` 是独立的开源项目，与 OpenAI, Inc. 无任何官方关联、赞助或背书关系。
