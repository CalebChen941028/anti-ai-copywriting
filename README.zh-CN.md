# anti-ai-copywriting（自然语态与学术文案引擎）

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![Version: 0.4.0](https://img.shields.io/badge/version-0.4.0-green.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**中英双语自然语态与学术专业文案引擎（面向 AI 编程智能体与大模型工作流）。**

系统性消除大模型输出中的恶性欧化、翻译腔、伪学术黑话、公式化煽情排比与防御性免责，恢复母语呼吸感与笃定专业质感。

---

## 1. 系统定位与行业范式对比

当前市面上的 AI 文本工具普遍落入两类极端：一类是**事后惩罚型检测器**，对非母语作者误杀率高且无法指导写作；另一类是**粗暴同义词乱换的商业降重器**，严重摧毁学术与工程写作所必须的术语纪律与因果链条。`anti-ai-copywriting` 定位于**主动式先验生成约束与环内确定性验证门禁**。

| 评估维度 | 被动检测工具<br>*(Turnitin, GPTZero, Copyleaks)* | 商业降重黑盒<br>*(Undetectable AI, HIX Bypass)* | `anti-ai-copywriting`<br>*(本项目)* |
| :--- | :--- | :--- | :--- |
| **干预时机** | 事后打分；在用户起草后进行被动判定 | 事后粗暴改写 | **先验生成约束** (`<auto_trigger>`) + **环内确定性门禁** |
| **术语与因果纪律** | 无（仅负责标记） | 盲目同义词换装，破坏孟德尔随机化、生态效度等专业术语 | **严格术语纪律与因果动词校准**，科学事实绝不降维换词 |
| **文体节奏建模** | 依赖黑盒困惑度/波动度打分 | 制造不通顺病句逃避检测 | **纯标准库句长波动变异系数** ($CV_{len} \ge 0.28$) 与 **MATTR** (窗口50) |
| **词汇实证依据** | 不透明启发式规则 | 人工收集的同义词替换表 | **Nature 2024 PubMed 1400万篇论文超额词表** + **朱德熙形式动词闭集** |
| **AI 工程生态** | 付费 Web 控制台 / 限额 API | 网页订阅制付费墙 | **零依赖 CLI**、**原生 MCP 服务**、**GitHub Action** 与 **DPO 语料飞轮** |

---

## 2. 工具加载前后实测效果对比（Before vs. After Benchmark）

> [!NOTE]
> 完整 6 大场景实测案例详析、指标推导、语言学病理诊断与复现指南请参阅：**[全量实测对比与基准评测报告 (docs/BENCHMARK_REPORT.zh-CN.md)](docs/BENCHMARK_REPORT.zh-CN.md)**。

基于项目内置的 6 大核心中英双语标准测试场景（`tests/fixtures/`，涵盖学术论文、商业管理备忘录、英文顶会论文、国家科研基金申报、前沿科普专栏与社交数码实测），智能体加载 `anti-ai-copywriting` 前后的量化实测对比如下：

| 评测场景分类 | 语体模式 | 加载前 AI 扣分 (Before) | 加载后扣分 (After) | 扣分降幅 | AI 违规项数 | 助词“的”密度 | 门禁判定 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **学术论文摘要** (`academic`) | 学术级 | 61.5 分 | **0.0 分** | **-100.0%** | 15 处 -> **0 处** | 5.85% -> **3.12%** | ❌ 拦截 -> **✅ 放行** |
| **商业管理备忘** (`business`) | 通用级 | 51.5 分 | **0.0 分** | **-100.0%** | 13 处 -> **0 处** | 5.88% -> **1.75%** | ❌ 拦截 -> **✅ 放行** |
| **英文顶会论文** (`en_academic`) | 英文学术 | 55.5 分 | **0.0 分** | **-100.0%** | 17 处 -> **0 处** | (Nature超额词清零) | ❌ 拦截 -> **✅ 放行** |
| **科研基金申报** (`grant`) | 学术级 | 39.5 分 | **0.0 分** | **-100.0%** | 10 处 -> **0 处** | 3.47% -> **0.55%** | ❌ 拦截 -> **✅ 放行** |
| **前沿科普专栏** (`popsci`) | 通用级 | 47.0 分 | **0.0 分** | **-100.0%** | 12 处 -> **0 处** | 6.06% -> **1.97%** | ❌ 拦截 -> **✅ 放行** |
| **社交数码实测** (`social`) | 通用级 | 41.0 分 | **0.0 分** | **-100.0%** | 10 处 -> **0 处** | 7.09% -> **1.74%** | ❌ 拦截 -> **✅ 放行** |
| **全场景宏观均值** | - | **49.3 分** | **0.0 分** | **-100.0%** | **12.8 处 -> 0 处** | **5.67% -> 1.83%** | **0% -> 100% 通过** |

- **扣分与违规项彻底清零**：消除 100% 的 AI 恶性套话、互联网黑话义肢与机器假大空升华。
- **虚词密度骤降 67.7%**：消除机器翻译腔中粘连的多重定语修饰，还原强动词驱动的母语骨力。
- **打破匀速机器蜂鸣**：通过信息论长短句节奏变异（$CV_{len} \ge 0.28$）与 MATTR（窗口 50）词汇丰富度驱动，赋予文本纯正自然的母语呼吸感。

---

## 3. 核心架构与 AI 前沿方法学

- **信息论节奏感度量（Burstiness & UID 均匀信息密度假说）**：
  - 基于纯 Python 标准库实现句长变异系数（Coefficient of Variation, $CV_{len} = \sigma / \mu$）。
  - 当段落句数 $\ge 6$ 且 $CV_{len} < 0.28$ 时，自动判定为 `rhythmic_monotony`（节奏呆滞单调，扣 3.5 分），打破大模型常见的 20 词/30 字匀速机器嗡鸣感。
  - 引入滑动窗口词汇丰富度（MATTR / Moving-Average Type-Token Ratio，窗口 50），避免传统 TTR 受文本长度影响的问题。
- **Kobak et al. 2024 Nature/Science Advances 科学论文超额词频突变模型**：
  - 基于 PubMed 1400 万篇论文摘要实证统计，建立基于对数优势比（Log-Odds Ratio）的动态惩罚分级：
    - **Tier S（极高跃升，扣 5.0 分）**：`delve`, `delve into`, `delving into`, `tapestry of`, `intricate tapestry`, `meticulously`, `testament to`。
    - **Tier A（中高跃升，扣 3.5 分）**：`realm`, `realm of`, `intricate`, `pivotal role`, `pivotal`, `beacon of`, `commendable`, `foster`, `navigating complexities`, `unwavering`。
    - **Tier B（高频通用，扣 2.0 分）**：`comprehensive`, `robust`, `leverage`, `utilize`, `seamless integration`, `seamless`, `seamlessly`, `multifaceted`, `myriad`, `revolutionize`。
- **汉语形式动词/轻动词结构（Light Verb Constructions, LVC）闭集**：
  - 朱德熙现代汉语形式动词闭集：`进行|开展|展开|作出|予以|给以|给予|加以|具有|得到|受到|作|做|致以`。
  - 名物化动作靶点扩充：`分析|探讨|调研|考察|评估|测评|审校|整改|梳理|阐述|测查|优化|迭代|部署|排查|总结|研究|复盘`。
  - 自动提供动作名词去名物化复原规则（如将“针对系统展开了全面的性能测评”精简为“全面测评了系统性能”）。
- **Model Context Protocol (MCP) 原生工具服务**：
  - 零外部依赖的纯标准库 JSON-RPC 2.0 stdio MCP 服务（`anti-ai-mcp` 或 `python3 -m anti_ai_lint.mcp_server`）。
  - 面向 Cursor、Claude Code、Windsurf、Zed、Cline 开放三大原子工具：`lint_prose`、`remediate_violation` 与 `get_style_contract`。
- **现代化 AI 工程交付体系**：
  - 官方 GitHub Action (`action.yml`)：支持在 PR 代码行直接输出 Workflow Commands 行内注释（`::warning` / `::error`）。
  - Pre-commit 提交前拦截钩子（`.pre-commit-hooks.yaml`）。
  - Stanford DSPy 提示词优化评估脚本（`scripts/dspy_optimizer.py`）。
  - DPO / SimPO 偏好对齐语料库导出器（`scripts/export_dpo_pairs.py`），生成 HuggingFace TRL、ChatML 与 ShareGPT 三元组。
- **全平台多智能体适配**：
  - 全面适配 **Codex**, **Claude Code**, **DeepSeek**, **OpenCode**, **WorkBuddy**, **Cursor**, **Windsurf**, **Cline**, **Aider**, **Antigravity**, **Harness²**, **ZCode**。

---

## 4. 安装与部署

### 3.1 智能体规则与技能安装

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

# 安装到通用项目目录：
./install.sh --target generic --dest /path/to/project --lang zh
```

详细接入文档请参阅 [智能体适配器与集成指南](docs/adapters/README.zh-CN.md)。

---

### 3.2 独立 Python 质检工具（`anti-ai-lint`）

在本地或虚拟环境中安装：

```bash
pip install ./lint
```

亦可免安装直接运行：

```bash
python3 -m anti_ai_lint /path/to/document.md --max-score 8.0
```

---

### 3.3 Model Context Protocol (MCP) 服务配置

在 Cursor、Windsurf、Claude Code 或 Zed 中接入 MCP 服务：

```bash
# 直接以 stdio 方式启动：
python3 -m anti_ai_lint.mcp_server

# 或使用安装好的可执行命令：
anti-ai-mcp
```

在项目 `.cursor/mcp.json` 或 Cline 设置中添加：

```json
{
  "mcpServers": {
    "anti-ai-copywriting": {
      "command": "python3",
      "args": ["-m", "anti_ai_lint.mcp_server"]
    }
  }
}
```

---

### 3.4 GitHub Action 与 Pre-commit 门禁

**GitHub Actions 流水线配置 (`.github/workflows/prose-lint.yml`)**：

```yaml
name: Natural Prose Linter
on: [push, pull_request]

jobs:
  lint-prose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./action.yml
        with:
          paths: 'docs/'
          genre: 'academic'
          max-score: '10.0'
```

**Pre-commit 提交前检查 (`.pre-commit-config.yaml`)**：

```yaml
repos:
  - repo: https://github.com/CalebChen941028/anti-ai-copywriting
    rev: v0.4.0
    hooks:
      - id: anti-ai-lint
        args: ["--format", "hook", "--genre", "general"]
```

---

## 5. 检查模式与输出格式

```bash
# 默认检查单个文件
anti-ai-lint paper.md

# 学术场景模式（适合论文、基金申报与预提交）
anti-ai-lint paper.md --genre academic --format hook --max-score 8.0

# 受控白话层质检
anti-ai-lint guide.md --genre plain --format agent

# GitHub Action 模式（输出 PR 行内报错与警告标记）
anti-ai-lint docs/ --format github
```

### 输出格式说明（`--format`）

- `text`：终端可读摘要，标明行列位置、节奏变异系数（CV）、MATTR 与改写建议。
- `json`：机器可读的结构化 AST 与指标报告。
- `hook`：单行/紧凑摘要，适用于 git pre-commit 与 Harness² 环内拦截。
- `agent`：专为大模型反思循环设计的 `<anti-ai-lint-feedback>` 格式载荷。
- `github`：GitHub Actions Workflow Commands 标记格式（`::warning` 与 `::error`）。

---

## 6. 学术参考文献（APA 规范）

`anti-ai-copywriting` 所采用的指标建模与语法特征分析具有严谨的学术与实证基础：

1. **Kobak, D., González-Márquez, R., Horvát, E. Á., & Schulz, C. (2024)**. Monitoring the footprint of large language models in scientific writing. *Nature/Science Advances* (arXiv:2406.07016).
2. **Meister, C., Leszczynski, M., Aji, A. F., & Cotterell, R. (2021)**. Uniform information density and language generation. In *Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.
3. **Mitchell, E., Yoon, J., Miao, N., Finn, C., & Manning, C. D. (2023)**. DetectGPT: Zero-shot machine-generated text detection using probability curvature. In *International Conference on Learning Representations (ICLR 2023)*.
4. **Hans, A., Schwarzschild, A., Cherepanova, V., Bansal, H., Saha, S., Jain, A., ... & Goldblum, M. (2024)**. Spotting LLMs with Binoculars: Zero-shot detection of machine-generated text. In *International Conference on Learning Representations (ICLR 2024)*.
5. **Li, W., et al. (2024)**. RAID: A shared benchmark for robust evaluation of machine-generated text detectors. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL 2024)*.
6. **朱德熙. (1982)**. *语法讲义*. 商务印书馆.（关于汉语形式动词结构与名物化语法分析）.
7. **ASD-STE100 规范**. 欧洲航空航天与防务工业协会（ASD）. 简化技术英语规范.
8. **Google Research (2024)**. Harness²: Agentic Evaluation, Specification, and Guardrail Protocols.

---

## 7. 卸载与清理

干净卸载已安装的规则与技能，恢复备份，绝不触碰用户个人其他配置：

```bash
# 卸载指定目标
./uninstall.sh --target codex
./uninstall.sh --target cursor --dest /path/to/project

# 卸载所有已注册目标
./uninstall.sh --all
```

---

## 8. 商标与非背书声明

本仓库中提及的所有产品名称、商标、服务标志与机构名称（包括 Anthropic、Claude、Claude Code、OpenAI、ChatGPT、Codex、DeepSeek、Google、Gemini、Antigravity、Cursor、Windsurf、Codeium、Cline、Aider、WorkBuddy 等）均为其各自所有者的财产。在此提及仅用于技术兼容性标识与说明，不代表各所有者对本项目的任何赞助、认可或关联。

---

## 9. 开源许可证

本项目基于 [MIT](LICENSE) 开源许可证发布 © 2026 Liangliang Chen
