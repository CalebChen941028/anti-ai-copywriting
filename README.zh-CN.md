# anti-ai-copywriting（反 AI 腔文案引擎）

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**中英双语自然语态与学术专业文案引擎（面向 AI 编程智能体与大模型工作流）。**

系统性消除大模型输出中的恶性欧化、翻译腔、伪学术黑话、公式化煽情排比与防御性免责，恢复母语呼吸感与笃定专业质感。

---

## 核心特性

- **多平台智能体适配**：原生支持 Codex、Claude Code、DeepSeek、OpenCode、WorkBuddy 以及常见智能体（Cursor、Windsurf、Cline、Aider、Antigravity、Harness²、ZCode）。
- **场景锚定与体裁定制（`--genre general|academic|plain`）**：
  - `academic`：严格去防御化、因果逻辑与科学问题导向、APA/JARS 规范统计量、严禁 `如表所示` 套话引表。
  - `plain`：受控白话层（中文单句 $\le 30$ 字，英文 $\le 25$ 词，杜绝“若干/一些/等等”模糊量词）。
  - `general`：全域通用自然语态清洗。
- **全域封锁 AI 腔词汇与套话模板**：彻底封锁 `赋能`、`抓手`、`闭环`、`底层逻辑`、`颗粒度`、`多维度`、`全方位`、`深度融合`、`随着……飞速发展`、`不仅是……更是……` 以及英文 `delve into`、`tapestry of`、`testament to`、`realm`、`navigating the complexities`、`revolutionize`、`leverage`。
- **具象化整改建议（Actionable Remediation）**：每一处检测出的违规均附带明确、可执行的替换词与改写方案。
- **Harness² 架构范式融合（c1..c8）**：
  - **c8 环内验证钩子（In-Loop Verification Hook）**：提供 `hooks/hooks.json` 与 `.codex/hooks.json`，在智能体调用写文件工具后即时运行门禁。
  - **c8 OpenCode 插件**：`plugin/anti-ai-copywriting.ts` 拦截工具执行并在发现机器腔时自动向智能体注入反馈。
  - **c5 专属文案润色子智能体（Copy-Editing Subagent）**：`sub_agents/copywriting-editor/AGENT.md` 定义专属审校专家智能体及调用契约。
  - **c6/c1 显式主动触发契约**：规则片段中内置 `<auto_trigger>` 契约块，驱动智能体主动加载技能规范。
- **零依赖确定性检查工具（`anti-ai-lint`）**：纯 Python 标准库实现，支持 text、json、hook、agent 四种格式及千字归一化扣分（`--max-normalized-score`）。

---

## 安装与部署

### 1. 智能体技能与规则安装

使用统一安装脚本（支持多目标清单追踪与 `--lang zh|en` 语义切换）：

```bash
# 安装到 Codex：
./install.sh --target codex --lang zh

# 安装到 Claude Code CLI：
./install.sh --target claude --lang en

# 安装到 DeepSeek（CLI / API 智能体）：
./install.sh --target deepseek --lang zh

# 安装到 OpenCode：
./install.sh --target opencode --lang zh

# 安装到 WorkBuddy：
./install.sh --target workbuddy --lang zh

# 安装到 Cursor 项目仓库：
./install.sh --target cursor --dest /path/to/project --lang zh

# 安装到 Windsurf 项目仓库：
./install.sh --target windsurf --dest /path/to/project --lang zh

# 安装到 Cline / Aider / Antigravity：
./install.sh --target cline --dest /path/to/project --lang zh
./install.sh --target aider --dest /path/to/project --lang zh
./install.sh --target antigravity --lang zh

# 安装到 ZCode：
./install.sh --target zcode --lang zh

# 安装到通用指定路径：
./install.sh --target generic --dest /path/to/project --lang zh
```

各平台详细集成说明与架构设计，请参阅 [智能体适配器支持总览与安装文档](docs/adapters/README.zh-CN.md)。

---

### 2. 独立检查工具（`anti-ai-lint`）

在本地虚拟环境中安装：

```bash
pip install ./lint
```

或者直接以模块形式运行（免安装）：

```bash
python3 -m anti_ai_lint /path/to/document.md --max-score 8.0
```

---

## 检查工具使用示例与格式

```bash
# 默认文本检查
anti-ai-lint paper.md

# 学术场景 + 钩子格式（适用于 CI 流程或 Git Pre-commit）
anti-ai-lint paper.md --genre academic --format hook --max-score 8.0

# 受控白话层检查 + 智能体反馈格式（直接返回给大模型反思循环）
anti-ai-lint guide.md --genre plain --format agent

# 基于千字密度的归一化扣分门禁
anti-ai-lint docs/ --max-normalized-score 25.0 --format json
```

### 输出格式说明 (`--format`)

- `text`：包含精确行列号、上下文与改写建议的详尽报告。
- `json`：机器可读的结构化 AST 与指标数据。
- `hook`：极简格式，专为 Git pre-commit 与 Harness² 环内钩子设计。
- `agent`：结构化 `<anti-ai-lint-feedback>` 标记格式，直接注入智能体上下文促成重写。

---

## 卸载与还原

支持针对单一目标或全部目标安全卸载，保留用户既有规则并清理空目录：

```bash
# 卸载指定目标（全局或特定项目）
./uninstall.sh --target codex
./uninstall.sh --target cursor --dest /path/to/project
./uninstall.sh --dest /path/to/project

# 卸载全部已安装目标
./uninstall.sh --all
```

---

## 回归测试集

运行全量测试套件（涵盖 6 大场景回归、代码块隔离、分句精度、体裁规则、归一化分数与多平台安装器集成）：

```bash
python3 -m unittest discover -s tests
```

---

## 引用与致谢

- **ASD-STE100**：受控白话层在设计思路上借鉴了 ASD-STE100 简化技术英文的受控语言通用原则（该规范版权归 ASD 所有，本项目全部规则与检测逻辑均为自主编写）。
- **Google Research Harness²**：架构工程模式融入了 Google Research Harness² 智能体系统范式（c1 契约规范、c5 子智能体分工、c6 主动触发、c8 环内实时校验）。

---

## 商标与非关联声明

文档与代码中提及的所有产品名称、商标、品牌与注册商标（包括 Anthropic、Claude、Claude Code、OpenAI、Codex、DeepSeek、Google、Cursor、Windsurf、Codeium、Cline、Aider、WorkBuddy 等）均归其各自所有者拥有。在本项目中引用这些名称仅为便于标识和说明兼容性。本项目为独立开源项目，与上述实体无任何官方关联、赞助或背书关系。

---

## 开源许可证

[MIT](LICENSE) © 2026 Liangliang Chen
