# Aider 适配与集成指南（自然语态与学术文案引擎）

[English](aider.md) | [简体中文](aider.zh-CN.md)

本指南说明如何在 Aider 命令行结对编程工具中接入 `anti-ai-copywriting`。

---

## 1. 快速安装

针对项目执行：

```bash
./install.sh --target aider --dest /path/to/your/project --lang zh
```

安装程序将在项目目录中配置 `CONVENTIONS.md`（或全局 `~/.aider.conventions.md`）与 `skills/anti-ai-copywriting/SKILL.md`。

---

## 2. 在 Aider 中生效

启动 Aider 时加载约定规范：

```bash
aider --read CONVENTIONS.md
```
在提交前运行 `anti-ai-lint` 实施确定性质检门禁。
