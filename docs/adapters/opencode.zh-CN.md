# OpenCode 适配器指南

[English](opencode.md) | [简体中文](opencode.zh-CN.md)

## 概述

OpenCode 智能体优先从 `~/.opencode/skills/` 载入技能，并从代码仓库根目录或用户主目录的 `AGENTS.md` 读取全局指令。

---

## 1. 自动安装

使用统一安装脚本指定 `opencode` 目标：

```bash
# 全局用户级安装
./install.sh --target opencode --lang zh

# 指定工作区项目安装
./install.sh --target opencode --dest /path/to/project --lang zh
```

安装流程自动完成：
1. 部署技能规范 `SKILL.md` 到 `~/.opencode/skills/anti-ai-copywriting/SKILL.md`（或工作区）。
2. 在 `AGENTS.md` 中以幂等方式插入包含 `<auto_trigger>` 触发指令的限定规则块（`<!-- BEGIN anti-ai-copywriting -->`）。
3. 在 `~/.local/share/anti-ai-copywriting/install-manifest.json` 中记录目标清单。

---

## 2. OpenCode 拦截插件（Harness² c8 范式）

如需在智能体运行时零容忍机器腔，可在 OpenCode 配置中加载 `plugin/anti-ai-copywriting.ts`：

```typescript
import antiAiPlugin from "./plugin/anti-ai-copywriting";

export default {
  plugins: [antiAiPlugin],
};
```

该插件拦截所有针对 `.md`、`.markdown` 与 `.txt` 文件的 `postToolExecution` 事件，自动调用 `anti-ai-lint --format agent`。当检测到套话或防御性犹豫词时，自动生成结构化修改要求送入智能体上下文驱动重写。

---

## 3. 安全卸载

```bash
./uninstall.sh --target opencode
```

---

## 商标与非关联声明

OpenCode 是开源 AI 智能体运行框架。`anti-ai-copywriting` 是独立开源项目，与 OpenCode 上游维护组织无官方隶属或赞助关系。
