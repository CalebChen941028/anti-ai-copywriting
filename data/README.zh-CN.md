# 真实端到端偏好对齐数据集（mimo-v2.6-flash）

[English](README.md) | [简体中文](README.zh-CN.md)

本目录包含直接提取自 **mimo-v2.6-flash 真实端到端双盲基准评测**（`tests/fixtures_mimo/`）的真实大模型偏好对齐数据对，专为直接偏好优化（DPO）、SimPO 及大模型消除 AI 腔调、翻译腔与事实杜撰的微调训练而设计。所有数据均来自 100% 真实网络请求（OpenCode Go 网关，HTTP 200，全量存证），不包含任何人工构造或模拟推理假数据。

---

## 1. 格式列表（位于 `mimo_dpo/`）

| 文件名 | 格式规范 | 框架兼容性 |
| :--- | :--- | :--- |
| `mimo_dpo/mimo_dpo.jsonl` | 标准 DPO 三元组 (`prompt`, `chosen`, `rejected`, `score`) | HuggingFace TRL `DPOTrainer`、Axolotl、LLaMA-Factory |
| `mimo_dpo/mimo_dpo_chatml.jsonl` | 对话式 ChatML 格式 | OpenAI Fine-Tuning、vLLM、FastChat |
| `mimo_dpo/mimo_dpo_sharegpt.jsonl` | 多轮 ShareGPT JSON 格式 | DeepSpeed、Axolotl ShareGPT 加载器 |

---

## 2. 数据源与测试规程

- **评测时间**：2026-10-24
- **基底大模型**：`mimo-v2.6-flash`（OpenCode Go 网关端点：`https://opencode.ai/zen/go/v1/chat/completions`）
- **真实存证保障**：共 24 次实时 HTTP POST 请求（全部返回 200，平均耗时 14,391 ms，累计消耗 27,976 tokens），每条记录均绑定服务端唯一 `response_id`。
- **双盲对照规程**：
  - `rejected`（未选用）：来自单一模型在无系统提示词、无工具门禁干预下的原生输出。
  - `chosen`（选用）：来自模型在加载 `anti-ai-copywriting` 技能规则引导并经 `anti-ai-lint` 确定性门禁质检（含环内反思自愈）后的合格输出。
- **覆盖领域**：涵盖学术论文、商业管理备忘、国家科研基金申报、科普专栏、社交数码实测、以及遵循信息守恒的技术润色与英译中等 8 大核心科目。
- **真实反例如实保留**：`polish` / `translate` 等场景中若自愈未大幅超越原生，如实记录其分数差，不进行人工粉饰。

---

## 3. 开源许可证

本项目基于 [MIT 开源许可证](../LICENSE) 发布 © 2026 Liangliang Chen。
