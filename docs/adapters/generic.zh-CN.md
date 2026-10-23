# 通用与常见智能体适配器指南

[English](generic.md) | [简体中文](generic.zh-CN.md)

## 概述

本指南介绍如何在常见 AI 编程助手与自主智能体框架中部署 `anti-ai-copywriting`，涵盖 **Cursor**、**Windsurf**、**Cline**、**Aider**、**Antigravity** 以及各类自定义大模型流水线。

---

## 1. 适配平台与文件对应表

| 工具 / 框架 | 目标参数 | 生成规则文件 | 本地技能目录 |
| :--- | :--- | :--- | :--- |
| **Cursor** | `--target cursor` | `.cursorrules`（或 `.cursor/rules/*.mdc`） | `.cursor/skills/anti-ai-copywriting/` |
| **Windsurf** | `--target windsurf` | `.windsurfrules` | `.windsurf/skills/anti-ai-copywriting/` |
| **Cline** | `--target cline` | `.clinerules` | `~/.cline/skills/anti-ai-copywriting/` |
| **Aider** | `--target aider` | `CONVENTIONS.md` / `~/.aider.conventions.md` | `~/.aider/skills/anti-ai-copywriting/` |
| **Antigravity** | `--target antigravity`| `AGENTS.md` | `~/.antigravity/skills/anti-ai-copywriting/` |
| **自定义智能体** | `--target generic` | 通过 `--dest` 指定 | 通过 `--dest` 指定 |

---

## 2. 各平台安装配置

### Cursor

#### 方案 A：项目根目录 `.cursorrules`
将限定规则块安装到代码仓库根目录：
```bash
./install.sh --target cursor --dest /path/to/project --lang zh
```
Cursor 会在智能体每次执行编辑和文档任务时自动加载 `.cursorrules`。

#### 方案 B：Cursor MDC 规范文件
部署为 `.cursor/rules/anti-ai.mdc` 规则卡片：
```bash
./install.sh --target cursor --dest /path/to/project/.cursor/rules/anti-ai.mdc --lang zh
```

---

### Windsurf

Windsurf (Cascade) 支持从项目根目录读取 `.windsurfrules`：
```bash
./install.sh --target windsurf --dest /path/to/project --lang zh
```
Cascade 在修改代码注释、编写技术文档或重构文本时将严格遵循反 AI 表达准则。

---

### Cline

安装至项目目录或全局用户目录：
```bash
# 项目目录
./install.sh --target cline --dest /path/to/project --lang zh

# 全局主目录
./install.sh --target cline --lang zh
```
Cline 在启动每一个工作区任务时会自动读取 `.clinerules` 规则。

---

### Aider

Aider 支持在交互会话中通过约定文件载入文案规则：
```bash
# 将规则安装为项目的约定文件
./install.sh --target aider --dest /path/to/project --lang zh

# 启动 Aider 时加载该文件
aider --read CONVENTIONS.md
```

也可在 `.aider.conf.yml` 中配置默认读取：
```yaml
read:
  - CONVENTIONS.md
```

---

### Antigravity

Antigravity 多智能体系统从 `AGENTS.md` 读取全局技能与规则契约：
```bash
./install.sh --target antigravity --lang zh
```

---

### 自定义智能体与大模型流水线

针对 LangChain、LlamaIndex、AutoGen、CrewAI 等自定义智能体框架：
1. 导出规则到指定路径：
   ```bash
   ./install.sh --target generic --dest /path/to/prompts --lang zh
   ```
2. 在应用代码中读取 `rules/AGENTS.snippet.zh.md` 并注入系统提示词（System Prompt）。

---

## 3. CI 流水线与 Git Pre-commit 自动化质检

无论选用何种智能体框架，均可将 `anti-ai-lint` 作为持续集成检查门禁：

```bash
# 检查整个文档目录
python3 -m anti_ai_lint docs/ --max-score 8.0 --format text

# 结合千字归一化扣分上限检查学术文本
python3 -m anti_ai_lint paper.md --genre academic --max-normalized-score 20.0
```

---

## 4. 安全卸载

```bash
# 卸载指定目标
./uninstall.sh --target cursor
./uninstall.sh --target windsurf
./uninstall.sh --target cline
./uninstall.sh --target aider
./uninstall.sh --target antigravity
./uninstall.sh --target generic
```

---

## 商标与非关联声明

Cursor 是 Anysphere, Inc. 的产品。Windsurf 是 Codeium 的产品。Cline 与 Aider 是开源项目。所有商标、注册商标与标识均归其各自所有者拥有。`anti-ai-copywriting` 是独立的开源项目，与上述实体无任何官方关联、赞助或背书关系。
