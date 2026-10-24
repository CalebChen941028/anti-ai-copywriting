# GLM-5.3 Anti-AI Preference Alignment Dataset

[English](README.md) | [简体中文](README.zh-CN.md)

This directory contains real empirical preference pairs extracted from the **GLM-5.3 dual-blind benchmark** (`tests/fixtures_glm5/`), designed for direct preference optimization (DPO), SimPO, and fine-tuning LLMs to eliminate AI tropes, translationese, and factual hallucinations.

---

## 1. Available Formats

| File | Target Format | Framework Compatibility |
| :--- | :--- | :--- |
| `glm5_dpo.jsonl` | Standard DPO Triplet (`prompt`, `chosen`, `rejected`, `score`) | HuggingFace TRL `DPOTrainer`, Axolotl, LLaMA-Factory |
| `glm5_dpo_chatml.jsonl` | Conversational ChatML Pair | OpenAI Fine-Tuning, vLLM, FastChat |
| `glm5_dpo_sharegpt.jsonl` | Multi-Turn ShareGPT JSON | DeepSpeed, Axolotl ShareGPT loader |

---

## 2. Dataset Provenance

- **Evaluation Date**: 2026-10-24
- **Model**: Zhipu GLM-5.3
- **Dual-Blind Protocol**:
  - `rejected`: Output from solo GLM-5.3 with zero system prompt and no tool verification.
  - `chosen`: Output from GLM-5.3 with `anti-ai-copywriting` prior skill rules, verified and remediated via `anti-ai-lint` deterministic in-loop gate.
- **Coverage**: 8 subjects across academic writing, business strategy, technical grant proposals, popular science, gadget reviews, and information-conserving translation and polishing.

---

## 3. License

Released under the project's [MIT License](../LICENSE) © 2026 Liangliang Chen.
