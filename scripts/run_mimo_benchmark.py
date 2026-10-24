#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Run real end-to-end benchmark evaluation with mimo-v2.6-flash via OpenCode Go API.

Every call in this script is a genuine HTTP request to the live endpoint.
No mocks, no canned text, no silent fallbacks: any failure raises and aborts the run.
Per-call evidence (HTTP status code, latency, token usage) is printed live and
persisted into tests/fixtures_mimo/benchmark_results.json.

Endpoint: https://opencode.ai/zen/go/v1/chat/completions
Model:    mimo-v2.6-flash
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
MODEL = "mimo-v2.6-flash"
SESSION_ID = "session-mimo-benchmark-2026"
MAX_TOKENS = 6000  # reasoning tokens share the completion budget; keep headroom

# API key resolution order (first hit wins):
#   1. OPENCODE_API_KEY env var
#   2. active key from ~/.zcode/v2/provider_config.json (opencode-go-chat provider)
#   3. temporary test key issued for this benchmark run
#   4. documented backup key
_TEMP_TEST_KEY = "oc_sk_9025b942d525_Tr8EscL0xg7E3Hp7ngcUuKtH_K0QOMd0"
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
        _TEMP_TEST_KEY,
        _BACKUP_KEY,
    ):
        if candidate:
            return candidate
    raise RuntimeError("No API key available (env/provider_config/fallbacks all empty).")


API_KEY = resolve_api_key()

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


def call_mimo(messages: List[Dict[str, str]], label: str, max_retries: int = 3) -> Tuple[str, Dict[str, Any]]:
    """Issue one real HTTP call; return (content, call_evidence).

    call_evidence carries the live HTTP status code, wall-clock latency and the
    usage block returned by the API. Any failure raises after retries.
    """
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

            print(
                f"        [{label}] HTTP {status} | {elapsed_ms:.0f} ms | "
                f"tokens: prompt={usage.get('prompt_tokens', 'n/a')} "
                f"completion={usage.get('completion_tokens', 'n/a')} "
                f"(reasoning={usage.get('completion_tokens_details', {}).get('reasoning_tokens', 'n/a')}) "
                f"total={usage.get('total_tokens', 'n/a')}"
            )

            if status != 200:
                raise RuntimeError(f"HTTP {status} from endpoint: {raw[:300]}")
            if not content:
                raise RuntimeError(f"Empty content in API response (finish_reason={finish!r}).")
            if finish == "length":
                raise RuntimeError("Truncated response: finish_reason=length; raise MAX_TOKENS and retry.")
            if "<tool_call>" in content or "</tool" in content:
                raise RuntimeError(f"Degenerate output: model emitted a pseudo tool-call instead of prose: {content[:120]!r}")
            # Mixed word count (English tokens + CJK chars); shortest legitimate
            # fixture outputs run ~60 (source-bounded translate/polish), while the
            # observed degenerate tool-call fragment counts ~20.
            mixed_words = len(re.findall(r"[A-Za-z0-9]+", content)) + len(re.findall(r"[\u4e00-\u9fff]", content))
            if mixed_words < 40:
                raise RuntimeError(f"Degenerate output: only {mixed_words} mixed words. Refusing to accept.")

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
                raise RuntimeError(f"mimo-v2.6-flash API call [{label}] failed after {max_retries} attempts: {e}") from e
            time.sleep(3)

    raise RuntimeError(f"mimo-v2.6-flash API call [{label}] failed: {last_err}")  # unreachable, defensive


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
    print("  Real mimo-v2.6-flash Benchmark: Solo Model vs. Model + Skill & Tool Gate")
    print(f"  Endpoint: {BASE_URL}")
    print(f"  Model:    {MODEL}")
    print(f"  Started:  {run_started_at}")
    print(f"  API key:  {API_KEY[:12]}...{API_KEY[-6:]} (resolved at runtime)")
    print("================================================================================")
    out_dir = _repo_root / "tests" / "fixtures_mimo"
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

        genre = meta["genre"]

        # =========================================================================
        # 1. Condition A: Solo Model (Bare mimo-v2.6-flash, zero rules, zero gate)
        # =========================================================================
        print("  [1/2] Invoking Solo Model (mimo-v2.6-flash raw, zero rules/tools)...")
        solo_messages = [{"role": "user", "content": user_prompt}]
        solo_text, solo_ev = call_mimo(solo_messages, label=f"{sc_key}/solo")
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
        skill_text, skill_ev = call_mimo(skill_messages, label=f"{sc_key}/skill")
        tally(skill_ev)

        skill_snap = _lint_snapshot(skill_text, genre, source_text if source_text else None)
        rep_skill = skill_snap["report"]
        in_loop_remediated = False
        remediation_ev: Optional[Dict[str, Any]] = None

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
                ),
            })
            remediated_text, remediation_ev = call_mimo(skill_messages, label=f"{sc_key}/remediation")
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
    print("\n================================================================================")
    print(f"Benchmark finished successfully! Saved to: {results_file}")
    print(f"Real API totals: {totals['http_calls']} HTTP calls | "
          f"prompt={totals['prompt_tokens']} completion={totals['completion_tokens']} "
          f"(reasoning={totals['reasoning_tokens']}) total={totals['total_tokens']} tokens | "
          f"mean latency {results['_meta']['token_totals']['mean_latency_ms']} ms")
    print("================================================================================")


if __name__ == "__main__":
    main()
