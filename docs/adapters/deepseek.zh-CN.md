# DeepSeek 适配器指南

[English](deepseek.md) | [简体中文](deepseek.zh-CN.md)

## 概述

本指南介绍如何在 DeepSeek 系列模型（DeepSeek-V3、DeepSeek-R1）、DeepSeek CLI、通用编程智能体（通过 API 接入 DeepSeek 的 Cursor、Cline、Aider）及自定义大模型流水线中集成 `anti-ai-copywriting`。

---

## 1. 自动安装

使用统一安装脚本指定 `deepseek` 目标平台：

```bash
# 全局用户级安装
./install.sh --target deepseek --lang zh

# 指定工作区项目安装
./install.sh --target deepseek --dest /path/to/project --lang zh
```

安装流程自动完成：
1. 复制技能规范 `SKILL.md` 到 `~/.deepseek/skills/anti-ai-copywriting/SKILL.md`（或工作区目录）。
2. 在 `~/.deepseek/AGENTS.md`（或工作区 `AGENTS.md`）中注入包含显式 `<auto_trigger>` 触发标记的限定规则块。
3. 在 `~/.local/share/anti-ai-copywriting/install-manifest.json` 中登记安装路径，供后续卸载时精准清理。

---

## 2. 在通用智能体中配置 DeepSeek 模型

若在开发工具中通过 OpenAI 兼容接口（`https://api.deepseek.com`）调用 DeepSeek 模型：

### Aider 搭配 DeepSeek

启动 Aider 时指定 DeepSeek 模型并读取反 AI 规则规范：

```bash
# 配置 DeepSeek 密钥
export DEEPSEEK_API_KEY="your-api-key"

# 启动 Aider 并载入规则
aider --model deepseek/deepseek-chat --read rules/AGENTS.snippet.zh.md
```

### Cursor 或 Cline 配置 DeepSeek

1. 在 Cursor 或 Cline 设置界面中将模型提供商切为 DeepSeek（`deepseek-chat` 或 `deepseek-reasoner`）。
2. 将规则安装至项目根目录：
   ```bash
   ./install.sh --target cursor --dest . --lang zh
   ```
3. 智能体将在每次提示交互中自动读取 `.cursorrules` 或 `.clinerules` 中的规则要求。

---

## 3. 自定义 DeepSeek API 与工作流集成

在 Python、TypeScript 或 Go 后端服务中直接调用 DeepSeek API 时，将规则片段作为系统提示注入：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 读取中文规则片段
with open("rules/AGENTS.snippet.zh.md", "r", encoding="utf-8") as f:
    system_rules = f.read()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_rules},
        {"role": "user", "content": "请起草系统性能评测报告的方法学与实验设计部分。"}
    ],
    temperature=0.3,
)

print(response.choices[0].message.content)
```

---

## 4. 环内反思与质检门禁

DeepSeek 推理模型（`deepseek-reasoner`）在获得结构化反馈后具备强大的自我纠偏能力。可构建如下确定性校验循环：

```bash
# 使用 agent 格式对生成结果运行门禁
python3 -m anti_ai_lint generated_report.md --genre academic --format agent --max-score 8.0
```

一旦检查工具发现违规，将输出的标准 `<anti-ai-lint-feedback>` 标记块直接送回 DeepSeek 上下文驱动重写：

```markdown
<anti-ai-lint-feedback>
在 generated_report.md 中检测到违规：
  - 第 14 行：禁用套话“底层逻辑” (+3.0) -> 改写建议：直接阐述核心机制或计算原理
  - 第 28 行：公式化煽情“不仅是...更是...” (+5.0) -> 改写建议：分句客观陈述实证结果
请在保留所有实验数据的前提下重写该段落。
</anti-ai-lint-feedback>
```

---

## 5. 安全卸载

如需移除 DeepSeek 相关配置并还原文件：

```bash
./uninstall.sh --target deepseek
```

---

## 商标与非关联声明

DeepSeek 是杭州深度求索人工智能基础技术研究有限公司的商标。`anti-ai-copywriting` 是独立的开源项目，与杭州深度求索人工智能基础技术研究有限公司无任何关联、赞助或背书关系。
