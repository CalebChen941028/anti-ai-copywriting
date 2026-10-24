# GLM-5.3 真实端到端偏好对齐数据集

[English](README.md) | [简体中文](README.zh-CN.md)

本目录包含直接提取自 **GLM-5.3 双盲基准评测**（`tests/fixtures_glm5/`）的真实大模型偏好对齐数据对，专为直接偏好优化（DPO）、SimPO 及大模型消除 AI 腔调、翻译腔与事实杜撰的微调训练而设计。

---

## 1. 格式列表

| 文件名 | 格式规范 | 框架兼容性 |
| :--- | :--- | :--- |
| `glm5_dpo.jsonl` | 标准 DPO 三元组 (`prompt`, `chosen`, `rejected`, `score`) | HuggingFace TRL `DPOTrainer`、Axolotl、LLaMA-Factory |
| `glm5_dpo_chatml.jsonl` | 对话式 ChatML 格式 | OpenAI Fine-Tuning、vLLM、FastChat |
| `glm5_dpo_sharegpt.jsonl` | 多轮 ShareGPT JSON 格式 | DeepSpeed、Axolotl ShareGPT 加载器 |

---

## 2. 数据源与测试规程

- **评测时间**：2026-10-24
- **基底大模型**：智谱 GLM-5.3
- **双盲对照规程**：
  - `rejected`（未选用）：来自单一 GLM-5.3 在无系统提示词、无工具门禁干预下的原生输出。
  - `chosen`（选用）：来自 GLM-5.3 在加载 `anti-ai-copywriting` 技能规则引导并经 `anti-ai-lint` 确定性门禁质检（含环内反思自愈）后的合格输出。
- **覆盖领域**：涵盖学术论文、商业管理备忘、国家科研基金申报、科普专栏、社交数码实测、以及遵循信息守恒的技术润色与英译中等 8 大核心科目。

---

## 3. 开源许可证

本项目基于 [MIT 开源许可证](../LICENSE) 发布 © 2026 Liangliang Chen。
