# Claude Code 适配器指南

[English](claude-code.md) | [简体中文](claude-code.zh-CN.md)

## 概述

Claude Code 命令行工具优先读取项目根目录的 `CLAUDE.md` 或用户全局配置文件 `~/.claude/CLAUDE.md`。其扩展技能存放在 `~/.claude/skills/` 目录。

---

## 1. 自动安装

使用统一安装脚本指定 `claude` 目标：

```bash
# 全局用户级安装
./install.sh --target claude --lang zh

# 指定工作区项目安装
./install.sh --target claude --dest /path/to/project --lang zh
```

安装流程自动完成：
1. 复制技能规范 `SKILL.md` 到 `~/.claude/skills/anti-ai-copywriting/SKILL.md`（或工作区目录）。
2. 在 `CLAUDE.md` 中注入包含显式 `<auto_trigger>` 触发标记的限定规则块。
3. 在 `~/.local/share/anti-ai-copywriting/install-manifest.json` 中登记安装路径。

---

## 2. 环内子智能体协同（Harness² c5 范式）

对于长篇文案润色或学术论文起草任务，Claude Code 可调用 `sub_agents/copywriting-editor/AGENT.md` 中定义的专属审校子智能体：

```markdown
调用 copywriting-editor 子智能体审校并润色 docs/architecture.md：
- 应用学术语态标准
- 清除所有恶性欧化与套话黑话
- 运行 anti-ai-lint --max-score 5.0 校验门禁
```

---

## 3. Git 预提交钩子与 CI 质量门禁

### Git Pre-Commit 钩子

在本地配置预提交检查，阻断带机器腔文案的提交：

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit
git diff --cached --name-only --diff-filter=ACM | grep -E '\.(md|markdown|txt)$' | while read -r file; do
  if [ -f "$file" ]; then
    python3 -m anti_ai_lint "$file" --genre general --format hook --max-score 8.0 || exit 1
  fi
done
```

### GitHub Actions 流水线集成

在 `.github/workflows/ci.yml` 中添加校验步骤：

```yaml
- name: 文案自然度质检门禁
  run: |
    python3 -m anti_ai_lint docs/ README.zh-CN.md --max-score 8.0 --format text
```

---

## 4. 安全卸载

还原原文件并彻底移除注入的规则片段：

```bash
./uninstall.sh --target claude
```

---

## 商标与非关联声明

Claude 与 Claude Code 是 Anthropic PBC 的商标。`anti-ai-copywriting` 是独立的开源项目，与 Anthropic PBC 无任何官方关联、赞助或背书关系。
