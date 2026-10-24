#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Run real end-to-end benchmark evaluation comparing:
1. Solo Model (Bare GLM-5.3 without skills or tools)
2. Model + Skill & Tool Gate (GLM-5.3 + anti-ai-copywriting skill + anti-ai-lint in-loop verification & reflection)
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

_repo_root = Path(__file__).resolve().parent.parent
_lint_dir = _repo_root / "lint"
if str(_lint_dir) not in sys.path:
    sys.path.insert(0, str(_lint_dir))

from anti_ai_lint.detector import analyze_text
from anti_ai_lint.cli import format_agent_report

API_KEY = "97b7eeb0b41c47a190cba6dddc6279f7.5vOnSiWnHRQ55RIn"
BASE_URL = "https://open.bigmodel.cn/api/anthropic/v1/messages"
MODEL = "GLM-5.3"

SYSTEM_RULES_ZH = (_repo_root / "rules" / "AGENTS.snippet.zh.md").read_text(encoding="utf-8")
SYSTEM_RULES_EN = (_repo_root / "rules" / "AGENTS.snippet.en.md").read_text(encoding="utf-8")

BENCHMARK_TASKS: Dict[str, Dict[str, Any]] = {
    "academic": {
        "title": "学术论文摘要与核心对比分析",
        "genre": "academic",
        "lang": "zh",
        "prompt": "请撰写一段关于深度学习在蛋白质结构预测中应用的学术论文摘要与核心对比分析。字数在250-350字左右。",
    },
    "business": {
        "title": "商业管理链路重构备忘录",
        "genre": "general",
        "lang": "zh",
        "prompt": "请起草一份面向管理层的Q3核心订单调度系统重构总结备忘录，汇报高并发下的吞吐改善与降本成果。字数在200-300字左右。",
    },
    "en_academic": {
        "title": "English Academic Paper (Speculative Decoding)",
        "genre": "academic",
        "lang": "en",
        "prompt": "Draft an academic analysis on memory bandwidth overhead and latency trade-offs in speculative decoding for large language models. Length: 150-250 words.",
    },
    "grant": {
        "title": "国家自然科学基金课题申报书技术路线",
        "genre": "academic",
        "lang": "zh",
        "prompt": "请起草一份国家自然科学基金课题申报书中的核心技术路线与关键考核指标，主题为自主智能体系统的安全对齐与防御机制。字数在250-350字左右。",
    },
    "popsci": {
        "title": "前沿科普专栏短文（大模型幻觉原理）",
        "genre": "general",
        "lang": "zh",
        "prompt": "请以资深科技专栏作者的视角，向公众科普大模型幻觉与记忆机制的运作原理。字数在200-300字左右。",
    },
    "social": {
        "title": "数码产品真实实测复盘",
        "genre": "general",
        "lang": "zh",
        "prompt": "请以数码极客视角撰写一篇降噪耳机的真实使用体验评测，总结其日常通勤中的真实降噪表现与优缺点。字数在200-300字左右。",
    },
    "polish": {
        "title": "技术故障通报润色（信息守恒）",
        "genre": "general",
        "lang": "zh",
        "source_file": "tests/workflow_cases/polish/source.md",
        "prompt": "请对以下技术通报进行润色，提升其表达质量：\n\n",
    },
    "translate": {
        "title": "技术文档英译中（信息守恒）",
        "genre": "general",
        "lang": "zh",
        "source_file": "tests/workflow_cases/translate/source.en.md",
        "prompt": "请将以下技术段落翻译为中文：\n\n",
    },
}

def call_glm5(messages: List[Dict[str, str]], system_prompt: Optional[str] = None, max_retries: int = 3) -> str:
    ctx = ssl._create_unverified_context()
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    # GLM-5.3 emits a `thinking` block before the `text` block; short budgets
    # get consumed by reasoning and return no text at all.
    payload: Dict[str, Any] = {
        "model": MODEL,
        "max_tokens": 8000,
        "messages": messages,
    }
    if system_prompt:
        payload["system"] = system_prompt

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                BASE_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text_parts = []
                for b in data.get("content", []):
                    if b.get("type") == "text":
                        text_parts.append(b.get("text", ""))
                text = "\n".join(text_parts).strip()
                if not text:
                    # Empty content bodies must never be scored as a clean pass.
                    raise RuntimeError("empty response content")
                return text
        except urllib.error.HTTPError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"GLM-5.3 API failed after {max_retries} attempts: {e}")
            if e.code == 429:
                # Provider quota windows reset on the scale of minutes to hours.
                time.sleep(60 * (attempt + 1))
            else:
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"GLM-5.3 API failed after {max_retries} attempts: {e}")
            time.sleep(5 * (attempt + 1))
    return ""

def main():
    print("================================================================================")
    print("  Real GLM-5.3 Benchmark: Solo Model vs. Model + Skill & Tool Gate")
    print("================================================================================")
    out_dir = _repo_root / "tests" / "fixtures_glm5"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}

    for sc_key, meta in BENCHMARK_TASKS.items():
        print(f"\n---> [Scenario: {sc_key}] {meta['title']}")
        sc_out_dir = out_dir / sc_key
        sc_out_dir.mkdir(parents=True, exist_ok=True)
        
        user_prompt = meta["prompt"]
        source_text = ""
        if "source_file" in meta:
            source_p = _repo_root / meta["source_file"]
            source_text = source_p.read_text(encoding="utf-8").strip()
            user_prompt = user_prompt + source_text

        # =========================================================================
        # 1. Condition A: 单一模型（Solo Model / Bare GLM-5.3）
        # =========================================================================
        print("  [1/2] Invoking Solo Model (GLM-5.3 raw, zero rules/tools)...")
        solo_messages = [{"role": "user", "content": user_prompt}]
        solo_text = call_glm5(solo_messages, system_prompt=None)
        (sc_out_dir / "solo_before.md").write_text(solo_text, encoding="utf-8")
        
        genre = meta["genre"]
        rep_solo = analyze_text(solo_text, genre=genre, source_text=source_text if source_text else None)

        # =========================================================================
        # 2. Condition B: 模型 + 技能工具（GLM-5.3 + Anti-AI Skill + Tool Guardrail）
        # =========================================================================
        print("  [2/2] Invoking Model + Skill (Prior Conditioned)...")
        sys_rules = SYSTEM_RULES_EN if meta["lang"] == "en" else SYSTEM_RULES_ZH
        skill_messages = [{"role": "user", "content": user_prompt}]
        skill_text = call_glm5(skill_messages, system_prompt=sys_rules)
        
        # In-loop Tool Verification Gate (Harness c8 / Reflector loop)
        rep_skill = analyze_text(skill_text, genre=genre, source_text=source_text if source_text else None)
        in_loop_remediated = False
        
        if not rep_skill.passed or rep_skill.score > 0.0:
            print(f"        -> Tool Gate triggered (Score: {rep_skill.score:.1f}, {len(rep_skill.violations)} violations). In-loop reflection active...")
            tool_feedback = format_agent_report([rep_skill], max_score=8.0)
            skill_messages.append({"role": "assistant", "content": skill_text})
            skill_messages.append({
                "role": "user",
                "content": (
                    f"【anti-ai-lint 质检门禁反馈】\n{tool_feedback}\n\n"
                    "请根据上述门禁诊断与修复建议，对草稿进行精准修复：彻底拔除被拦截的套话/黑话/多重定语，"
                    "确保事实与数字严格守恒，恢复母语呼吸感。请直接输出修复后的正文："
                )
            })
            remediated_text = call_glm5(skill_messages, system_prompt=sys_rules)
            rep_skill = analyze_text(remediated_text, genre=genre, source_text=source_text if source_text else None)
            skill_text = remediated_text
            in_loop_remediated = True

        (sc_out_dir / "skill_tool_after.md").write_text(skill_text, encoding="utf-8")
        
        sc_res = {
            "title": meta["title"],
            "genre": genre,
            "lang": meta["lang"],
            "prompt": user_prompt,
            "solo_model": {
                "score": rep_solo.score,
                "normalized_score": rep_solo.normalized_score,
                "passed": rep_solo.passed,
                "violations_count": len(rep_solo.violations),
                "violations": [{"cat": v.category, "msg": v.message} for v in rep_solo.violations],
                "burstiness_cv": rep_solo.metrics.burstiness_cv,
                "mattr": rep_solo.metrics.mattr,
                "de_ratio": rep_solo.metrics.de_ratio,
                "word_count": rep_solo.metrics.total_words,
            },
            "model_plus_skill_tool": {
                "score": rep_skill.score,
                "normalized_score": rep_skill.normalized_score,
                "passed": rep_skill.passed,
                "violations_count": len(rep_skill.violations),
                "violations": [{"cat": v.category, "msg": v.message} for v in rep_skill.violations],
                "burstiness_cv": rep_skill.metrics.burstiness_cv,
                "mattr": rep_skill.metrics.mattr,
                "de_ratio": rep_skill.metrics.de_ratio,
                "word_count": rep_skill.metrics.total_words,
                "in_loop_remediation": in_loop_remediated,
            }
        }
        results[sc_key] = sc_res
        
        print(f"     [Solo Model]        Score: {rep_solo.score:.1f} | Violations: {len(rep_solo.violations)} | De: {rep_solo.metrics.de_ratio*100:.1f}% | Gate: {'PASS' if rep_solo.passed else 'FAIL'}")
        print(f"     [Model+Skill+Tool]  Score: {rep_skill.score:.1f} | Violations: {len(rep_skill.violations)} | De: {rep_skill.metrics.de_ratio*100:.1f}% | Gate: {'PASS' if rep_skill.passed else 'FAIL'}")
        time.sleep(5)

    results_file = out_dir / "benchmark_results.json"
    results_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n================================================================================")
    print(f"Benchmark finished successfully! Saved to: {results_file}")
    print(f"================================================================================")

if __name__ == "__main__":
    main()
