#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Run advanced high-difficulty stress test benchmark with deepseek-v4.1-flash via OpenCode Go API.

Every call in this script is a genuine HTTP request to the live OpenCode Go endpoint.
No mocks, no synthetic fallbacks: any network or API failure raises and aborts the run.
Per-call evidence (HTTP status code, latency, token usage, response id) is printed live and
persisted into tests/fixtures_advanced/benchmark_results.json and BENCHMARK_REPORT.md.

Endpoint: https://opencode.ai/zen/go/v1/chat/completions
Model:    deepseek-v4.1-flash
"""

from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_repo_root = Path(__file__).resolve().parent.parent
_lint_dir = _repo_root / "lint"
if str(_lint_dir) not in sys.path:
    sys.path.insert(0, str(_lint_dir))

from anti_ai_lint.detector import analyze_text
from anti_ai_lint.cli import format_agent_report

BASE_URL = "https://opencode.ai/zen/go/v1/chat/completions"
MODEL = "deepseek-v4.1-flash"
SESSION_ID = "session-deepseek-advanced-benchmark-2026"
MAX_TOKENS = 6000

# API key resolution order:
#   1. OPENCODE_API_KEY env var
#   2. active key from ~/.zcode/v2/provider_config.json
#   3. project verified backup key
_BACKUP_KEY = "oc_sk_d3a33de6e5fb_i9tvgs5NmBboxDvT6pQ_9mQDBl_Icnnb"


def _key_from_provider_config() -> Optional[str]:
    cfg_path = Path.home() / ".zcode" / "v2" / "provider_config.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        for rule in cfg.get("config", {}).get("providerRules", []):
            if rule.get("providerId") == "opencode-go-chat":
                key = rule.get("config", {}).get("access", {}).get("apiKey")
                if key:
                    return key
    except Exception:
        return None
    return None


def resolve_api_key() -> str:
    for candidate in (
        os.environ.get("OPENCODE_API_KEY"),
        _key_from_provider_config(),
        _BACKUP_KEY,
    ):
        if candidate:
            return candidate
    raise RuntimeError("No API key available (env/provider_config/fallbacks all empty).")


API_KEY = resolve_api_key()

SYSTEM_RULES_ZH = (_repo_root / "rules" / "AGENTS.snippet.zh.md").read_text(encoding="utf-8")
SYSTEM_RULES_EN = (_repo_root / "rules" / "AGENTS.snippet.en.md").read_text(encoding="utf-8")

ADVANCED_TASKS: Dict[str, Dict[str, Any]] = {
    "long_architecture": {
        "title": "长文跨段落架构方案（挑战长文本风格漂移与段落节奏呆滞）",
        "genre": "general",
        "lang": "zh",
        "prompt": (
            "请撰写一份面向技术委员会的《核心交易集群跨机房双活与高可用架构演进方案》，"
            "字数要求在1000至1500字左右。内容需涵盖：现有单机房痛点剖析、双活网络拓扑与专线延时容忍设计、"
            "分布式事务与多活数据强一致同步机制、以及机房级容灾逃生演练策略。"
        ),
    },
    "financial_unit_fidelity": {
        "title": "精密数字与量纲跨单位转换（挑战严格事实守恒与反虚构捏造）",
        "genre": "general",
        "lang": "zh",
        "source_text": (
            "本次核心清算系统数据库去O与微服务改造历时9个月，涉及核心系统12个微服务模块。"
            "实测数据库峰值查询时延由850ms降低至180ms，P99长尾时延由2.4s收敛至420ms。"
            "通过冷热数据分层归档与NVMe存储池化，年化硬件采购与维保预算节约3000万元。"
            "集群每秒峰值吞吐量由1.2万笔提升至4.8万笔，机房级故障自动切换恢复时间由15分钟缩减至30秒以内。"
        ),
        "prompt": (
            "请对以下金融清算系统改造成效通报进行专业技术润色与重构，提升面向高管的技术穿透力。"
            "必须严格基于给出的事实与数据，允许对度量衡与量纲进行合理等价转换（如毫秒与秒、万元与千万元转换），"
            "但严禁虚构任何未在原文中出现的衍生数据、增幅百分比或无端细节：\n\n"
        ),
    },
    "adversarial_cliche": {
        "title": "对抗性黑话套话清洗（挑战大厂空洞动词与过度抽象堆叠）",
        "genre": "general",
        "lang": "zh",
        "source_text": (
            "我们要以此为重要抓手，全面赋能业务生态闭环，打通上下游全链路的最后一公里。"
            "通过深度下沉与多维联动，构建全方位、多层次的战略协同矩阵，以底层逻辑为依托，"
            "拉通各方资源，形成组合拳打法，全面助推核心业务实现跨越式高质量发展，助力企业降本增效。"
        ),
        "prompt": (
            "请将以下充满大厂空洞黑话与套话的文字重构为干练、务实、直击要害的工作汇报。"
            "彻底剔除一切空洞动词、抽象套话与行业黑话，用具体、可落地的工程与业务表述陈述推进路径：\n\n"
        ),
    },
    "multiturn_remediation": {
        "title": "高难度复杂违规多轮自愈质检（挑战闭环门禁反思修复）",
        "genre": "academic",
        "lang": "zh",
        "prompt": (
            "请全面宏观地论述AI大模型在下一代多模态医学影像诊断中的深远战略意义、颠覆性突破与广阔应用前景，"
            "深入探讨其如何全方位革新传统医疗体系并带来跨越式赋能。字数400字左右。"
        ),
    },
}


def call_deepseek(messages: List[Dict[str, str]], label: str, max_retries: int = 3) -> Tuple[str, Dict[str, Any]]:
    """Issue one genuine HTTP call to deepseek-v4.1-flash; return (content, call_evidence)."""
    ctx = ssl._create_unverified_context()
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)",
        "x-opencode-session": SESSION_ID,
    }
    payload: Dict[str, Any] = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
    }
    last_err: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        started = time.perf_counter()
        try:
            req = urllib.request.Request(
                BASE_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                status = resp.getcode()
                raw = resp.read().decode("utf-8")
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            data = json.loads(raw)
            usage = data.get("usage", {}) or {}
            choices = data.get("choices", [])
            content = (choices[0].get("message", {}).get("content", "") or "").strip() if choices else ""
            finish = choices[0].get("finish_reason", "") if choices else ""

            reasoning = usage.get("completion_tokens_details", {}).get("reasoning_tokens", "n/a")
            print(
                f"        [{label}] HTTP {status} | {elapsed_ms:.0f} ms | "
                f"tokens: prompt={usage.get('prompt_tokens', 'n/a')} "
                f"completion={usage.get('completion_tokens', 'n/a')} "
                f"(reasoning={reasoning}) "
                f"total={usage.get('total_tokens', 'n/a')}"
            )

            if status != 200:
                raise RuntimeError(f"HTTP {status} from endpoint: {raw[:300]}")
            if not content:
                raise RuntimeError(f"Empty content in API response (finish_reason={finish!r}).")
            if finish == "length":
                raise RuntimeError("Truncated response: finish_reason=length; increase MAX_TOKENS.")
            if "<tool_call>" in content or "</tool" in content:
                raise RuntimeError(f"Degenerate output: model emitted a pseudo tool-call fragment: {content[:120]!r}")

            evidence = {
                "http_status": status,
                "latency_ms": round(elapsed_ms, 1),
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "reasoning_tokens": usage.get("completion_tokens_details", {}).get("reasoning_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                },
                "response_id": data.get("id", ""),
            }
            return content, evidence
        except Exception as e:
            last_err = e
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            print(f"        [{label}] attempt {attempt}/{max_retries} FAILED after {elapsed_ms:.0f} ms: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"deepseek-v4.1-flash API call [{label}] failed after {max_retries} attempts: {e}") from e
            time.sleep(3)

    raise RuntimeError(f"deepseek-v4.1-flash API call [{label}] failed: {last_err}")


def _lint_snapshot(text: str, genre: str, source_text: Optional[str]) -> Dict[str, Any]:
    rep = analyze_text(text, genre=genre, source_text=source_text)
    return {
        "report": rep,
        "json": {
            "score": rep.score,
            "normalized_score": rep.normalized_score,
            "passed": rep.passed,
            "violations_count": len(rep.violations),
            "violations": [{"cat": v.category, "msg": v.message} for v in rep.violations],
            "burstiness_cv": rep.metrics.burstiness_cv,
            "mattr": rep.metrics.mattr,
            "de_ratio": rep.metrics.de_ratio,
            "word_count": rep.metrics.total_words,
        },
    }


def main() -> None:
    run_started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    wall_start = time.perf_counter()
    print("================================================================================")
    print("  DeepSeek v4.1-Flash Advanced Benchmark: Solo vs. Model + Skill & Tool Gate")
    print(f"  Endpoint: {BASE_URL}")
    print(f"  Model:    {MODEL}")
    print(f"  Started:  {run_started_at}")
    print(f"  API key:  {API_KEY[:12]}...{API_KEY[-6:]} (runtime resolved)")
    print("================================================================================")

    out_dir = _repo_root / "tests" / "fixtures_advanced"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Any] = {}
    totals = {
        "http_calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "reasoning_tokens": 0,
        "total_tokens": 0,
        "latency_ms_sum": 0.0,
    }

    def tally(ev: Dict[str, Any]) -> None:
        totals["http_calls"] += 1
        u = ev.get("usage", {})
        for k in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens"):
            if isinstance(u.get(k), int):
                totals[k] += u[k]
        totals["latency_ms_sum"] += ev.get("latency_ms", 0.0)

    for sc_key, meta in ADVANCED_TASKS.items():
        print(f"\n---> [Scenario: {sc_key}] {meta['title']}")
        sc_out_dir = out_dir / sc_key
        sc_out_dir.mkdir(parents=True, exist_ok=True)

        user_prompt = meta["prompt"]
        source_text = meta.get("source_text", "").strip()
        if source_text:
            (sc_out_dir / "source.md").write_text(source_text, encoding="utf-8")
            user_prompt = user_prompt + source_text

        genre = meta["genre"]

        # =========================================================================
        # 1. Condition A: Solo Model (Bare deepseek-v4.1-flash, zero rules, zero gate)
        # =========================================================================
        print("  [1/2] Invoking Solo Model (deepseek-v4.1-flash bare, zero rules/tools)...")
        solo_messages = [{"role": "user", "content": user_prompt}]
        solo_text, solo_ev = call_deepseek(solo_messages, label=f"{sc_key}/solo")
        tally(solo_ev)
        (sc_out_dir / "solo_before.md").write_text(solo_text, encoding="utf-8")
        solo_snap = _lint_snapshot(solo_text, genre, source_text if source_text else None)
        rep_solo = solo_snap["report"]

        # =========================================================================
        # 2. Condition B: Model + Skill & Tool Gate (rules in system + in-loop lint remediation)
        # =========================================================================
        print("  [2/2] Invoking Model + Skill (Prior Conditioned)...")
        sys_rules = SYSTEM_RULES_EN if meta["lang"] == "en" else SYSTEM_RULES_ZH
        skill_messages: List[Dict[str, str]] = [
            {"role": "system", "content": sys_rules},
            {"role": "user", "content": user_prompt},
        ]
        skill_text, skill_ev = call_deepseek(skill_messages, label=f"{sc_key}/skill")
        tally(skill_ev)

        skill_snap = _lint_snapshot(skill_text, genre, source_text if source_text else None)
        rep_skill = skill_snap["report"]
        in_loop_remediated = False
        remediation_ev: Optional[Dict[str, Any]] = None

        if not rep_skill.passed or rep_skill.score > 0.0:
            print(f"        -> Tool Gate triggered (Score: {rep_skill.score:.1f}, {len(rep_skill.violations)} violations). In-loop reflection active...")
            (sc_out_dir / "skill_turn1.md").write_text(skill_text, encoding="utf-8")
            tool_feedback = format_agent_report([rep_skill], max_score=8.0)
            skill_messages.append({"role": "assistant", "content": skill_text})
            skill_messages.append({
                "role": "user",
                "content": (
                    f"【anti-ai-lint 质检门禁反馈】\n{tool_feedback}\n\n"
                    "请根据上述门禁诊断与修复建议，对草稿进行精准修复：彻底拔除被拦截的套话/黑话/单调句式，"
                    "若有原文则确保事实与数字严格守恒，恢复母语呼吸感。请直接输出修复后的正文："
                ),
            })
            remediated_text, remediation_ev = call_deepseek(skill_messages, label=f"{sc_key}/remediation")
            tally(remediation_ev)
            skill_snap = _lint_snapshot(remediated_text, genre, source_text if source_text else None)
            rep_skill = skill_snap["report"]
            skill_text = remediated_text
            in_loop_remediated = True

        (sc_out_dir / "skill_tool_after.md").write_text(skill_text, encoding="utf-8")

        results[sc_key] = {
            "title": meta["title"],
            "genre": genre,
            "lang": meta["lang"],
            "prompt": user_prompt,
            "solo_model": {
                **solo_snap["json"],
                "api_evidence": solo_ev,
            },
            "model_plus_skill_tool": {
                **skill_snap["json"],
                "in_loop_remediation": in_loop_remediated,
                "api_evidence": {
                    **skill_ev,
                    "remediation_call": remediation_ev,
                },
            },
        }

        print(f"     [Solo Model]        Score: {rep_solo.score:.1f} | Violations: {len(rep_solo.violations)} | De: {rep_solo.metrics.de_ratio*100:.1f}% | Gate: {'PASS' if rep_solo.passed else 'FAIL'}")
        print(f"     [Model+Skill+Tool]  Score: {rep_skill.score:.1f} | Violations: {len(rep_skill.violations)} | De: {rep_skill.metrics.de_ratio*100:.1f}% | Gate: {'PASS' if rep_skill.passed else 'FAIL'} | Remediated: {in_loop_remediated}")
        time.sleep(1)

    run_finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    results["_meta"] = {
        "endpoint": BASE_URL,
        "model": MODEL,
        "session": SESSION_ID,
        "api_key_fingerprint": f"{API_KEY[:12]}...{API_KEY[-6:]}",
        "started_at_utc": run_started_at,
        "finished_at_utc": run_finished_at,
        "wall_clock_s": round(time.perf_counter() - wall_start, 1),
        "token_totals": {
            "http_calls": totals["http_calls"],
            "prompt_tokens": totals["prompt_tokens"],
            "completion_tokens": totals["completion_tokens"],
            "reasoning_tokens": totals["reasoning_tokens"],
            "total_tokens": totals["total_tokens"],
            "mean_latency_ms": round(totals["latency_ms_sum"] / max(totals["http_calls"], 1), 1),
        },
        "no_mock_guarantee": "All texts generated by live HTTP calls; any failure aborts the run.",
    }

    results_file = out_dir / "benchmark_results.json"
    results_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate Markdown Report
    report_lines = [
        "# DeepSeek v4.1-Flash Advanced Stress Benchmark Report",
        "",
        f"- **Model**: `{MODEL}`",
        f"- **Endpoint**: `{BASE_URL}`",
        f"- **Session**: `{SESSION_ID}`",
        f"- **Executed At**: `{run_started_at}`",
        f"- **Total HTTP Calls**: `{totals['http_calls']}` (100% Real Live Calls, Zero Mocks)",
        f"- **Total Tokens**: `{totals['total_tokens']}` (Prompt: `{totals['prompt_tokens']}`, Completion: `{totals['completion_tokens']}`, Reasoning: `{totals['reasoning_tokens']}`)",
        "",
        "## Summary Results",
        "",
        "| Scenario | Solo Score | Solo Gate | Skill+Tool Score | Skill+Tool Gate | In-Loop Remediated |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for k, v in results.items():
        if k.startswith("_"):
            continue
        s_solo = v["solo_model"]
        s_skill = v["model_plus_skill_tool"]
        report_lines.append(
            f"| **{k}** ({v['title']}) | {s_solo['score']:.1f} | {'✅ PASS' if s_solo['passed'] else '❌ FAIL'} | "
            f"**{s_skill['score']:.1f}** | {'✅ PASS' if s_skill['passed'] else '❌ FAIL'} | {'Yes' if s_skill['in_loop_remediation'] else 'No'} |"
        )

    report_lines.extend([
        "",
        "## Detailed Analysis by Scenario",
        "",
    ])

    for k, v in results.items():
        if k.startswith("_"):
            continue
        s_solo = v["solo_model"]
        s_skill = v["model_plus_skill_tool"]
        report_lines.extend([
            f"### {k}: {v['title']}",
            "",
            f"- **Solo Model Score**: `{s_solo['score']:.1f}` (Violations: {len(s_solo['violations'])}, '的' Ratio: {s_solo['de_ratio']*100:.1f}%)",
            f"- **Model + Skill & Tool Gate Score**: `{s_skill['score']:.1f}` (Violations: {len(s_skill['violations'])}, '的' Ratio: {s_skill['de_ratio']*100:.1f}%)",
            f"- **In-Loop Remediation Triggered**: `{s_skill['in_loop_remediation']}`",
            "",
            "#### Solo Model Violations",
        ])
        if s_solo["violations"]:
            for viol in s_solo["violations"]:
                report_lines.append(f"- `[{viol['cat']}]` {viol['msg']}")
        else:
            report_lines.append("- None (Clean)")

        report_lines.extend([
            "",
            "#### Skill + Tool Gate Violations",
        ])
        if s_skill["violations"]:
            for viol in s_skill["violations"]:
                report_lines.append(f"- `[{viol['cat']}]` {viol['msg']}")
        else:
            report_lines.append("- **None (100% Gate Clearance)**")
        report_lines.append("")

    report_file = out_dir / "BENCHMARK_REPORT.md"
    report_file.write_text("\n".join(report_lines), encoding="utf-8")

    print("\n================================================================================")
    print(f"Benchmark finished successfully!")
    print(f"JSON Output:   {results_file}")
    print(f"Report Output: {report_file}")
    print(f"Real API totals: {totals['http_calls']} HTTP calls | {totals['total_tokens']} tokens")
    print("================================================================================")


if __name__ == "__main__":
    main()
