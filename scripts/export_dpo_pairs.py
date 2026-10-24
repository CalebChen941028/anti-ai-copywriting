#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""DPO (Direct Preference Optimization) preference dataset exporter.

Extracts pairwise (prompt, chosen, rejected) training pairs from curated fixtures
and drafts, validated against deterministic anti-ai-lint gates.

Formats supported:
- 'dpo': Standard HuggingFace TRL DPOTrainer triplet (prompt, chosen, rejected)
- 'chatml': Conversational ChatML turn pairs
- 'sharegpt': Multi-turn ShareGPT format
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_repo_root = Path(__file__).resolve().parent.parent
_lint_dir = _repo_root / "lint"
if str(_lint_dir) not in sys.path:
    sys.path.insert(0, str(_lint_dir))

from anti_ai_lint.detector import analyze_text

PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "academic": {
        "genre": "academic",
        "lang": "zh",
        "prompt": "请撰写一段关于深度学习在生物大分子（如蛋白质）结构预测中应用的学术论文摘要与核心对比分析。要求：客观笃定，严禁防御性免责与空洞套话，严谨报告实证数据与置信区间。",
    },
    "en_academic": {
        "genre": "academic",
        "lang": "en",
        "prompt": "Draft an academic analysis on memory bandwidth overhead and latency in speculative decoding for large language models. Requirements: rigorous empirical reporting, confident de-hedged voice, zero AI buzzwords (e.g. no 'delve', 'tapestry', 'testament').",
    },
    "business": {
        "genre": "general",
        "lang": "zh",
        "prompt": "起草一份面向技术管理层的服务拆分与链路重构备忘录。要求：第一句直入事实与指标，拔除互联网黑话与弱动词义肢，清晰陈述降本增效成果与落地路径。",
    },
    "grant": {
        "genre": "academic",
        "lang": "zh",
        "prompt": "起草一份国家自然科学基金课题申报书的核心研究内容与技术路线。要求：条目动词直接切入，删除「拟通过...从而...进而...」套链，明确可核验量化指标与适用边界。",
    },
    "popsci": {
        "genre": "general",
        "lang": "zh",
        "prompt": "以资深科学专栏作者的视角，向公众解释大模型幻觉与记忆机制的运作原理。要求：生活具象动作比喻，平视交流，有温度、克制，无假大空升华总结。",
    },
    "social": {
        "genre": "general",
        "lang": "zh",
        "prompt": "以真实实测复盘视角撰写一篇降噪耳机使用评测。要求：从具体翻车痛点切入，详实提供分贝与体感参数，严禁官方说明书式空洞修饰。",
    },
}


def load_fixture_pairs(fixtures_dir: Path) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    
    # Try loading metadata from benchmark_results.json if present
    bench_json = fixtures_dir / "benchmark_results.json"
    bench_data: Dict[str, Any] = {}
    if bench_json.exists():
        try:
            bench_data = json.loads(bench_json.read_text(encoding="utf-8"))
        except Exception:
            pass

    for sc_dir in sorted(fixtures_dir.iterdir()):
        if not sc_dir.is_dir():
            continue
        sc_name = sc_dir.name
        before_files = sorted(list(sc_dir.glob("*.before.md")) + list(sc_dir.glob("*before*.md")))
        after_files = sorted(list(sc_dir.glob("*.after.md")) + list(sc_dir.glob("*after*.md")))
        # Deduplicate
        before_files = sorted(list(set(before_files)))
        after_files = sorted(list(set(after_files)))
        if not before_files or not after_files:
            continue

        meta_from_bench = bench_data.get(sc_name, {})
        default_meta = PROMPT_TEMPLATES.get(sc_name, {
            "genre": "general",
            "lang": "zh" if sc_name != "en_academic" else "en",
            "prompt": f"Write natural, professional prose for scenario: {sc_name}.",
        })

        genre = meta_from_bench.get("genre", default_meta.get("genre", "general"))
        lang = meta_from_bench.get("lang", default_meta.get("lang", "zh"))
        prompt = meta_from_bench.get("prompt", default_meta.get("prompt", ""))

        for b_file, a_file in zip(before_files, after_files):
            rejected_text = b_file.read_text(encoding="utf-8").strip()
            chosen_text = a_file.read_text(encoding="utf-8").strip()
            pairs.append({
                "scenario": sc_name,
                "genre": genre,
                "lang": lang,
                "prompt": prompt,
                "rejected": rejected_text,
                "chosen": chosen_text,
                "rejected_file": str(b_file.resolve().relative_to(_repo_root)),
                "chosen_file": str(a_file.resolve().relative_to(_repo_root)),
            })
    return pairs


def validate_pairs(pairs: List[Dict[str, Any]], verbose: bool = False, min_rejected_score: float = 10.0) -> bool:
    all_valid = True
    for item in pairs:
        genre = item.get("genre", "general")
        rep_rejected = analyze_text(item["rejected"], genre=genre, max_score=10.0)
        rep_chosen = analyze_text(item["chosen"], genre=genre, max_score=10.0)

        item["rejected_score"] = rep_rejected.score
        item["chosen_score"] = rep_chosen.score
        item["score_margin"] = round(rep_rejected.score - rep_chosen.score, 2)

        # Rejected should fail or have high penalty; chosen should pass
        if rep_rejected.score < min_rejected_score:
            sys.stderr.write(f"Warning: Rejected draft for {item['scenario']} has low penalty score: {rep_rejected.score}\n")
            all_valid = False
        if not rep_chosen.passed or rep_chosen.score > 5.0:
            sys.stderr.write(f"Error: Chosen draft for {item['scenario']} failed gate with score: {rep_chosen.score}\n")
            all_valid = False

        if verbose:
            print(f"[{item['scenario']}] Margin: +{item['score_margin']} (Rejected: {rep_rejected.score:.1f} -> Chosen: {rep_chosen.score:.1f})")
    return all_valid


def export_dpo(
    pairs: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    fmt: str = "dpo",
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    for item in pairs:
        system_prompt = (
            "You are a professional natural language copywriter adhering strictly to "
            "anti-ai copywriting axioms: eliminate AI clichés, light verbs, translationese, "
            "and formulaic emotional parallelism while preserving empirical accuracy and cadence."
        )

        if fmt == "dpo":
            rec = {
                "scenario": item["scenario"],
                "genre": item["genre"],
                "prompt": item["prompt"],
                "chosen": item["chosen"],
                "rejected": item["rejected"],
                "rejected_score": item.get("rejected_score", 0.0),
                "chosen_score": item.get("chosen_score", 0.0),
            }
        elif fmt == "chatml":
            rec = {
                "scenario": item["scenario"],
                "system": system_prompt,
                "prompt": item["prompt"],
                "chosen": [
                    {"role": "user", "content": item["prompt"]},
                    {"role": "assistant", "content": item["chosen"]},
                ],
                "rejected": [
                    {"role": "user", "content": item["prompt"]},
                    {"role": "assistant", "content": item["rejected"]},
                ],
            }
        elif fmt == "sharegpt":
            rec = {
                "scenario": item["scenario"],
                "conversations_chosen": [
                    {"from": "system", "value": system_prompt},
                    {"from": "human", "value": item["prompt"]},
                    {"from": "gpt", "value": item["chosen"]},
                ],
                "conversations_rejected": [
                    {"from": "system", "value": system_prompt},
                    {"from": "human", "value": item["prompt"]},
                    {"from": "gpt", "value": item["rejected"]},
                ],
            }
        else:
            raise ValueError(f"Unknown format: {fmt}")
        records.append(rec)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Exported {len(records)} preference pairs to {output_path}")

    return records


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Export validated DPO preference pairs for de-AI fine-tuning.")
    parser.add_argument("--fixtures-dir", type=str, default=str(_repo_root / "tests" / "fixtures_glm5"), help="Path to fixtures directory.")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output JSONL filepath.")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Export all three formats (dpo, chatml, sharegpt) as <stem>_dpo*.jsonl into this directory.")
    parser.add_argument("--format", choices=["dpo", "chatml", "sharegpt"], default="dpo", help="Target preference format.")
    parser.add_argument("--validate", "--verify", dest="validate", action="store_true", help="Validate score margin between rejected and chosen.")
    parser.add_argument("--min-rejected-score", type=float, default=0.0, help="Minimum penalty score for rejected draft during validation.")

    args = parser.parse_args(argv)

    pairs = load_fixture_pairs(Path(args.fixtures_dir))
    if not pairs:
        sys.stderr.write("No before/after fixture pairs found.\n")
        return 1

    valid = validate_pairs(pairs, verbose=True, min_rejected_score=args.min_rejected_score)
    if not valid:
        sys.stderr.write("Validation failed on one or more fixture pairs.\n")
        return 1

    if args.output_dir:
        out_dir = Path(args.output_dir)
        stem = out_dir.name.rstrip("/")
        for fmt in ("dpo", "chatml", "sharegpt"):
            suffix = "" if fmt == "dpo" else f"_{fmt}"
            export_dpo(pairs, output_path=str(out_dir / f"{stem}{suffix}.jsonl"), fmt=fmt)
        print(f"All three formats exported to {out_dir}/")
        return 0

    if args.validate and not args.output:
        print(f"All {len(pairs)} preference pairs validated successfully.")
        return 0

    records = export_dpo(pairs, output_path=args.output, fmt=args.format)
    if not args.output:
        for r in records:
            print(json.dumps(r, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
