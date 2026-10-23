# anti-ai-copywriting（反 AI 腔文案引擎）

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**中英双语自然语态与学术专业文案引擎（面向 AI 编程智能体与大模型工作流）。**

系统性消除大模型输出中的恶性欧化、翻译腔、伪学术黑话、公式化煽情排比与防御性免责，恢复母语呼吸感与笃定专业质感。

---

## 核心特性

- **场景锚定与基调重塑**：学术论文、课题申报书、专业科普、深度专栏、社媒种草、商务沟通。
- **全域封锁 AI 腔词汇**：彻底封锁“赋能、抓手、闭环、底层逻辑、颗粒度、多维度、全方位、不仅是……更是……”以及英文“delve into, tapestry of, testament to, realm, navigating the complexities”。
- **受控白话层**：面向分析脚本注释与通俗导读的可度量硬规则（短句字数上限、单句单概念、主动语态、名词串控制）。
- **学术呈现规范**：三线表、标准图题、APA/JARS 规范统计量与结构式摘要。
- **零依赖确定性检查工具（`anti-ai-lint`）**：纯 Python 标准库实现，零第三方依赖，可直接作为 CI 关卡或智能体攻坚任务的 `verifyCommand`。

---

## 安装说明

### 1. 智能体技能与规则安装

使用统一安装脚本：

```bash
# 安装到 ZCode：
./install.sh --target zcode --lang zh

# 安装到 Claude Code CLI：
./install.sh --target claude --lang zh

# 安装到 Codex / OpenCode：
./install.sh --target codex
./install.sh --target opencode

# 安装到通用环境（Cursor, Windsurf, WorkBuddy, Cline）：
./install.sh --target generic --dest /path/to/project
```

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

## 检查工具使用示例

```bash
# 检查单个 Markdown 文件
anti-ai-lint paper.md

# 递归检查目录，超分退出非零，输出 JSON 结构
anti-ai-lint docs/ --max-score 6.0 --format json

# 从标准输入读取流式检查
cat draft.txt | anti-ai-lint --max-score 5.0
```

当违规累计扣分超过 `--max-score` 时，`anti-ai-lint` 以退出码 `1` 退出，非常适合作为自动测试关卡。

---

## 回归测试集

运行内置的 6 大场景回归测试集（学术论文、课题申报、专业科普、社交媒体、商务沟通、英文学术）：

```bash
python3 -m unittest discover -s tests
```

---

## 引用与致谢

- 受控白话层在设计思路上借鉴了 ASD-STE100 简化技术英文的受控语言通用原则（该规范版权归 ASD 所有，本项目全部规则均为自主编写）。

---

## 免责声明

本项目为独立开源作品，与 Google LLC 或 Anthropic 无任何关联，亦未获得其官方背书。

---

## 开源许可证

[MIT](LICENSE) © 2026 Liangliang Chen
